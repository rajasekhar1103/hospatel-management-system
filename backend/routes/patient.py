from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, time, timedelta, date
from extensions import db, celery 
# FIXED IMPORTS: Absolute paths
from models.models import DoctorProfile, Specialization, Appointment, Treatment, DoctorAvailabilityDay, DoctorSlot, PatientProfile, User, Review
from utils.auth_decorators import role_required
from jobs.tasks import export_treatment_history
import csv
from io import StringIO
from sqlalchemy import func

bp = Blueprint('patient', __name__)

@bp.route('/specializations', methods=['GET'])
def get_specializations():
    specs = Specialization.query.all()
    result = [{'id': s.id, 'name': s.name} for s in specs]
    return jsonify(result), 200

@bp.route('/doctors', methods=['GET'])
@role_required(['Patient'])
def get_doctors():
    spec_id = request.args.get('spec_id', type=int)
    date_str = request.args.get('date') # YYYY-MM-DD
    
    if not date_str:
        return jsonify(msg="Date parameter is required"), 400

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(msg="Invalid date format"), 400

    query = DoctorProfile.query
    if spec_id:
        query = query.filter_by(specialization_id=spec_id)
        
    doctors = query.all()
    
    result = []
    
    for doc in doctors:
        # Find availability for this day
        day_avail = DoctorAvailabilityDay.query.filter_by(doctor_id=doc.user_id, date=date_obj).first()
        
        if not day_avail:
            continue
            
        # Get unbooked slots
        available_slots = DoctorSlot.query.filter_by(
            availability_day_id=day_avail.id,
            is_booked=False
        ).all()
        
        if not available_slots:
            continue
            
        # Calculate average rating for this doctor
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(doctor_id=doc.user_id).scalar()
        review_count = db.session.query(func.count(Review.id)).filter_by(doctor_id=doc.user_id).scalar()
        
        result.append({
            'id': doc.user_id,
            'name': doc.full_name,
            'specialization': doc.specialization.name if doc.specialization else 'General',
            'slots': [slot.time.strftime('%H:%M') for slot in available_slots],
            'rating': round(avg_rating, 1) if avg_rating else None,
            'review_count': review_count or 0
        })
        
    return jsonify(result), 200

@bp.route('/book', methods=['POST'])
@role_required(['Patient'])
def book_appointment():
    data = request.get_json()
    patient_id = get_jwt_identity()
    
    try:
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        time_obj = datetime.strptime(data['time'], '%H:%M').time()
        doctor_id = data['doctor_id']
        
        # 1. Find the availability day
        day_avail = DoctorAvailabilityDay.query.filter_by(
            doctor_id=doctor_id, 
            date=date_obj
        ).first()
        
        if not day_avail:
            return jsonify(msg="Doctor is not available on this date."), 409
        
        # 2. Find the specific slot
        slot = DoctorSlot.query.filter_by(
            availability_day_id=day_avail.id,
            time=time_obj
        ).first()
        
        if not slot:
             return jsonify(msg="This time slot is not available."), 409
             
        if slot.is_booked:
            return jsonify(msg="Slot already booked."), 409

        # 3. Enforce patient-level spacing: ensure this patient has no other
        # booked appointment within 15 minutes on the same date (any doctor).
        spacing_minutes = 15
        requested_dt = datetime.combine(date_obj, time_obj)

        patient_appts = Appointment.query.filter_by(
            patient_id=patient_id,
            date=date_obj,
            status='Booked'
        ).all()

        for ap in patient_appts:
            existing_dt = datetime.combine(ap.date, ap.time)
            delta = abs((existing_dt - requested_dt).total_seconds())
            if delta < spacing_minutes * 60:
                return jsonify(msg=f"You have another appointment within {spacing_minutes} minutes."), 409

        # 4. Check for existing appointment for this doctor/time (handle cancelled re-use)
        existing_appt = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=date_obj,
            time=time_obj
        ).first()

        if existing_appt:
            if existing_appt.status == 'Cancelled':
                # Reactivate the appointment
                existing_appt.status = 'Booked'
                existing_appt.patient_id = patient_id
            else:
                return jsonify(msg="Slot already booked."), 409
        else:
            # Create new Appointment
            new_appt = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                date=date_obj,
                time=time_obj,
                status='Booked'
            )
            db.session.add(new_appt)
        
        # 4. Mark slot as booked
        slot.is_booked = True
        
        db.session.commit()
        return jsonify(msg="Appointment booked successfully"), 201
        
    except ValueError:
         return jsonify(msg="Invalid date or time format."), 400
    except Exception as e:
        return jsonify(msg=f"Booking failed: {str(e)}"), 500

@bp.route('/appointment', methods=['POST'])
@role_required(['Patient'])
def book_appointment_alias():
    # Alias for /book endpoint (frontend compatibility)
    return book_appointment()

