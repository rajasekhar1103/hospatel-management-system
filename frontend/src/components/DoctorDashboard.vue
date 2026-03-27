<template>
    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3 mb-4">
                <div class="glass-panel p-3 h-100">
                    <div class="text-center mb-4">
                        <div class="avatar-circle bg-success text-white mx-auto mb-3 d-flex align-items-center justify-content-center display-4 fw-bold shadow-sm" style="width: 80px; height: 80px; border-radius: 50%;">
                            D
                        </div>
                        <h4 class="fw-bold">Doctor Portal</h4>
                        <p class="text-muted small">Manage patients & schedule</p>
                    </div>
                    
                    <div class="nav flex-column nav-pills" id="doctorTabs" role="tablist">
                        <button class="nav-link active mb-2 text-start fw-medium" id="schedule-tab" data-bs-toggle="pill" data-bs-target="#schedule" type="button" role="tab">
                            📅 Appointments
                        </button>
                        <button class="nav-link mb-2 text-start fw-medium" id="patients-tab" data-bs-toggle="pill" data-bs-target="#patients" type="button" role="tab">
                            👥 My Patients
                        </button>
                        <button class="nav-link mb-2 text-start fw-medium" id="availability-tab" data-bs-toggle="pill" data-bs-target="#availability" type="button" role="tab" @click="fetchAvailability">
                            ⏰ Availability
                        </button>
                        <button class="nav-link mt-4 text-start fw-medium text-danger" @click="logout">
                            🚪 Logout
                        </button>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9">
                <div class="tab-content" id="doctorTabsContent">
                    
                    <!-- Appointments Tab -->
                    <div class="tab-pane fade show active" id="schedule" role="tabpanel">
                        <div class="glass-panel p-4">
                            <h4 class="mb-4 fw-bold text-primary">Upcoming Appointments</h4>
                            
                            <div v-if="upcomingAppointments.length > 0" class="row g-3">
                                <div v-for="appt in upcomingAppointments" :key="appt.id" class="col-md-6 col-lg-4">
                                    <div class="card h-100 border-0 shadow-sm hover-elevate">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-start mb-3">
                                                <div class="date-box bg-light rounded p-2 text-center" style="min-width: 50px;">
                                                    <div class="fw-bold text-primary">{{ appt.date.split('-')[2] }}</div>
                                                    <small class="text-muted text-uppercase" style="font-size: 0.6rem;">{{ new Date(appt.date).toLocaleString('default', { month: 'short' }) }}</small>
                                                </div>
                                                <span :class="getStatusBadge(appt.status)">{{ appt.status }}</span>
                                            </div>
                                            
                                            <h6 class="fw-bold mb-1">{{ appt.patient_name }}</h6>
                                            <p class="text-muted small mb-3">Time: {{ appt.time }}</p>
                                            
                                            <div class="d-grid gap-2">
                                                <button v-if="appt.status === 'Booked'" class="btn btn-primary btn-sm" @click="openTreatmentModal(appt)">Treat Patient</button>
                                                <button v-if="appt.status === 'Booked'" class="btn btn-outline-danger btn-sm" @click="cancelAppointment(appt.id)">Cancel</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div v-else class="text-center py-5 text-muted">
                                <p>No upcoming appointments found.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Patients Tab -->
                    <div class="tab-pane fade" id="patients" role="tabpanel">
                        <div class="glass-panel p-4">
                            <h4 class="mb-4 fw-bold text-primary">Assigned Patients</h4>
                            <div v-if="assignedPatients.length > 0" class="list-group list-group-flush">
                                <div v-for="patient in assignedPatients" :key="patient.id" class="list-group-item bg-transparent d-flex justify-content-between align-items-center py-3 border-bottom">
                                    <div class="d-flex align-items-center">
                                        <div class="bg-light rounded-circle p-2 me-3 text-secondary">👤</div>
                                        <span class="fw-medium">{{ patient.name }}</span>
                                    </div>
                                    <button class="btn btn-sm btn-outline-secondary rounded-pill px-3" @click="viewPatientHistory(patient)">View History</button>
                                </div>
                            </div>
                            <div v-else class="text-center py-5 text-muted">
                                <p>No patients assigned yet.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Availability Tab -->
                    <div class="tab-pane fade" id="availability" role="tabpanel">
                        <div class="glass-panel p-4">
                            <h4 class="mb-4 fw-bold text-primary">Manage Availability</h4>
                            
                            <div class="row">
                                <div class="col-md-5 border-end">
                                    <label class="form-label text-muted small fw-bold">SELECT DATE</label>
                                    <input type="date" class="form-control mb-4 shadow-sm" v-model="selectedDate" @change="loadSlotsForDate">
                                    
                                    <div v-if="selectedDate">
                                        <label class="form-label text-muted small fw-bold">ADD NEW SLOT</label>
                                        <div class="input-group mb-3">
                                            <input type="time" class="form-control" v-model="newSlotTime">
                                            <button class="btn btn-success text-white" type="button" @click="addSlot">Add</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-md-7 ps-md-4">
                                    <div v-if="selectedDate">
                                        <div class="d-flex justify-content-between align-items-center mb-3">
                                            <label class="form-label text-muted small fw-bold mb-0">SLOTS FOR {{ selectedDate }}</label>
                                            <button class="btn btn-primary btn-sm" @click="saveAvailability">Save Changes</button>
                                        </div>
                                        
                                        <div class="d-flex flex-wrap gap-2">
                                            <span v-for="(slot, index) in currentSlots" :key="index" class="badge bg-soft-info text-info p-2 d-flex align-items-center border border-info border-opacity-25">
                                                {{ slot }} 
                                                <button type="button" class="btn-close ms-2" style="font-size: 0.5em;" @click="removeSlot(index)"></button>
                                            </span>
                                            <span v-if="currentSlots.length === 0" class="text-muted small fst-italic">No slots added yet.</span>
                                        </div>
                                    </div>
                                    <div v-else class="text-center py-5 text-muted opacity-50">
                                        <div class="display-4 mb-2">📅</div>
                                        <p>Select a date to manage slots.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Treatment Modal -->
        <div class="modal fade" id="treatmentModal" tabindex="-1" ref="treatmentModal">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-header border-0 bg-success text-white">
                        <h5 class="modal-title fw-bold">Record Treatment</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form @submit.prevent="submitTreatment">
                        <div class="modal-body p-4">
                            <div class="mb-3">
                                <label class="form-label fw-bold text-muted small">DIAGNOSIS</label>
                                <textarea class="form-control bg-light border-0" v-model="treatmentDetails.diagnosis" rows="2" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-bold text-muted small">PRESCRIPTION</label>
                                <textarea class="form-control bg-light border-0" v-model="treatmentDetails.prescription" rows="3" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-bold text-muted small">NOTES</label>
                                <textarea class="form-control bg-light border-0" v-model="treatmentDetails.notes" rows="2"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer border-0 bg-light">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="submit" class="btn btn-success px-4 fw-bold">Save Treatment</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Patient History Modal -->
        <div class="modal fade" id="historyModal" tabindex="-1" ref="historyModal">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-header border-0 bg-info text-white">
                        <h5 class="modal-title fw-bold">{{ selectedPatient?.name }} - Treatment History</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body p-4">
                        <div v-if="patientHistory.length > 0" class="d-flex flex-column gap-3">
                            <div v-for="history in patientHistory" :key="history.id" class="card border-0 shadow-sm">
                                <div class="card-header bg-light border-0 d-flex justify-content-between align-items-center">
                                    <span class="badge bg-light text-dark border">{{ history.date }}</span>
                                    <small class="text-muted">{{ history.specialization }}</small>
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
                            <p>No completed treatment history found for this patient.</p>
                        </div>
                    </div>
                    <div class="modal-footer border-0 bg-light">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { Modal } from 'bootstrap';

