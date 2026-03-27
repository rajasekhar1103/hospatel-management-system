# Video Presentation Storyboard: HMS

This document provides a visual storyboard and detailed screen recording cues for each section of the video presentation.

---

## SCENE 1: Introduction (0:00–0:30)

### Visual Setup

- **Background:** Your room or a simple backdrop (avoid clutter)
- **Camera position:** Head and shoulders, well-lit face
- **Attire:** Professional (shirt, blazer) or neat casual
- **Font on screen:** Display project title "Hospital Management System (HMS)" in large, clear text

### On-Screen Elements

Option A: Title slide
- Large text: "Hospital Management System"
- Subtitle: "A Role-Based Appointment Management Platform"
- Your name and date

Option B: Live screen share
- Show a screenshot of the HMS login page
- Overlay your introduction text on the screen

### Action

- Speak directly to camera (confident, clear voice)
- Maintain eye contact with the camera lens
- Use hand gestures naturally (not stiff)
- Smile, be personable

### Audio

- Clear, calm voice
- No background noise
- Use intro music (optional): 3–5 second fade-in, then fade out as you start speaking

---

## SCENE 2: Approach to Problem Statement (0:30–1:00)

### Visual Setup

- **Transition:** Fade to screen sharing your desktop or slide with architecture diagram

### On-Screen Elements

Display a simple architecture diagram (you can create this in Figma, PowerPoint, or even draw it on a whiteboard and photograph it):

```
┌──────────────────────────────────────────────────────────┐
│                    HMS Architecture                      │
├──────────────────┬──────────────────────────────────────┤
│  Vue SPA         │  Flask Backend                       │
│ ┌────────────┐   │ ┌──────────────────────────────────┐ │
│ │Login/Reg   │   │ │ Auth Blueprint (login/register) │ │
│ │Dashboard   │   │ ├──────────────────────────────────┤ │
│ │Appt List   │   │ │ Patient Routes (book, view)     │ │
│ └────────────┘   │ ├──────────────────────────────────┤ │
│                  │ │ Doctor Routes (manage, confirm) │ │
│  ↕ HTTP/REST    │ ├──────────────────────────────────┤ │
│                  │ │ Admin Routes (users, metrics)   │ │
│                  │ └──────────────────────────────────┘ │
│                  │  Role-Based Decorators              │
│                  │  Auth Layer (Sessions/Tokens)       │
│                  │  ↓                                   │
│                  │  ┌──────────────────────────────────┐ │
│                  │  │ Database: Users, Appointments   │ │
│                  │  └──────────────────────────────────┘ │
└──────────────────┴──────────────────────────────────────┘
```

- Highlight the three roles in different colors (Patient = blue, Doctor = green, Admin = orange)
- Annotate: "Modular, secure, scalable"

### Action

- Point to sections of the diagram as you speak
- Emphasize the separation of concerns
- Use a pointer or cursor to highlight each component

### Audio

- Speak at measured pace, enunciating the architectural decisions
- Emphasize: "modular," "role-based," "secure," "scalable"

---

## SCENE 3: Key Features (1:00–2:30)

### Layout

Split screen or sequential screen recordings:

#### Subsection 3.1: Authentication & Registration (1:00–1:20)

**Visual:**
- Screen recording of browser showing HMS login page
- Click "Register" button
- Fill out registration form:
  - Name: (e.g., "Dr. Smith")
  - Email: (e.g., "dr.smith@hospital.com")
  - Password: (masked)
  - Role: (dropdown showing "admin", "doctor", "patient")
- Click "Register"
- Show confirmation or redirect to login
- Log in with the new account
- Show dashboard after login

**Audio Narration:**
"Users can sign up by providing their name, email, password, and selecting their role—patient, doctor, or admin. Passwords are securely hashed using industry-standard methods. Once registered, they log in and are automatically routed to their role-specific dashboard."

**Duration:** 20 seconds

---

#### Subsection 3.2: Role-Based Dashboards (1:20–1:45)

**Visual:**
Screen recording showing three consecutive dashboards:

1. **Patient Dashboard**
   - Show sidebar/menu highlighting "Patient"
   - Display sections: "Upcoming Appointments" (table/list), "Request New Appointment" (button)
   - Show a few dummy appointment cards with date, doctor name, status
   - Highlight: "Request New Appointment" button in a different color

2. **Doctor Dashboard**
   - Log out and log in as a doctor
   - Show sidebar/menu highlighting "Doctor"
   - Display: "My Appointments" (table with patient name, requested time, status)
   - Show action buttons: "Confirm", "Reject", "Complete"
   - Highlight: Appointments with status "requested" (waiting for action)

3. **Admin Dashboard**
   - Log out and log in as admin
   - Show sidebar/menu highlighting "Admin"
   - Display: "System Overview" with metrics (total users, total appointments, pending appointments)
   - Show a "Users" list with columns: name, email, role, actions (delete)

**Audio Narration:**
"Each role has a customized dashboard tailored to their needs. Patients see their upcoming appointments and can request new ones. Doctors view their scheduled appointments with patient details and can confirm or manage them. Admins have an overview of all users and key system metrics."

**Duration:** 25 seconds

---

#### Subsection 3.3: Appointment Booking & Management (1:45–2:10)

**Visual:**
Screen recording of a complete appointment workflow:

1. **Patient requests appointment:**
   - Log in as patient
   - Click "Request New Appointment"
   - Show form: Doctor dropdown (select a doctor), Date/time picker, Notes field
   - Fill in example data and submit
   - Show confirmation: "Appointment request submitted"

