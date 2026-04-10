"""
Database query helpers and optimization utilities
"""
from sqlalchemy import func
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)


def get_doctor_with_availability(doctor_id, date_obj, db):
    """
    Fetch doctor profile with related data using eager loading
    
    Args:
        doctor_id: Doctor user ID
        date_obj: Date to check availability
        db: SQLAlchemy database instance
    
    Returns:
        Doctor object or None
    """
    from models.models import DoctorProfile
    
    return DoctorProfile.query.options(
        joinedload(DoctorProfile.specialization),
        joinedload(DoctorProfile.user)
    ).filter_by(user_id=doctor_id).first()


def get_doctor_rating_stats(doctor_id, db):
    """
    Get rating statistics for a doctor (optimized query)
    
    Args:
        doctor_id: Doctor user ID
        db: SQLAlchemy database instance
    
    Returns:
        Dict with avg_rating and review_count
    """
    from models.models import Review
    
    stats = db.session.query(
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).filter_by(doctor_id=doctor_id).first()
    
    return {
        'avg_rating': round(float(stats.avg_rating), 1) if stats.avg_rating else None,
        'review_count': stats.review_count or 0
    }


def get_doctors_with_ratings(doctor_ids, db):
    """
    Get rating stats for multiple doctors in one query (avoids N+1)
    
    Args:
        doctor_ids: List of doctor user IDs
        db: SQLAlchemy database instance
    
    Returns:
        Dict mapping doctor_id to rating stats
    """
    from models.models import Review
    
    if not doctor_ids:
        return {}
    
    results = db.session.query(
        Review.doctor_id,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).filter(Review.doctor_id.in_(doctor_ids)).group_by(
        Review.doctor_id
    ).all()
    
    stats_map = {}
    for doctor_id, avg_rating, count in results:
        stats_map[doctor_id] = {
            'avg_rating': round(float(avg_rating), 1) if avg_rating else None,
            'review_count': count or 0
        }
    
    # Fill in missing doctors with None ratings
    for doc_id in doctor_ids:
        if doc_id not in stats_map:
            stats_map[doc_id] = {
                'avg_rating': None,
                'review_count': 0
            }
    
    return stats_map


def get_patient_appointments_optimized(patient_id, db, future_only=False):
    """
    Fetch patient appointments with doctor and treatment data using eager loading
    
    Args:
        patient_id: Patient user ID
        db: SQLAlchemy database instance
        future_only: If True, only get future appointments
    
    Returns:
        List of appointments with related data
    """
    from datetime import date
    from models.models import Appointment, DoctorProfile, Treatment
    
    query = db.session.query(Appointment).options(
        joinedload(Appointment.doctor).joinedload(DoctorProfile.specialization),
        joinedload(Appointment.treatment)
    ).filter_by(patient_id=patient_id)
    
    if future_only:
        query = query.filter(Appointment.date >= date.today())
    
    return query.order_by(
        Appointment.date.desc(),
        Appointment.time.desc()
    ).all()


def check_appointment_conflict(patient_id, date_obj, time_obj, exclude_statuses=None, db=None):
    """
    Check if patient has conflicting appointments within spacing window
    
    Args:
        patient_id: Patient user ID
        date_obj: Appointment date
        time_obj: Appointment time
        exclude_statuses: List of statuses to exclude (e.g., ['Cancelled'])
        db: SQLAlchemy database instance
    
    Returns:
        (True, message) if conflict found, (False, None) otherwise
    """
    from datetime import datetime
    from models.models import Appointment
    
    if exclude_statuses is None:
        exclude_statuses = []
    
    spacing_minutes = 15
    requested_dt = datetime.combine(date_obj, time_obj)

    query = Appointment.query.filter_by(patient_id=patient_id, date=date_obj)
    
    if exclude_statuses:
        query = query.filter(~Appointment.status.in_(exclude_statuses))
    
    patient_appts = query.all()

    for appt in patient_appts:
        existing_dt = datetime.combine(appt.date, appt.time)
        delta = abs((existing_dt - requested_dt).total_seconds())
        if delta < spacing_minutes * 60:
            return (True, f"You have another appointment within {spacing_minutes} minutes.")
    
    return (False, None)
