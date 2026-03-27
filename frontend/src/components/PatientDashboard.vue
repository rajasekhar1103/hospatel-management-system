<template>
    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Sidebar / Navigation -->
            <div class="col-md-3 mb-4">
                <div class="glass-panel p-3 h-100">
                    <div class="text-center mb-4">
                        <div class="avatar-circle bg-accent text-white mx-auto mb-3 d-flex align-items-center justify-content-center display-4 fw-bold shadow-sm" style="width: 80px; height: 80px; border-radius: 50%;">
                            P
                        </div>
                        <h4 class="fw-bold">Patient Portal</h4>
                        <p class="text-muted small">Manage your health journey</p>
                    </div>
                    
                    <div class="nav flex-column nav-pills" id="patientTabs" role="tablist">
                        <button class="nav-link active mb-2 text-start fw-medium" id="book-tab" data-bs-toggle="pill" data-bs-target="#book" type="button" role="tab">
                            📅 Book Appointment
                        </button>
                        <button class="nav-link mb-2 text-start fw-medium" id="appointments-tab" data-bs-toggle="pill" data-bs-target="#appointments" type="button" role="tab" @click="fetchAppointments">
                            📋 My Appointments
                        </button>
                        <button class="nav-link mb-2 text-start fw-medium" id="history-tab" data-bs-toggle="pill" data-bs-target="#history" type="button" role="tab" @click="fetchTreatmentHistory">
                            📜 Treatment History
                        </button>
                        <button class="nav-link mt-4 text-start fw-medium text-danger" @click="logout">
                            🚪 Logout
                        </button>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9">
                <div class="tab-content" id="patientTabsContent">
                    
                    <!-- Book Appointment Tab -->
                    <div class="tab-pane fade show active" id="book" role="tabpanel">
                        <div class="glass-panel p-4 mb-4">
                            <h4 class="mb-4 fw-bold text-primary">Find a Doctor</h4>
                            
                            <div class="row g-3 mb-4">
                                <div class="col-md-5">
                                    <label class="form-label text-muted small fw-bold">SPECIALIZATION</label>
                                    <select class="form-select border-0 bg-light shadow-sm" v-model="selectedSpecialization" @change="fetchDoctors">
                                        <option value="">Select Specialization...</option>
                                        <option v-for="spec in specializations" :key="spec.id" :value="spec.id">{{ spec.name }}</option>
                                    </select>
                                </div>
                                <div class="col-md-5">
                                    <label class="form-label text-muted small fw-bold">DATE</label>
                                    <input type="date" class="form-control border-0 bg-light shadow-sm" v-model="selectedDate" @change="fetchDoctors">
                                </div>
                                <div class="col-md-2 d-flex align-items-end">
                                    <button class="btn btn-primary w-100 shadow-sm" @click="fetchDoctors">Search</button>
                                </div>
                            </div>

                            <div v-if="availableDoctors.length > 0" class="row g-3">
                                <div v-for="doc in availableDoctors" :key="doc.id" class="col-md-6 col-lg-4">
                                    <div class="card h-100 border-0 shadow-sm hover-elevate">
                                        <div class="card-body">
                                            <h6 class="fw-bold mb-1">{{ doc.name }}</h6>
                                            <p class="text-muted small mb-3">{{ doc.specialization }}</p>
                                            <div class="d-flex flex-wrap gap-2">
                                                <button v-for="(time, idx) in doc.slots" :key="idx" class="btn btn-outline-primary btn-sm me-2 mb-2" @click="confirmBooking(doc, time)">{{ time }}</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div v-else-if="hasSearched" class="alert alert-light border-0 shadow-sm text-center py-4">
                                <p class="mb-0 text-muted">No doctors available for the selected criteria.</p>
                            </div>
                            <div v-else class="text-center py-5 text-muted opacity-50">
                                <div class="display-1 mb-3">🔍</div>
                                <p>Select a specialization and date to start searching.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Appointments Tab -->
                    <div class="tab-pane fade" id="appointments" role="tabpanel">
                        <div class="glass-panel p-4">
                            <h4 class="mb-4 fw-bold text-primary">My Upcoming Appointments</h4>
                            <div v-if="myAppointments.length > 0" class="d-flex flex-column gap-3">
                                <div v-for="appt in myAppointments" :key="appt.id" class="card border-0 shadow-sm">
                                    <div class="card-body d-flex justify-content-between align-items-center">
                                        <div class="d-flex align-items-center">
                                            <div class="date-box bg-light rounded p-2 text-center me-3" style="min-width: 60px;">
                                                <div class="fw-bold text-primary">{{ appt.date.split('-')[2] }}</div>
                                                <small class="text-muted text-uppercase" style="font-size: 0.7rem;">{{ new Date(appt.date).toLocaleString('default', { month: 'short' }) }}</small>
                                            </div>
                                            <div>
                                                <h6 class="mb-1 fw-bold">Dr. {{ appt.doctor_name }}</h6>
                                                <p class="mb-0 text-muted small">{{ appt.specialization }} • {{ appt.time }}</p>
                                            </div>
                                        </div>
                                        <div class="d-flex align-items-center gap-3">
                                            <span :class="getStatusBadge(appt.status)">{{ appt.status }}</span>
                                            <button v-if="appt.status === 'Booked'" class="btn btn-outline-danger btn-sm rounded-pill px-3" @click="cancelAppointment(appt.id)">Cancel</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div v-else class="text-center py-5 text-muted">
                                <p>No upcoming appointments scheduled.</p>
                            </div>
                        </div>
                    </div>

                    <!-- History Tab -->
                    <div class="tab-pane fade" id="history" role="tabpanel">
                        <div class="glass-panel p-4">
                            <div class="d-flex justify-content-between align-items-center mb-4">
                                <h4 class="fw-bold text-primary mb-0">Treatment History</h4>
                                <button class="btn btn-outline-primary btn-sm" @click="triggerCSVExport">
                                    📥 Export CSV
                                </button>
                            </div>
                            
                            <div v-if="treatmentHistory.length > 0" class="d-flex flex-column gap-3">
                                <div v-for="history in treatmentHistory" :key="history.id" class="card border-0 shadow-sm">
                                    <div class="card-header bg-transparent border-0 d-flex justify-content-between align-items-center pb-0 pt-3">
                                        <span class="badge bg-light text-dark border">{{ history.date }}</span>
                                        <small class="text-muted">Dr. {{ history.doctor_name }}</small>
                                    </div>
                                    <div class="card-body">
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <label class="small text-muted fw-bold text-uppercase">Diagnosis</label>
                                                <p class="mb-0 fw-medium">{{ history.diagnosis || 'N/A' }}</p>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="small text-muted fw-bold text-uppercase">Prescription</label>
                                                <p class="mb-0 fw-medium">{{ history.prescription || 'N/A' }}</p>
                                            </div>
                                            <div class="col-12" v-if="history.notes">
                                                <label class="small text-muted fw-bold text-uppercase">Notes</label>
                                                <p class="mb-0 text-muted small fst-italic">{{ history.notes }}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div v-else class="text-center py-5 text-muted">
                                <p>No past treatment history found.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Booking Confirmation Modal -->
        <div class="modal fade" id="bookingModal" tabindex="-1" aria-hidden="true" ref="bookingModal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-header border-0 bg-primary text-white">
                        <h5 class="modal-title fw-bold">Confirm Booking</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body p-4 text-center">
                        <div class="display-4 mb-3">📅</div>
                        <p class="lead mb-1">You are about to book an appointment with</p>
                        <h5 class="fw-bold text-primary mb-3">Dr. {{ selectedDoctor?.full_name }}</h5>
                        <div class="d-inline-block bg-light rounded px-4 py-2">
                            <span class="fw-bold">{{ selectedDate }}</span> at <span class="fw-bold">{{ selectedTime }}</span>
                        </div>
                    </div>
                    <div class="modal-footer border-0 justify-content-center pb-4">
                        <button type="button" class="btn btn-light px-4" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary px-4 fw-bold" @click="finalizeBooking">Confirm Booking</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
