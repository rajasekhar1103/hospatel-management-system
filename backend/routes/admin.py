from flask import Blueprint, request, jsonify
from extensions import db
from models.models import User, DoctorProfile, Specialization, Appointment, PatientProfile
from utils.auth_decorators import role_required

bp = Blueprint('admin', __name__)

@bp.route('/stats', methods=['GET'])
@role_required(['Admin'])
def get_stats():
    stats = {
        'total_doctors': DoctorProfile.query.count(),
        'total_patients': PatientProfile.query.count(),
        'upcoming_appointments': Appointment.query.filter_by(status='Booked').count()
    }
    return jsonify(stats), 200

# --- BLOCK/UNBLOCK (Blacklist) Endpoint: Used for Doctors and Patients ---
@bp.route('/users/<int:user_id>/blacklist', methods=['PUT'])
@role_required(['Admin'])
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'Admin':
        return jsonify(msg="Cannot blacklist Admin"), 400
    
    # Toggle active status (True -> False, or False -> True)
    user.is_active = not user.is_active
    db.session.commit()
    status = "activated" if user.is_active else "blacklisted"
    return jsonify(msg=f"User {user.username} {status} successfully"), 200

@bp.route('/search', methods=['GET'])
@role_required(['Admin'])
def search_users():
    query = request.args.get('query', '')
    results = []
    
    # Search Patients
    patients = db.session.query(User, PatientProfile).join(PatientProfile).filter(
        (User.username.contains(query)) | (PatientProfile.full_name.contains(query))
    ).all()
    
    for u, p in patients:
        results.append({'id': u.id, 'username': u.username, 'full_name': p.full_name, 'role': 'Patient', 'is_active': u.is_active, 'contact_info': p.contact_info})

    # Search Doctors
    doctors = db.session.query(User, DoctorProfile).join(DoctorProfile).filter(
        (User.username.contains(query)) | (DoctorProfile.full_name.contains(query))
    ).all()

    for u, d in doctors:
        spec_name = d.specialization.name if d.specialization else 'N/A'
        results.append({
            'id': u.id, 
            'username': u.username, 
            'full_name': d.full_name, 
            'role': 'Doctor', 
            'is_active': u.is_active, 
            'specialization': spec_name, 
            'contact_info': d.contact_info, 
            'bio': d.bio
        })

    return jsonify(results), 200

# --- ADMIN CRUD: ADD/UPDATE DOCTOR PROFILE ---
# Note: Admin CANNOT add other user types (Patients register themselves).

@bp.route('/doctors', methods=['POST'])
@role_required(['Admin'])
def add_doctor():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify(msg="Username already exists"), 400

    user = User(username=data['username'], role='Doctor')
    user.set_password(data['password'])
    
    spec_name = data.get('specialization')
    if not spec_name:
        return jsonify(msg="Specialization is required"), 400
        
    spec = Specialization.query.filter_by(name=spec_name).first()
    if not spec:
        spec = Specialization(name=spec_name)
        db.session.add(spec)
        db.session.flush()

    doctor_profile = DoctorProfile(
        user=user,
        full_name=data['full_name'],
        specialization=spec,
        contact_info=data.get('contact_info'),
        bio=data.get('bio')
    )

    db.session.add_all([user, doctor_profile])
    db.session.commit()

    return jsonify(msg="Doctor added successfully"), 201

@bp.route('/doctors/<int:user_id>', methods=['PUT'])
@role_required(['Admin'])
def update_doctor(user_id):
    data = request.get_json()
    # Ensure user is a Doctor
    User.query.filter_by(id=user_id, role='Doctor').first_or_404() 
    doctor_profile = DoctorProfile.query.get_or_404(user_id)
    
    # 1. Update Specialization
    spec_name = data.get('specialization')
    if spec_name:
        spec = Specialization.query.filter_by(name=spec_name).first()
        if not spec:
            spec = Specialization(name=spec_name)
            db.session.add(spec)
            db.session.flush()
        doctor_profile.specialization = spec

    # 2. Update Doctor Profile Fields
    doctor_profile.full_name = data.get('full_name', doctor_profile.full_name)
    doctor_profile.contact_info = data.get('contact_info', doctor_profile.contact_info)
    doctor_profile.bio = data.get('bio', doctor_profile.bio)

    db.session.commit()
    return jsonify(msg="Doctor profile updated successfully"), 200

# --- ADMIN CRUD: EDIT PATIENT INFO ---

@bp.route('/patients/<int:user_id>', methods=['PUT'])
@role_required(['Admin'])
def update_patient(user_id):
    data = request.get_json()
    # Ensure user is a Patient
    User.query.filter_by(id=user_id, role='Patient').first_or_404()
    patient_profile = PatientProfile.query.get_or_404(user_id)
    
    # Update Patient Profile Fields
    patient_profile.full_name = data.get('full_name', patient_profile.full_name)
    patient_profile.contact_info = data.get('contact_info', patient_profile.contact_info)
    patient_profile.address = data.get('address', patient_profile.address)

    db.session.commit()
    return jsonify(msg="Patient profile updated successfully"), 200

# --- ADMIN: VIEW ALL APPOINTMENTS ---

@bp.route('/appointments', methods=['GET'])
@role_required(['Admin'])
def get_all_appointments():
    appointments = db.session.query(
        Appointment, DoctorProfile, PatientProfile
    ).join(DoctorProfile, Appointment.doctor_id == DoctorProfile.user_id
    ).join(PatientProfile, Appointment.patient_id == PatientProfile.user_id
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    result = []
    for appt, doc, patient in appointments:
        result.append({
            'id': appt.id,
            'date': str(appt.date),
            'time': str(appt.time),
            'status': appt.status,
            'patient_name': patient.full_name,
            'doctor_name': doc.full_name,
            'specialization': doc.specialization.name if doc.specialization else 'N/A'
        })
    
    return jsonify(result), 200