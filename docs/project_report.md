# Project Report: Hospital Management System -(V2)
## Student Details

- Name: Nakka Rajasekhar
- ID: 22f3001169
- Email: 22f3001169@ds.study.iitm.ac.in
- course : Modern Application Development II (MAD II)
---

## Project Details

- Project Title: Hospital Management System (HMS)
- Question statement: Build a compact, role-aware Hospital Management System that supports user registration/login, appointment booking and management, role-based dashboards (admin/doctor/patient), and basic background tasks for reminders/cleanup.

### How I approached the problem

1. Defined core user roles (Patient, Doctor, Admin) and the key use-cases each role must perform.
2. Chose a simple, testable architecture: Flask backend (REST endpoints) and a small Vue SPA front-end powered by Vite.
3. Implemented modular blueprints for `auth`, `doctor`, `patient`, and `admin` to keep responsibilities separated.
4. Built minimal models for `User` and `Appointment`, and used decorators to enforce role-based access in routes.
5. Developed front-end components for login/register, dashboards, and appointment list to demonstrate end-to-end flows.
6. Added a small jobs module for background tasks (reminders/cleanup) to showcase periodic processes.

---

## AI / LLM Declaration

- Approximately 25-30% of the text was drafted with AI assistance for structure and wording. All code and technical decisions were my own work. I reviewed and edited all AI-generated content for accuracy.

---

## Frameworks and Libraries Used

- Backend: `Flask`, `Flask-Login` (or session-based auth), `Werkzeug` (password hashing), `SQLAlchemy` (ORM) — see `backend/requirements.txt` for exact versions.
- Frontend: `Vue.js`, `Vite`, `axios` for HTTP requests.
- Dev / Utilities:  `Celery` or `APScheduler` (optional, for background jobs), `Redis` (optional cache / broker).


---

## Database ER Diagrame
![alt text](<Screenshot 2025-11-29 221921.png>)


## API Resource Endpoints (representative)

- `POST /api/auth/register` — register new user (body: name, email, password, role)
- `POST /api/auth/login` — login (body: email, password) → returns session / token
- `GET /api/patient/appointments` — list appointments for authenticated patient
- `POST /api/patient/appointments` — create appointment request (body: doctor_id, scheduled_at, notes)
- `GET /api/doctor/appointments` — list appointments assigned to authenticated doctor
- `PUT /api/doctor/appointments/<id>` — update appointment status (confirm/complete/cancel)
- `GET /api/admin/users` — (admin) list users
- `DELETE /api/admin/users/<id>` — (admin) delete a user

---

## Presentation Video

- Drive link: [INSERT DRIVE LINK HERE]

---

## Acknowledgements

- Flask and Vue documentation and examples used as references during development.


