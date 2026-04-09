from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from datetime import date, datetime, timedelta
from werkzeug.utils import secure_filename
from extensions import db
# FIXED IMPORTS: Absolute paths
from models.models import Appointment, Treatment, DoctorAvailabilityDay, DoctorSlot, PatientProfile, User, DoctorProfile, Specialization, Review
from utils.auth_decorators import role_required
import os
from sqlalchemy import func

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

bp = Blueprint('doctor', __name__)

@bp.route('/schedule', methods=['GET'])
@role_required(['Doctor'])
def get_schedule():
    current_user_id = get_jwt_identity()
    today = date.today()
    
    # Fetch appointments (joined with Patient to get names)
    appointments = db.session.query(Appointment, PatientProfile).join(PatientProfile).filter(
        Appointment.doctor_id == current_user_id,
        Appointment.date >= today
    ).order_by(Appointment.date, Appointment.time).all()

    result = []
    for appt, patient in appointments:
        result.append({
            'id': appt.id,
            'date': str(appt.date),
            'time': str(appt.time),
            'status': appt.status,
            'patient_id': patient.user_id,
            'patient_name': patient.full_name
        })
    
    return jsonify(result), 200

@bp.route('/appointment/<int:id>/status', methods=['PUT'])
@role_required(['Doctor'])
def update_status(id):
    data = request.get_json()
    status = data.get('status') # 'Completed' or 'Cancelled'
    current_user_id = get_jwt_identity()
    
    appt = Appointment.query.get_or_404(id)
    # Security check
    if str(appt.doctor_id) != str(current_user_id):
         return jsonify(msg="Unauthorized access to this appointment"), 403

    # Prevent invalid transitions
    if appt.status == 'Completed' and status == 'Booked':
        return jsonify(msg="Cannot revert a completed appointment to Booked"), 400

    appt.status = status

    # If doctor cancels, free up the doctor's slot so patients can rebook
    if status == 'Cancelled':
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
    return jsonify(msg="Status updated"), 200

@bp.route('/treatment', methods=['POST'])
@role_required(['Doctor'])
def add_treatment():
    data = request.get_json()
    appt_id = data.get('appointment_id')
    current_user_id = get_jwt_identity()

    # Verify appointment
    appt = Appointment.query.get(appt_id)
    if not appt or str(appt.doctor_id) != str(current_user_id):
        return jsonify(msg="Invalid appointment or unauthorized"), 400

    treatment = Treatment(
        appointment_id=appt_id,
        diagnosis=data.get('diagnosis'),
        prescription=data.get('prescription'),
        notes=data.get('notes')
    )
    
    # Ensure status is completed
    appt.status = 'Completed'
    
    db.session.add(treatment)
    db.session.commit()
    return jsonify(msg="Treatment record saved"), 201

@bp.route('/patients', methods=['GET'])
@role_required(['Doctor'])
def get_my_patients():
    current_user_id = get_jwt_identity()
    
    patients = db.session.query(PatientProfile).join(Appointment).filter(
        Appointment.doctor_id == current_user_id
    ).distinct().all()
    
    result = [{'id': p.user_id, 'name': p.full_name} for p in patients]
    return jsonify(result), 200

@bp.route('/profile', methods=['GET'])
@role_required(['Doctor'])
def get_profile():
    doctor_id = get_jwt_identity()
    doctor = DoctorProfile.query.get_or_404(doctor_id)
    return jsonify({
        'full_name': doctor.full_name,
        'specialization': doctor.specialization.name if doctor.specialization else '',
        'contact_info': doctor.contact_info,
        'experience_years': doctor.experience_years,
        'bio': doctor.bio,
        'photo_url': doctor.photo_url or ''
    }), 200

@bp.route('/profile', methods=['PUT'])
@role_required(['Doctor'])
def update_profile():
    doctor_id = get_jwt_identity()
    doctor = DoctorProfile.query.get_or_404(doctor_id)

    full_name = request.form.get('full_name')
    specialization_name = request.form.get('specialization')
    contact_info = request.form.get('contact_info')
    experience_years = request.form.get('experience_years')
    bio = request.form.get('bio')

    if full_name:
        doctor.full_name = full_name
    if contact_info is not None:
        doctor.contact_info = contact_info
    if experience_years is not None and experience_years != '':
        try:
            doctor.experience_years = int(experience_years)
        except ValueError:
            pass
    if bio is not None:
        doctor.bio = bio

    if specialization_name:
        specialization = Specialization.query.filter_by(name=specialization_name).first()
        if not specialization:
            specialization = Specialization(name=specialization_name)
            db.session.add(specialization)
            db.session.flush()
        doctor.specialization = specialization

    if 'photo' in request.files:
        photo = request.files['photo']
        if photo and allowed_file(photo.filename):
            filename = f"doctor_{doctor_id}_{secure_filename(photo.filename)}"
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            photo.save(save_path)
            doctor.photo_url = f"/static/uploads/{filename}"

    db.session.commit()
    return jsonify(msg='Profile updated successfully', photo_url=doctor.photo_url), 200