2. **Doctor receives and confirms:**
   - Log out, log in as the doctor you selected
   - Navigate to "My Appointments"
   - Show a new appointment card with status "Requested"
   - Click "Confirm" button
   - Show status change to "Confirmed" in real-time or with a refresh

3. **Both sides updated:**
   - Log back to patient and show appointment now has status "Confirmed"
   - Optionally show a "Complete" or "Cancel" action on the doctor's side

**Audio Narration:**
"Here's how appointment booking works: a patient selects a doctor and requests an appointment with a preferred time and any notes. The doctor receives this request and can confirm, reject, or propose an alternative time. Once confirmed, both the patient and doctor can see the appointment on their dashboards. The status flows from 'requested' to 'confirmed' to 'completed' or 'cancelled,' maintaining a clear record throughout."

**Duration:** 25 seconds

---

#### Subsection 3.4: Background Jobs (2:10–2:30)

**Visual:**
- Show code snippet in editor (VS Code) displaying `backend/jobs/tasks.py`
- Highlight sections like:
  - `send_appointment_reminder()` function
  - `cleanup_old_appointments()` function
  - Job scheduling configuration

Or, if the admin dashboard has a "Jobs" or "Logs" section, show that.

- Show a log output showing completed jobs and their timestamps

**Audio Narration:**
"Beyond real-time features, the system includes a background jobs framework for periodic tasks. This powers appointment reminders (e.g., reminding patients 24 hours before their appointment) and automatic cleanup of old data. This infrastructure is essential for real-world hospital operations and demonstrates a production-ready design."

**Duration:** 20 seconds

---

## SCENE 4: Additional Features (2:30–3:00)

### Visual Setup

Screen recording or code editor view:

#### Feature 1: Caching Layer (Redis) (2:30–2:40)

**Visual:**
- Show `backend/utils/cache.py` in the editor
- Highlight caching decorators like `@cache.cached(timeout=300)`
- Or show a backend config file showing Redis connection

**Audio Narration:**
"First, I've implemented a caching layer using Redis. This significantly improves performance by caching frequently accessed data like user lists and appointment counts, reducing database load."

**Duration:** 10 seconds

---

#### Feature 2: Appointment Notes (2:40–2:45)

**Visual:**
- Go back to appointment detail view in the UI
- Show a "Notes" section with past notes and an input field to add new ones
- Doctor/patient can add clinical or personal notes

**Audio Narration:**
"Second, appointment notes allow doctors and patients to leave detailed information about each appointment, improving communication and capturing clinical details."

**Duration:** 5 seconds

---

#### Feature 3: Status Tracking & Audit Trail (2:45–2:52)

**Visual:**
- Show a status history or log, e.g., clicking on an appointment shows:
  - "Created: 2025-11-25 10:00 AM"
  - "Status changed to Confirmed: 2025-11-25 11:30 AM (by Dr. Smith)"
  - "Status changed to Completed: 2025-11-30 03:15 PM (by Dr. Smith)"

**Audio Narration:**
"Third, the system maintains an audit trail of status changes, providing a clear record of who did what and when. This is crucial for compliance and debugging."

**Duration:** 7 seconds

---

#### Feature 4: Modular Jobs Framework (2:52–3:00)

**Visual:**
- Show code structure in backend/jobs/:
  - `__init__.py`
  - `tasks.py` with multiple job definitions
- Highlight that adding a new job is as simple as adding a new function

**Audio Narration:**
"Finally, the modular jobs framework makes it easy to add new background tasks without touching the core application logic. This extensibility demonstrates a production-minded design that can grow with future requirements."

**Duration:** 8 seconds

---

## SCENE 5: Closing (3:00–3:10, Optional)

### Visual Setup

- Fade back to title slide or a professional closing screen
- Display project repository link or QR code (if available)

### On-Screen Elements

- Text overlay: "Questions?"
- Your contact info (email or GitHub link)
- Project repository link

### Audio Narration

"Thank you for watching. This Hospital Management System demonstrates a clean, scalable approach to healthcare software. The project is open for discussion, and I'm happy to dive deeper into any architectural or implementation details. Thank you."

---

## Recording Tips & Checklist

- [ ] Use a professional or neutral background (bookshelf, simple wall, or virtual background)
- [ ] Ensure good lighting (face is well-lit, minimal shadows)
- [ ] Use a good microphone (USB headset or external mic)
- [ ] Record in a quiet environment (close windows, turn off notifications)
- [ ] Speak clearly and at a moderate pace (130–140 words/min)
- [ ] Maintain good posture and eye contact with the camera
- [ ] Use cursor highlights or pointer tools during screen sharing to guide viewer's eye
- [ ] Practice the presentation 2–3 times before final recording
- [ ] Export at 1080p (1920x1080) or 720p minimum
- [ ] Aim for 30 fps frame rate
- [ ] Add intro/outro music (royalty-free, 3–5 sec each) for polish

---

## Files to Have Ready During Recording

- Browser with HMS app running locally (or deployed test instance)
- VS Code with the backend code visible
- Architecture diagram (PowerPoint, Figma, or PDF)
- A second monitor or tablet to read the script off-camera

---

## Final Video Checklist

- [ ] Total duration: ~3 minutes
- [ ] Audio is clear and loud enough
- [ ] Screen recordings are at high resolution
- [ ] Transitions are smooth (fade, cut, or dissolve)
- [ ] Text overlays are readable (large font, good contrast)
- [ ] Video is saved in a common format (MP4, WebM, or MOV)
- [ ] Upload to Google Drive and share link in the project report

