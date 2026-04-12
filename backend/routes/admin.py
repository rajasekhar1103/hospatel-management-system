from flask import Blueprint, request, jsonify
from extensions import db
from models.models import User, DoctorProfile, Specialization, Appointment, PatientProfile
from utils.auth_decorators import role_required
from utils.validators import sanitize_string, validate_integer
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__)

@bp.route('/stats', methods=['GET'])
@role_required(['Admin'])
def get_stats():
    """
    Get dashboard statistics for admin
    
    Returns:
        - 200: {total_doctors, total_patients, upcoming_appointments}
    """
    try:
        stats = {
            'total_doctors': DoctorProfile.query.count(),
            'total_patients': PatientProfile.query.count(),
            'upcoming_appointments': Appointment.query.filter_by(status='Booked').count()
        }
        logger.info("Admin stats requested")
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify(msg="Could not fetch statistics"), 500

# --- BLOCK/UNBLOCK (Blacklist) Endpoint: Used for Doctors and Patients ---
@bp.route('/users/<int:user_id>/blacklist', methods=['PUT'])
@role_required(['Admin'])
def blacklist_user(user_id):
    """
    Activate or deactivate user account
    
    Returns:
        - 200: User status updated
        - 400: Cannot blacklist admin
        - 404: User not found
    """
    try:
        user = User.query.get_or_404(user_id)
        if user.role == 'Admin':
            logger.warning(f"Admin attempted to blacklist another admin: user_id={user_id}")
            return jsonify(msg="Cannot blacklist Admin"), 400
        
        # Toggle active status (True -> False, or False -> True)
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "activated" if user.is_active else "blacklisted"
        logger.info(f"User {user.username} {status} by admin")
        return jsonify(msg=f"User {user.username} {status} successfully"), 200
    except Exception as e:
        logger.error(f"Blacklist error: {str(e)}")
        return jsonify(msg="Operation failed"), 500

