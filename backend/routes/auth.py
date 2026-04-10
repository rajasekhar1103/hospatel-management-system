from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta
from extensions import db
# FIXED IMPORT: Absolute path
from models.models import User, PatientProfile
from utils.validators import sanitize_string, validate_json
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__)

def create_auth_token(user):
    """
    Create JWT access token for authenticated user
    
    Args:
        user: User model instance
    
    Returns:
        JWT token string
    """
    # Include role in the claims for RBAC
    identity = str(user.id)
    additional_claims = {'username': user.username, 'role': user.role}
    # Create token with 24-hour expiration
    access_token = create_access_token(
        identity=identity, 
        additional_claims=additional_claims, 
        expires_delta=timedelta(hours=24)
    )
    return access_token

@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token
    
    Expected JSON:
        {
            "username": "user@example.com",
            "password": "password123"
        }
    
    Returns:
        - 200: {access_token, role, user_id}
        - 401: Invalid credentials
        - 400: Missing/invalid input
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(msg="Request body is required"), 400
        
        username = sanitize_string(data.get('username'))
        password = data.get('password')
        
        if not username or not password:
            return jsonify(msg="Username and password are required"), 400

        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {username}")
                return jsonify(msg="Account is blacklisted/inactive"), 403

            token = create_auth_token(user)
            logger.info(f"User {username} logged in successfully")
            return jsonify(access_token=token, role=user.role, user_id=user.id), 200
        
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify(msg="Bad username or password"), 401
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify(msg="Login failed"), 500

@bp.route('/register', methods=['POST'])
def register_patient():
    """
    Register new patient user
    
    Expected JSON:
        {
            "username": "user@example.com",
            "password": "password123",
            "full_name": "John Doe",
            "contact_info": "1234567890",
            "address": "123 Main St"
        }
    
    Returns:
        - 201: Patient registered successfully
        - 400: Username exists or validation failed
        - 500: Database error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(msg="Request body is required"), 400
        
        # Validate required fields
        required_fields = ['username', 'password', 'full_name', 'contact_info']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return jsonify(msg=f"Missing required fields: {', '.join(missing)}"), 400
        
        username = sanitize_string(data.get('username'), max_length=80)
        if not username:
            return jsonify(msg="Invalid username"), 400
        
        if User.query.filter_by(username=username).first():
            logger.warning(f"Registration attempt with existing username: {username}")
            return jsonify(msg="Username already exists"), 400

        # 1. Create User
        user = User(username=username, role='Patient')
        user.set_password(data['password'])
        
        # 2. Create Patient Profile
        patient_profile = PatientProfile(
            user=user,
            full_name=sanitize_string(data['full_name'], max_length=100),
            contact_info=sanitize_string(data['contact_info'], max_length=100),
            address=sanitize_string(data.get('address', ''), max_length=200)
        )
        
        db.session.add(user)
        db.session.add(patient_profile)
        db.session.commit()
        
        logger.info(f"New patient registered: {username}")
        return jsonify(msg="Patient registered successfully"), 201
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify(msg="Registration failed"), 500