from app import celery, db, redis_client
from datetime import date, timedelta
# Assuming your models are located at: backend/models/models.py
# New line for robust execution:
from models.models import Appointment, Treatment, DoctorProfile, User, PatientProfile
from io import StringIO
import csv

# Scheduled Job - Daily reminders (Celery Beat)
@celery.task
def send_daily_reminders():
    today = date.today()
    # Find all appointments for today that are 'Booked'
    appointments = Appointment.query.filter(
        Appointment.date == today,
        Appointment.status == 'Booked'
    ).all()

    for appt in appointments:
        patient = appt.patient.user # Assuming PatientProfile has contact_info
        # Simulated send operation
        print(f"Reminder sent to {patient.username} via Mail/Chat: Appointment today at {appt.time} with Doctor ID {appt.doctor_id}.")
        # Implementation detail: Use Google Chat Webhooks/Mail library here

# Scheduled Job - Monthly Activity Report (Celery Beat)
@celery.task
def generate_monthly_report():
    first_day_of_month = date.today().replace(day=1)
    last_month_start = (first_day_of_month - timedelta(days=1)).replace(day=1)
    last_month_end = first_day_of_month - timedelta(days=1)
    
    doctors = DoctorProfile.query.all()
    
    for doctor_profile in doctors:
        # Get treatments for this doctor in the last month
        reports_data = db.session.query(
            Appointment, Treatment
        ).join(Treatment, Appointment.id == Treatment.appointment_id
        ).filter(
            Appointment.doctor_id == doctor_profile.user_id,
            Appointment.status == 'Completed',
            Appointment.date.between(last_month_start, last_month_end)
        ).all()
        
        # Build HTML report content (simplified)
        report_html = f"<h2>Monthly Activity Report for Dr. {doctor_profile.full_name}</h2>"
        report_html += f"<p>Total completed appointments: {len(reports_data)}</p>"
        
        # Implementation detail: Render detailed HTML using Jinja2 template
        # Send mail with HTML report to doctor_profile.user.username (if it's an email)
        print(f"Sending monthly report to Dr. {doctor_profile.full_name}. Appointments: {len(reports_data)}")


# User Triggered Async Job - Export as CSV
@celery.task
def export_treatment_history(patient_id):
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
    
    # Write header
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
    
    csv_content = si.getvalue()
    
    # 3. Store/Alert (Simplified: printing and setting a Redis flag)
    # In a real app, this file would be saved to disk and a download link emailed.
    
    # Example of alert/status update:
    redis_key = f"csv_export_status_{patient_id}"
    redis_client.set(redis_key, 'DONE') 
    
    print(f"CSV export for Patient ID {patient_id} finished. Content: \n{csv_content}")

# --- Celery Beat Schedule (Defined in config or separately) ---
# Example for Celery Beat configuration:
# CELERY_BEAT_SCHEDULE = {
#     'daily-reminder': {
#         'task': 'backend.jobs.tasks.send_daily_reminders',
#         'schedule': timedelta(days=1), # e.g., run every day at 8:00 AM
#     },
#     'monthly-report': {
#         'task': 'backend.jobs.tasks.generate_monthly_report',
#         'schedule': crontab(day_of_month='1', hour=9, minute=0), # 1st of every month at 9 AM
#     },
# }