@bp.route('/availability', methods=['GET'])
@role_required(['Doctor'])
def get_availability():
    doctor_id = get_jwt_identity()
    today = date.today()
    
    # Get availability for today onwards
    avail_days = DoctorAvailabilityDay.query.filter(
        DoctorAvailabilityDay.doctor_id == doctor_id,
        DoctorAvailabilityDay.date >= today
    ).order_by(DoctorAvailabilityDay.date).all()
    
    result = []
    for day in avail_days:
        slots = [str(slot.time) for slot in day.slots]
        result.append({
            'date': str(day.date),
            'slots': slots
        })
        
    return jsonify(result), 200

@bp.route('/availability', methods=['POST'])
@role_required(['Doctor'])
def set_availability():
    data = request.get_json()
    doctor_id = get_jwt_identity()
    
    # Expects data format: [{"date": "2025-12-01", "slots": ["09:00", "10:00"]}, ...]
    
    for item in data:
        try:
            date_obj = datetime.strptime(item['date'], '%Y-%m-%d').date()
            
            # Find or create the day
            day_avail = DoctorAvailabilityDay.query.filter_by(doctor_id=doctor_id, date=date_obj).first()
            if not day_avail:
                day_avail = DoctorAvailabilityDay(doctor_id=doctor_id, date=date_obj)
                db.session.add(day_avail)
                db.session.flush() # Flush to get ID
            
            # Clear existing slots for this day (simple replacement strategy)
            DoctorSlot.query.filter_by(availability_day_id=day_avail.id).delete()
            
            # Add new slots
            for time_str in item.get('slots', []):
                # time_str expected as "HH:MM" or "HH:MM:SS"
                try:
                    time_obj = datetime.strptime(time_str, '%H:%M').time()
                except ValueError:
                    time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
                slot = DoctorSlot(availability_day_id=day_avail.id, time=time_obj)
                db.session.add(slot)
                
        except ValueError as e:
            return jsonify(msg=f"Invalid date or time format: {str(e)}"), 400

    db.session.commit()
    return jsonify(msg="Availability updated successfully"), 200

@bp.route('/availability/<date_str>', methods=['DELETE'])
@role_required(['Doctor'])
def delete_availability(date_str):
    doctor_id = get_jwt_identity()
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(msg="Invalid date format"), 400
    
    # Find the availability day
    day_avail = DoctorAvailabilityDay.query.filter_by(doctor_id=doctor_id, date=date_obj).first()
    if not day_avail:
        return jsonify(msg="No availability found for this date"), 404
    
    # Check if any slots are booked
    booked_slots = DoctorSlot.query.filter_by(availability_day_id=day_avail.id, is_booked=True).count()
    if booked_slots > 0:
        return jsonify(msg="Cannot delete availability with booked appointments"), 400
    
    # Delete the day (cascade will delete slots)
    db.session.delete(day_avail)
    db.session.commit()
    
    return jsonify(msg="Availability deleted successfully"), 200

@bp.route('/patient/<int:patient_id>/history', methods=['GET'])
@role_required(['Doctor'])
def get_patient_history(patient_id):
    patient = PatientProfile.query.filter_by(user_id=patient_id).first()
    if not patient:
        return jsonify(msg="Patient not found"), 404

    appointments = db.session.query(Appointment, DoctorProfile, Treatment).join(
        DoctorProfile, Appointment.doctor_id == DoctorProfile.user_id
    ).outerjoin(
        Treatment, Appointment.id == Treatment.appointment_id
    ).filter(
        Appointment.patient_id == patient_id,
        Appointment.status == 'Completed'
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    result = []
    for appt, doc, treatment in appointments:
        item = {
            'id': appt.id,
            'date': str(appt.date),
            'doctor_name': doc.full_name,
            'specialization': doc.specialization.name if doc.specialization else 'N/A',
            'diagnosis': treatment.diagnosis if treatment else None,
            'prescription': treatment.prescription if treatment else None,
            'notes': treatment.notes if treatment else None
        }
        result.append(item)
        
    return jsonify(result), 200

@bp.route('/statistics', methods=['GET'])
@role_required(['Doctor'])
def get_statistics():
    doctor_id = get_jwt_identity()
    
    # Total appointments
    total_appointments = Appointment.query.filter_by(doctor_id=doctor_id).count()
    
    # Completed appointments
    completed_appointments = Appointment.query.filter_by(doctor_id=doctor_id, status='Completed').count()
    
    # Upcoming appointments
    today = date.today()
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date >= today,
        Appointment.status == 'Booked'
    ).count()
    
    # Unique patients
    unique_patients = db.session.query(func.count(func.distinct(Appointment.patient_id))).filter_by(doctor_id=doctor_id).scalar()
    
    # Average rating
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(doctor_id=doctor_id).scalar()
    
    # Review count
    review_count = Review.query.filter_by(doctor_id=doctor_id).count()
    
    return jsonify({
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'upcoming_appointments': upcoming_appointments,
        'unique_patients': unique_patients,
        'average_rating': round(avg_rating, 1) if avg_rating else None,
        'review_count': review_count
    }), 200

@bp.route('/reviews', methods=['GET'])
@role_required(['Doctor'])
def get_my_reviews():
    doctor_id = get_jwt_identity()
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