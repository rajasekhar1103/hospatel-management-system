# Hospital Management System

A comprehensive Hospital Management System (HMS) designed to streamline healthcare operations. This application features a robust backend API and a modern frontend interface to manage patients, doctors, appointments, and medical records.

## Features

*   **User Roles**: Admin, Doctor, and Patient dashboards.
*   **Appointment Management**: Booking, rescheduling, and cancellation of appointments.
*   **Patient Records**: Management of patient history and medical details.
*   **Doctor Availability**: Management of doctor schedules and availability.
*   **Secure Authentication**: User login and registration.

## Tech Stack

### Backend
*   **Language**: Python
*   **Framework**: Flask (assumed based on structure)
*   **Database**: SQLite (default) / SQLAlchemy
*   **Dependencies**:Celery, redis, Werkzeug

### Frontend
*   **Framework**: Vue.js 3
*   **Build Tool**: Vite
*   **Styling**: CSS / Component-based styles

## Setup Instructions

### Prerequisites
*   Python 3.8+
*   Node.js & npm

### Backend Setup
1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate.ps1  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the application:
    ```bash
    python app.py
    ```

### Frontend Setup
1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
### Admin login
*  **ID**: admin
*  **Password**: adminpass123
## Usage
Once both servers are running, access the application in your browser (typically at `http://localhost:5173` for Vite).