@bp.route('/history', methods=['GET'])
@role_required(['Patient'])
def get_patient_history():
    patient_id = get_jwt_identity()
    
    # Fetch appointments with treatments
    appointments = db.session.query(Appointment, DoctorProfile, Treatment).join(
        DoctorProfile, Appointment.doctor_id == DoctorProfile.user_id
    ).outerjoin(
        Treatment, Appointment.id == Treatment.appointment_id
    ).filter(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    result = []
    for appt, doc, treatment in appointments:
        item = {
            'id': appt.id,
            'date': str(appt.date),
            'time': str(appt.time),
            'doctor_name': doc.full_name,
            'specialization': doc.specialization.name if doc.specialization else 'N/A',
            'status': appt.status,
            'diagnosis': treatment.diagnosis if treatment else None,
            'prescription': treatment.prescription if treatment else None,
            'notes': treatment.notes if treatment else None
        }
        result.append(item)
        
    return jsonify(result), 200

@bp.route('/appointments', methods=['GET'])
@role_required(['Patient'])
def get_my_appointments():
    # Reusing the history logic for now as it returns all appointments
    return get_patient_history()

@bp.route('/export_csv', methods=['POST'])
@role_required(['Patient'])
def trigger_export():
    patient_id = get_jwt_identity()
    
    # 1. Fetch data
    records = db.session.query(
        User.username, 
        Appointment.date,
        DoctorProfile.full_name.label('doctor_name'),
        Treatment.diagnosis, 
        Treatment.prescription
    ).join(PatientProfile, User.id == PatientProfile.user_id
    ).join(Appointment, PatientProfile.user_id == Appointment.patient_id
    ).join(Treatment, Appointment.id == Treatment.appointment_id
    ).join(DoctorProfile, Appointment.doctor_id == DoctorProfile.user_id
    ).filter(User.id == patient_id).all()
    
    # 2. Generate CSV
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['User ID', 'Username', 'Consulting Doctor', 'Appointment Date', 'Diagnosis', 'Prescription'])

    for record in records:
        cw.writerow([
            patient_id, 
            record.username, 
            record.doctor_name, 
            record.date, 
            record.diagnosis, 
            record.prescription
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=treatment_history.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@bp.route('/appointment/<int:id>/cancel', methods=['PUT'])
@role_required(['Patient'])
def cancel_appointment(id):
    patient_id = get_jwt_identity()
    appt = Appointment.query.get_or_404(id)
    
    if str(appt.patient_id) != str(patient_id):
        return jsonify(msg="Unauthorized"), 403
        
    if appt.status != 'Booked':
        return jsonify(msg="Cannot cancel completed or already cancelled appointments"), 400
        
    # 1. Update Appointment Status
    appt.status = 'Cancelled'
    
    # 2. Free up the Doctor Slot
    # Find the slot for this doctor, date, and time
    day_avail = DoctorAvailabilityDay.query.filter_by(
        doctor_id=appt.doctor_id, 
        date=appt.date
    ).first()
    
    if day_avail:
        slot = DoctorSlot.query.filter_by(
            availability_day_id=day_avail.id,
            time=appt.time
        ).first()
        if slot:
            slot.is_booked = False
            
    db.session.commit()
    return jsonify(msg="Appointment cancelled successfully"), 200

# --- Review Endpoints ---
@bp.route('/doctor/<int:doctor_id>/reviews', methods=['GET'])
def get_doctor_reviews(doctor_id):
    """Get all reviews for a specific doctor"""
    reviews = Review.query.filter_by(doctor_id=doctor_id).order_by(Review.created_at.desc()).all()
    
    result = []
    for review in reviews:
        result.append({
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'patient_name': review.patient.full_name,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result), 200

@bp.route('/doctor/<int:doctor_id>/rating', methods=['GET'])
def get_doctor_rating(doctor_id):
    """Get average rating and review count for a doctor"""
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(doctor_id=doctor_id).scalar()
    review_count = db.session.query(func.count(Review.id)).filter_by(doctor_id=doctor_id).scalar()
    
    return jsonify({
        'doctor_id': doctor_id,
        'average_rating': round(avg_rating, 1) if avg_rating else None,
        'review_count': review_count or 0,
        'total_stars': 5
    }), 200

@bp.route('/review', methods=['POST'])
@role_required(['Patient'])
def submit_review():
    """Submit or update a review for a doctor (patient must have had an appointment with them)"""
    patient_id = get_jwt_identity()
    data = request.get_json()
    
    doctor_id = data.get('doctor_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    # Validate rating
    if not rating or rating < 1 or rating > 5:
        return jsonify(msg="Rating must be between 1 and 5"), 400
    
    if not doctor_id:
        return jsonify(msg="Doctor ID is required"), 400
    
    # Check if patient has completed appointment with this doctor
    completed_appt = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor_id,
        status='Completed'
    ).first()
    
    if not completed_appt:
        return jsonify(msg="You can only review doctors you have completed appointments with"), 400
    
    # Check if review already exists
    existing_review = Review.query.filter_by(
        doctor_id=doctor_id,
        patient_id=patient_id
    ).first()
    
    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.comment = comment
        existing_review.created_at = datetime.utcnow()
        db.session.commit()
        return jsonify(msg="Review updated successfully", review_id=existing_review.id), 200
    else:
        # Create new review
        review = Review(
            doctor_id=doctor_id,
            patient_id=patient_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        return jsonify(msg="Review submitted successfully", review_id=review.id), 201

@bp.route('/my-reviews', methods=['GET'])
@role_required(['Patient'])
def get_my_reviews():
    """Get reviews submitted by the current patient"""
    patient_id = get_jwt_identity()
    reviews = Review.query.filter_by(patient_id=patient_id).order_by(Review.created_at.desc()).all()
    
    result = []
    for review in reviews:
        result.append({
            'id': review.id,
            'doctor_id': review.doctor_id,
            'doctor_name': review.doctor.full_name,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result), 200