const getToken = () => localStorage.getItem('access_token');

export default {
    name: 'PatientDashboard',
    data() {
        return {
            specializations: [],
            selectedSpecialization: '',
            selectedDate: new Date().toISOString().slice(0, 10),
            availableDoctors: [],
            hasSearched: false,
            
            myAppointments: [],
            treatmentHistory: [],
            fetchError: null,
            
            // Modal data
            selectedDoctor: null,
            selectedTime: null,
            bookingModalInstance: null,
        };
    },
    mounted() {
        this.fetchSpecializations();
        this.fetchAppointments();
        // Initialize Bootstrap modal
        if (window.bootstrap && window.bootstrap.Modal) {
            this.bookingModalInstance = new window.bootstrap.Modal(this.$refs.bookingModal);
        }
    },
    methods: {
        logout() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_role');
            this.$router.push('/login');
        },
        getStatusBadge(status) {
            const base = 'badge rounded-pill px-3 py-2 ';
            return status === 'Booked' ? base + 'bg-soft-primary text-primary' : 
                   status === 'Completed' ? base + 'bg-soft-success text-success' : base + 'bg-soft-danger text-danger';
        },
        async fetchSpecializations() {
            try {
                const response = await fetch('/api/patient/specializations');
                if (response.ok) {
                    this.specializations = await response.json();
                } else {
                    this.fetchError = `Status: ${response.status}`;
                }
            } catch (e) { 
                console.error(e); 
                this.fetchError = e.message;
            }
        },
        async fetchDoctors() {
            if (!this.selectedDate) return;
            this.hasSearched = true;
            this.availableDoctors = [];
            
            let url = `/api/patient/doctors?date=${this.selectedDate}`;
            if (this.selectedSpecialization) url += `&spec_id=${this.selectedSpecialization}`;
            
            try {
                const response = await fetch(url, { headers: { 'Authorization': `Bearer ${getToken()}` } });
                if (response.ok) this.availableDoctors = await response.json();
            } catch (e) { console.error(e); }
        },
        confirmBooking(doctor, time) {
            this.selectedDoctor = doctor;
            this.selectedTime = time;
            if (this.bookingModalInstance) this.bookingModalInstance.show();
        },
        async finalizeBooking() {
            if (this.bookingModalInstance) this.bookingModalInstance.hide();
            
            const payload = {
                doctor_id: this.selectedDoctor.id,
                date: this.selectedDate,
                time: this.selectedTime
            };

            try {
                const response = await fetch('/api/patient/appointment', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    alert('Appointment booked successfully!');
                    this.fetchDoctors(); // Refresh slots
                    this.fetchAppointments(); // Refresh my appointments
                } else {
                    const data = await response.json();
                    alert(`Booking failed: ${data.msg}`);
                }
            } catch (e) { console.error(e); }
        },
        async fetchAppointments() {
            try {
                const response = await fetch('/api/patient/appointments', { headers: { 'Authorization': `Bearer ${getToken()}` } });
                if (response.ok) this.myAppointments = await response.json();
            } catch (e) { console.error(e); }
        },
        async fetchTreatmentHistory() {
            try {
                const response = await fetch('/api/patient/history', { headers: { 'Authorization': `Bearer ${getToken()}` } });
                if (response.ok) this.treatmentHistory = await response.json();
            } catch (e) { console.error(e); }
        },
        async cancelAppointment(id) {
            if (!confirm('Are you sure you want to cancel this appointment?')) return;
            try {
                const response = await fetch(`/api/patient/appointment/${id}/cancel`, {
                    method: 'PUT',
                    headers: { 'Authorization': `Bearer ${getToken()}` }
                });
                if (response.ok) this.fetchAppointments();
                else {
                    const data = await response.json();
                    alert(`Cancellation failed: ${data.msg || response.statusText}`);
                }
            } catch (e) { console.error(e); }
        },
        async triggerCSVExport() {
            try {
                const response = await fetch('/api/patient/export_csv', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${getToken()}` }
                });
                if (!response.ok) return alert('Export failed.');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'treatment_history.csv';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            } catch (e) { console.error(e); }
        }
    }
};
</script>

<style scoped>
.bg-soft-primary { background-color: rgba(14, 165, 233, 0.1); }
.bg-soft-success { background-color: rgba(16, 185, 129, 0.1); }
.bg-soft-danger { background-color: rgba(239, 68, 68, 0.1); }
.bg-soft-info { background-color: rgba(56, 189, 248, 0.1); }
.bg-accent { background-color: var(--accent-color); }

.nav-pills .nav-link {
    color: var(--text-secondary);
    border-radius: var(--radius-md);
    padding: 1rem;
    transition: all 0.2s;
}
.nav-pills .nav-link:hover {
    background-color: rgba(14, 165, 233, 0.05);
    color: var(--accent-color);
}
.nav-pills .nav-link.active {
    background-color: var(--accent-color);
    color: white;
    box-shadow: var(--shadow-md);
}
.hover-elevate {
    transition: transform 0.2s, box-shadow 0.2s;
}
.hover-elevate:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg) !important;
}
.cursor-pointer {
    cursor: pointer;
}
</style>