const getToken = () => localStorage.getItem('access_token');

export default {
    name: 'DoctorDashboard',
    data() {
        return {
            upcomingAppointments: [],
            assignedPatients: [],
            
            // Availability Data
            selectedDate: '',
            currentSlots: [],
            newSlotTime: '',
            allAvailability: [], // Cache of fetched availability
            
            // Treatment Data
            currentAppt: null,
            treatmentDetails: { diagnosis: '', prescription: '', notes: '' },
            treatmentModalInstance: null,
            
            // Patient History Data
            selectedPatient: null,
            patientHistory: [],
            historyModalInstance: null,
        };
    },
    mounted() {
        this.fetchSchedule();
        this.fetchPatients();
        if (window.bootstrap && window.bootstrap.Modal) {
             this.treatmentModalInstance = new window.bootstrap.Modal(this.$refs.treatmentModal);
             this.historyModalInstance = new window.bootstrap.Modal(this.$refs.historyModal);
        }
    },
    methods: {
        logout() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_role');
            this.$router.push('/login');
        },
        getStatusBadge(status) {
            const base = 'badge rounded-pill px-2 py-1 ';
            return status === 'Booked' ? base + 'bg-soft-primary text-primary' : 
                   status === 'Completed' ? base + 'bg-soft-success text-success' : base + 'bg-soft-danger text-danger';
        },
        async fetchSchedule() {
            try {
                const response = await fetch('/api/doctor/schedule', { headers: { 'Authorization': `Bearer ${getToken()}` } });
                if (response.ok) this.upcomingAppointments = await response.json();
            } catch (e) { console.error(e); }
        },
        async fetchPatients() {
            try {
                const response = await fetch('/api/doctor/patients', { headers: { 'Authorization': `Bearer ${getToken()}` } });
                if (response.ok) this.assignedPatients = await response.json();
            } catch (e) { console.error(e); }
        },
        
        // --- Availability Logic ---
        async fetchAvailability() {
            try {
                const response = await fetch('/api/doctor/availability', { headers: { 'Authorization': `Bearer ${getToken()}` } });
                if (response.ok) {
                    this.allAvailability = await response.json();
                    // If a date is selected, refresh its slots
                    if (this.selectedDate) this.loadSlotsForDate();
                }
            } catch (e) { console.error(e); }
        },
        loadSlotsForDate() {
            const dayData = this.allAvailability.find(d => d.date === this.selectedDate);
            this.currentSlots = dayData ? [...dayData.slots] : [];
        },
        addSlot() {
            if (!this.newSlotTime) return;
            if (!this.currentSlots.includes(this.newSlotTime)) {
                this.currentSlots.push(this.newSlotTime);
                this.currentSlots.sort();
            }
            this.newSlotTime = '';
        },
        removeSlot(index) {
            this.currentSlots.splice(index, 1);
        },
        async saveAvailability() {
            const payload = [{
                date: this.selectedDate,
                slots: this.currentSlots
            }];
            
            try {
                const response = await fetch('/api/doctor/availability', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (response.ok) {
                    alert('Availability saved!');
                    this.fetchAvailability(); // Refresh cache
                } else {
                    alert('Failed to save.');
                }
            } catch (e) { console.error(e); }
        },

        // --- Treatment Logic ---
        openTreatmentModal(appt) {
            this.currentAppt = appt;
            this.treatmentDetails = { diagnosis: '', prescription: '', notes: '' };
            if (this.treatmentModalInstance) this.treatmentModalInstance.show();
        },
        async submitTreatment() {
            const payload = {
                appointment_id: this.currentAppt.id,
                ...this.treatmentDetails
            };
            try {
                const response = await fetch('/api/doctor/treatment', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (response.ok) {
                    alert('Treatment recorded!');
                    if (this.treatmentModalInstance) this.treatmentModalInstance.hide();
                    this.fetchSchedule(); // Refresh list
                } else {
                    alert('Failed to record treatment.');
                }
            } catch (e) { console.error(e); }
        },
        async cancelAppointment(id) {
            if(!confirm('Cancel this appointment?')) return;
            try {
                const response = await fetch(`/api/doctor/appointment/${id}/status`, {
                    method: 'PUT',
                    headers: { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: 'Cancelled' })
                });
                if (response.ok) this.fetchSchedule();
            } catch (e) { console.error(e); }
        },
        
        // --- Patient History Logic ---
        async viewPatientHistory(patient) {
            this.selectedPatient = patient;
            this.patientHistory = [];
            try {
                const response = await fetch(`/api/doctor/patient/${patient.id}/history`, {
                    headers: { 'Authorization': `Bearer ${getToken()}` }
                });
                if (response.ok) {
                    this.patientHistory = await response.json();
                    if (this.historyModalInstance) this.historyModalInstance.show();
                } else {
                    alert('Failed to load patient history.');
                }
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
    background-color: rgba(16, 185, 129, 0.05);
    color: var(--success-color);
}
.nav-pills .nav-link.active {
    background-color: var(--success-color);
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
</style>