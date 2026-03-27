from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import date, datetime, timedelta
from extensions import db
# FIXED IMPORTS: Absolute paths
from models.models import Appointment, Treatment, DoctorAvailabilityDay, DoctorSlot, PatientProfile, User, DoctorProfile
from utils.auth_decorators import role_required

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