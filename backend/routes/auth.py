from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta
from extensions import db
# FIXED IMPORT: Absolute path
from models.models import User, PatientProfile

bp = Blueprint('auth', __name__)

def create_auth_token(user):
    # Include role in the claims for RBAC
    identity = str(user.id)
    additional_claims = {'username': user.username, 'role': user.role}
    # Create token
    access_token = create_access_token(
        identity=identity, 
        additional_claims=additional_claims, 
        expires_delta=timedelta(hours=24)
    )
    return access_token

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        if not user.is_active:
             return jsonify(msg="Account is blacklisted/inactive"), 403

        token = create_auth_token(user)
        return jsonify(access_token=token, role=user.role, user_id=user.id), 200
    
    return jsonify(msg="Bad username or password"), 401

@bp.route('/register', methods=['POST'])
def register_patient():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify(msg="Username already exists"), 400

    # 1. Create User
    user = User(username=data['username'], role='Patient')
    user.set_password(data['password'])
    
    # 2. Create Patient Profile
    patient_profile = PatientProfile(
        user=user,
        full_name=data['full_name'],
        contact_info=data['contact_info'],
        address=data.get('address')
    )
    
    db.session.add(user)
    db.session.add(patient_profile)
    db.session.commit()
    
    return jsonify(msg="Patient registered successfully"), 201