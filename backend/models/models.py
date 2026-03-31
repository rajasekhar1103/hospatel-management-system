from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- Core User Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Admin', 'Doctor', 'Patient'
    is_active = db.Column(db.Boolean, default=True) # For blacklisting

    # Profile relationship (1-to-1)
    doctor_profile = db.relationship('DoctorProfile', backref='user', uselist=False, lazy=True)
    patient_profile = db.relationship('PatientProfile', backref='user', uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- Specialization/Doctor Models ---
class Specialization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

class DoctorProfile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    specialization_id = db.Column(db.Integer, db.ForeignKey('specialization.id'))
    contact_info = db.Column(db.String(100))
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.String(500)) # FIX: Added 'bio' column
    
    # Relationships
    specialization = db.relationship('Specialization', backref='doctors')
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    reviews = db.relationship('Review', backref='doctor', lazy=True, cascade='all, delete-orphan')

class DoctorAvailabilityDay(db.Model):
    """Stores the day the doctor has opened slots."""
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profile.user_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    # Ensure uniqueness per doctor per day
    __table_args__ = (db.UniqueConstraint('doctor_id', 'date', name='_doctor_date_uc'),)
    
    # Relationship to store the specific slots for this day
    slots = db.relationship('DoctorSlot', backref='day_availability', lazy=True, cascade="all, delete-orphan")


class DoctorSlot(db.Model):
    """Stores the individual time slot stamps that the doctor is available for."""
    id = db.Column(db.Integer, primary_key=True)
    availability_day_id = db.Column(db.Integer, db.ForeignKey('doctor_availability_day.id'), nullable=False)
    time = db.Column(db.Time, nullable=False) # e.g., 09:00:00 or 14:30:00
    is_booked = db.Column(db.Boolean, default=False) # Track if this slot is booked

    __table_args__ = (db.UniqueConstraint('availability_day_id', 'time', name='_day_time_uc'),)

# --- Patient Models ---
class PatientProfile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(100))
    address = db.Column(db.String(200))
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

# --- Appointment and Treatment Models ---
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_profile.user_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profile.user_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Booked') # Booked, Completed, Cancelled
    # Ensure no multiple appointments at the same time for the same doctor
    __table_args__ = (db.UniqueConstraint('doctor_id', 'date', 'time', name='_doctor_time_uc'),)

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, nullable=False)
    diagnosis = db.Column(db.String(500), nullable=False)
    prescription = db.Column(db.String(500), nullable=False)
    notes = db.Column(db.String(500))
    # Relationship
    appointment = db.relationship('Appointment', backref='treatment', uselist=False)

# --- Review Model ---
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_profile.user_id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_profile.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Relationship
    patient = db.relationship('PatientProfile', backref='reviews')
    # Ensure one review per patient per doctor
    __table_args__ = (db.UniqueConstraint('doctor_id', 'patient_id', name='_doctor_patient_review_uc'),)


# --- Initial Admin Creation Function (Called by app.py) ---
def create_initial_admin(db):
    if not User.query.filter_by(role='Admin').first():
        admin = User(
            username='admin',
            role='Admin',
            is_active=True
        )
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()
        print("Initial Admin created.")