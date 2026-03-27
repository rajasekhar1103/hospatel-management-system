from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, time, timedelta, date
from extensions import db, celery 
# FIXED IMPORTS: Absolute paths
from models.models import DoctorProfile, Specialization, Appointment, Treatment, DoctorAvailabilityDay, DoctorSlot, PatientProfile, User
from utils.auth_decorators import role_required
from jobs.tasks import export_treatment_history
import csv
from io import StringIO

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
            
        result.append({
            'id': doc.user_id,
            'name': doc.full_name,
            'specialization': doc.specialization.name if doc.specialization else 'General',
            'slots': [slot.time.strftime('%H:%M') for slot in available_slots]
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

        # 3. Check for existing appointment (to handle re-booking after cancellation)
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
                # No need to add to session, it's already attached
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