@bp.route('/search', methods=['GET'])
@role_required(['Admin'])
def search_users():
    """
    Search for users by username or name
    
    Query params:
        query: Search term
    
    Returns:
        - 200: List of matching users
    """
    try:
        query = sanitize_string(request.args.get('query', ''))
        if not query or len(query) < 2:
            return jsonify(msg="Search query must be at least 2 characters"), 400
        
        results = []
        
        # Search Patients
        patients = db.session.query(User, PatientProfile).join(PatientProfile).filter(
            (User.username.ilike(f'%{query}%')) | (PatientProfile.full_name.ilike(f'%{query}%'))
        ).all()
        
        for u, p in patients:
            results.append({
                'id': u.id,
                'username': u.username,
                'full_name': p.full_name,
                'role': 'Patient',
                'is_active': u.is_active,
                'contact_info': p.contact_info
            })

        # Search Doctors
        doctors = db.session.query(User, DoctorProfile).join(DoctorProfile).filter(
            (User.username.ilike(f'%{query}%')) | (DoctorProfile.full_name.ilike(f'%{query}%'))
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

        logger.info(f"User search performed: query='{query}', results={len(results)}")
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify(msg="Search failed"), 500

# --- ADMIN CRUD: ADD/UPDATE DOCTOR PROFILE ---
# Note: Admin CANNOT add other user types (Patients register themselves).

@bp.route('/doctors', methods=['POST'])
@role_required(['Admin'])
def add_doctor():
    """
    Create new doctor account
    
    Expected JSON:
        {
            "username": "doctor@hospital.com",
            "password": "secure_password",
            "full_name": "Dr. John Smith",
            "specialization": "Cardiology",
            "contact_info": "1234567890",
            "bio": "Experienced cardiologist..."
        }
    
    Returns:
        - 201: Doctor created successfully
        - 400: Validation failed or username exists
        - 500: Database error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'password', 'full_name', 'specialization']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return jsonify(msg=f"Missing required fields: {', '.join(missing)}"), 400

        username = sanitize_string(data['username'], max_length=80)
        if not username:
            return jsonify(msg="Invalid username"), 400
        
        if User.query.filter_by(username=username).first():
            logger.warning(f"Attempt to create doctor with existing username: {username}")
            return jsonify(msg="Username already exists"), 400

        user = User(username=username, role='Doctor')
        user.set_password(data['password'])
        
        spec_name = sanitize_string(data.get('specialization'), max_length=50)
        if not spec_name:
            return jsonify(msg="Specialization is required and must be valid"), 400
            
        spec = Specialization.query.filter_by(name=spec_name).first()
        if not spec:
            spec = Specialization(name=spec_name)
            db.session.add(spec)
            db.session.flush()

        doctor_profile = DoctorProfile(
            user=user,
            full_name=sanitize_string(data['full_name'], max_length=100),
            specialization=spec,
            contact_info=sanitize_string(data.get('contact_info', ''), max_length=100),
            bio=sanitize_string(data.get('bio', ''), max_length=500)
        )

        db.session.add_all([user, doctor_profile])
        db.session.commit()
        
        logger.info(f"New doctor created: {username}")
        return jsonify(msg="Doctor created successfully", doctor_id=user.id), 201
    
    except Exception as e:
        logger.error(f"Doctor creation error: {str(e)}")
        db.session.rollback()
        return jsonify(msg="Doctor creation failed"), 500

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

# --- ADMIN: SYSTEM HISTORY/AUDIT LOG ---

@bp.route('/history', methods=['GET'])
@role_required(['Admin'])
def get_system_history():
    """
    Get system activity history for admin monitoring
    
    Query params:
        type: Filter by activity type (user_registration, appointment_booked, etc.)
        date_from: Filter from date (YYYY-MM-DD)
        date_to: Filter to date (YYYY-MM-DD)
    
    Returns:
        - 200: List of system activities
    """
    try:
        activity_type = request.args.get('type', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # For now, we'll simulate history data since we don't have an audit log table
        # In a real application, you'd have an AuditLog model with proper database storage
        history_data = []
        
        # Get recent user registrations
        recent_users = User.query.order_by(User.created_at.desc()).limit(20).all()
        for user in recent_users:
            history_data.append({
                'id': f'user_reg_{user.id}',
                'type': 'user_registration',
                'description': f'New {user.role.lower()} registered: {user.username}',
                'details': f'User ID: {user.id}, Role: {user.role}',
                'timestamp': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(user, 'created_at') and user.created_at else 'Recent'
            })
        
        # Get recent appointments
        recent_appointments = db.session.query(Appointment).order_by(Appointment.created_at.desc()).limit(20).all()
        for appt in recent_appointments:
            doctor = DoctorProfile.query.get(appt.doctor_id)
            patient = PatientProfile.query.get(appt.patient_id)
            
            if appt.status == 'Booked':
                activity_type_entry = 'appointment_booked'
                description = f'Appointment booked: {patient.full_name if patient else "Unknown"} with Dr. {doctor.full_name if doctor else "Unknown"}'
            elif appt.status == 'Completed':
                activity_type_entry = 'appointment_completed'
                description = f'Appointment completed: {patient.full_name if patient else "Unknown"} with Dr. {doctor.full_name if doctor else "Unknown"}'
            else:
                continue
                
            history_data.append({
                'id': f'appt_{appt.id}',
                'type': activity_type_entry,
                'description': description,
                'details': f'Date: {appt.date}, Time: {appt.time}',
                'timestamp': appt.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(appt, 'created_at') and appt.created_at else str(appt.date)
            })
        
        # Get doctor additions (we'll use a simple heuristic since we don't track creation time)
        recent_doctors = db.session.query(User, DoctorProfile).join(DoctorProfile).filter(User.role == 'Doctor').limit(10).all()
        for user, doctor in recent_doctors:
            history_data.append({
                'id': f'doctor_add_{user.id}',
                'type': 'doctor_added',
                'description': f'Doctor added: Dr. {doctor.full_name}',
                'details': f'Specialization: {doctor.specialization.name if doctor.specialization else "N/A"}',
                'timestamp': 'Recent addition'
            })
        
        # Apply filters
        if activity_type:
            history_data = [h for h in history_data if h['type'] == activity_type]
        
        # Sort by timestamp (descending - most recent first)
        history_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit results
        history_data = history_data[:50]
        
        logger.info(f"System history requested: type='{activity_type}', results={len(history_data)}")
        return jsonify(history_data), 200
        
    except Exception as e:
        logger.error(f"History fetch error: {str(e)}")
        return jsonify(msg="Failed to fetch system history"), 500