<template>
    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3 mb-4">
                <div class="glass-panel p-3 h-100">
                    <div class="text-center mb-4">
                        <div class="avatar-circle bg-primary text-white mx-auto mb-3 d-flex align-items-center justify-content-center display-4 fw-bold shadow-sm" style="width: 80px; height: 80px; border-radius: 50%;">
                            A
                        </div>
                        <h4 class="fw-bold">Admin Portal</h4>
                        <p class="text-muted small">System Management</p>
                    </div>
                    
                    <div class="nav flex-column nav-pills" id="adminTabs" role="tablist">
                        <button class="nav-link active mb-2 text-start fw-medium" id="doctors-tab" data-bs-toggle="pill" data-bs-target="#doctors" type="button" role="tab" @click="clearSearchAndRefresh">
                            👨‍⚕️ Doctor Management
                        </button>
                        <button class="nav-link mb-2 text-start fw-medium" id="users-tab" data-bs-toggle="pill" data-bs-target="#users" type="button" role="tab" @click="loadAllUsersForTab">
                            👥 User Search & Block
                        </button>
                        <button class="nav-link mb-2 text-start fw-medium" id="appointments-tab" data-bs-toggle="pill" data-bs-target="#appointments" type="button" role="tab" @click="fetchAllAppointments">
                            📅 All Appointments
                        </button>
                        <button class="nav-link mb-2 text-start fw-medium" id="history-tab" data-bs-toggle="pill" data-bs-target="#history" type="button" role="tab" @click="fetchSystemHistory">
                            📜 System History
                        </button>
                        <button class="nav-link mt-4 text-start fw-medium text-danger" @click="logout">
                            🚪 Logout
                        </button>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9">
                <!-- Stats Row -->
                <div class="row mb-4 g-3">
                    <div class="col-md-4">
                        <div class="glass-panel p-3 d-flex justify-content-between align-items-center border-start border-4 border-primary">
                            <div>
                                <h6 class="text-muted text-uppercase small fw-bold mb-1">Total Doctors</h6>
                                <h2 class="mb-0 fw-bold text-primary">{{ stats.total_doctors }}</h2>
                            </div>
                            <div class="bg-soft-primary p-2 rounded-circle text-primary display-6">👨‍⚕️</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="glass-panel p-3 d-flex justify-content-between align-items-center border-start border-4 border-info">
                            <div>
                                <h6 class="text-muted text-uppercase small fw-bold mb-1">Total Patients</h6>
                                <h2 class="mb-0 fw-bold text-info">{{ stats.total_patients }}</h2>
                            </div>
                            <div class="bg-soft-info p-2 rounded-circle text-info display-6">👥</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="glass-panel p-3 d-flex justify-content-between align-items-center border-start border-4 border-warning">
                            <div>
                                <h6 class="text-muted text-uppercase small fw-bold mb-1">Upcoming Appts</h6>
                                <h2 class="mb-0 fw-bold text-warning">{{ stats.upcoming_appointments }}</h2>
                            </div>
                            <div class="bg-soft-warning p-2 rounded-circle text-warning display-6">📅</div>
                        </div>
                    </div>
                </div>

                <div class="tab-content" id="adminTabsContent">
                    
                    <!-- Doctor Management Tab -->
                    <div class="tab-pane fade show active" id="doctors" role="tabpanel">
                        <div class="glass-panel p-4">
                            <div class="d-flex justify-content-between align-items-center mb-4">
                                <h4 class="fw-bold text-primary mb-0">Manage Doctors</h4>
                                <button class="btn btn-primary shadow-sm" @click="toggleAddForm">
                                    {{ showAddForm ? 'Cancel' : '+ Add New Doctor' }}
                                </button>
                            </div>

                            <div class="input-group mb-4 shadow-sm">
                                <span class="input-group-text bg-white border-end-0"><i class="text-muted">🔍</i></span>
                                <input type="text" class="form-control border-start-0 ps-0" placeholder="Search doctors by name or specialization..." v-model="doctorSearchQuery" @keyup.enter="searchDoctors">
                                <button class="btn btn-primary" type="button" @click="searchDoctors">Search</button>
                                <button class="btn btn-light border" type="button" @click="clearDoctorSearchAndRefresh">Clear</button>
                            </div>
                            
                            <div v-if="showAddForm" class="card mb-4 border-0 shadow-sm bg-light">
                                <div class="card-body p-4">
                                    <h5 class="card-title fw-bold mb-3 text-primary">Register New Doctor</h5>
                                    <form @submit.prevent="submitDoctor">
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <label class="form-label small fw-bold text-muted">USERNAME</label>
                                                <input type="text" class="form-control" v-model="newDoctor.username" required>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label small fw-bold text-muted">PASSWORD</label>
                                                <input type="password" class="form-control" v-model="newDoctor.password" required>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label small fw-bold text-muted">FULL NAME</label>
                                                <input type="text" class="form-control" v-model="newDoctor.full_name" required>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label small fw-bold text-muted">SPECIALIZATION</label>
                                                <input type="text" class="form-control" v-model="newDoctor.specialization" placeholder="e.g. Cardiology" required>
                                            </div>
                                            <div class="col-md-12">
                                                <label class="form-label small fw-bold text-muted">CONTACT INFO</label>
                                                <input type="text" class="form-control" v-model="newDoctor.contact_info">
                                            </div>
                                            <div class="col-md-12">
                                                <label class="form-label small fw-bold text-muted">BIO</label>
                                                <textarea class="form-control" v-model="newDoctor.bio" rows="2"></textarea>
                                            </div>
                                            <div class="col-12 text-end">
                                                <button type="submit" class="btn btn-success px-4 fw-bold">Create Account</button>
                                            </div>
                                        </div>
                                    </form>
                                </div>
                            </div>

                            <div class="table-responsive">
                                <table class="table table-hover align-middle">
                                    <thead class="bg-light text-muted small text-uppercase">
                                        <tr>
                                            <th class="border-0 rounded-start ps-3">Name</th>
                                            <th class="border-0">Specialization</th>
                                            <th class="border-0">Status</th>
                                            <th class="border-0 rounded-end text-end pe-3">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="doc in doctorList" :key="doc.id">
                                            <td class="ps-3 fw-medium">{{ doc.full_name }}</td>
                                            <td><span class="badge bg-soft-info text-info">{{ doc.specialization }}</span></td>
                                            <td>
                                                <span v-if="doc.is_active" class="badge bg-soft-success text-success">Active</span>
                                                <span v-else class="badge bg-soft-danger text-danger">Inactive</span>
                                            </td>
                                            <td class="text-end pe-3">
                                                <button class="btn btn-sm btn-outline-primary me-2" @click="openEditModal(doc)">Edit</button>
                                                <button :class="['btn btn-sm', doc.is_active ? 'btn-outline-danger' : 'btn-outline-success']" @click="toggleBlacklist(doc.id, doc.is_active)">
                                                    {{ doc.is_active ? 'Block' : 'Unblock' }}
                                                </button>
                                            </td>
                                        </tr>
                                        <tr v-if="doctorList.length === 0">
                                            <td colspan="4" class="text-center py-4 text-muted">No doctors found.</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <!-- User Search Tab -->
                    <div class="tab-pane fade" id="users" role="tabpanel">
                        <div class="glass-panel p-4">
                            <h4 class="mb-4 fw-bold text-primary">User Management</h4>
                            <div class="input-group mb-4 shadow-sm">
                                <input type="text" class="form-control" placeholder="Search by name, ID, or contact..." v-model="searchQuery" @keyup.enter="searchUsers">
                                <button class="btn btn-primary px-4" type="button" @click="searchUsers">Search</button>
                            </div>
                            
                            <div v-if="searchResults.length" class="list-group list-group-flush">
                                <div v-for="user in searchResults" :key="user.id" class="list-group-item bg-transparent d-flex justify-content-between align-items-center py-3 border-bottom">
                                    <div>
                                        <div class="d-flex align-items-center mb-1">
                                            <span class="fw-bold me-2">{{ user.full_name }}</span>
                                            <span class="badge bg-light text-dark border">{{ user.role }}</span>
                                        </div>
                                        <div class="small text-muted">
                                            <span class="me-3">@{{ user.username }}</span>
                                            <span :class="user.is_active ? 'text-success' : 'text-danger'">● {{ user.is_active ? 'Active' : 'Blocked' }}</span>
                                        </div>
                                    </div>
                                    <button :class="['btn btn-sm px-3 fw-bold', user.is_active ? 'btn-soft-danger' : 'btn-soft-success']" @click="toggleBlacklist(user.id, user.is_active)">
                                        {{ user.is_active ? 'Block User' : 'Unblock User' }}
                                    </button>
                                </div>
                            </div>
                            <div v-else-if="hasSearched && searchResults.length === 0" class="text-center py-5 text-muted">
                                <p>No users found matching your query.</p>
                            </div>
                            <div v-else-if="!hasSearched" class="text-center py-5 text-muted opacity-50">
                                <div class="display-4 mb-2">🔍</div>
                                <p>Search for users to manage their access.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Appointments Tab -->
                    <div class="tab-pane fade" id="appointments" role="tabpanel">
                        <div class="glass-panel p-4">
                            <h4 class="mb-4 fw-bold text-primary">All Appointments</h4>
                            <div class="table-responsive">
                                <table class="table table-hover align-middle">
                                    <thead class="bg-light text-muted small text-uppercase">
                                        <tr>
                                            <th class="border-0 rounded-start ps-3">Date & Time</th>
                                            <th class="border-0">Status</th>
                                            <th class="border-0">Patient</th>
                                            <th class="border-0 rounded-end">Doctor</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="appt in allAppointments" :key="appt.id">
                                            <td class="ps-3">
                                                <div class="fw-bold">{{ appt.date }}</div>
                                                <small class="text-muted">{{ appt.time }}</small>
                                            </td>
                                            <td><span :class="getStatusBadge(appt.status)">{{ appt.status }}</span></td>
                                            <td>{{ appt.patient_name }}</td>
                                            <td>
                                                <div class="fw-medium">Dr. {{ appt.doctor_name }}</div>
                                                <small class="text-muted">{{ appt.specialization }}</small>
                                            </td>
                                        </tr>
                                        <tr v-if="allAppointments.length === 0">
                                            <td colspan="4" class="text-center py-4 text-muted">No appointments found.</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- History Tab -->
        <div class="tab-pane fade" id="history" role="tabpanel">
            <div class="glass-panel p-4">
                <h4 class="mb-4 fw-bold text-primary">System Activity History</h4>
                
                <div class="mb-4">
                    <div class="row g-3">
                        <div class="col-md-3">
                            <label class="form-label text-muted small fw-bold">FILTER BY TYPE</label>
                            <select class="form-select border-0 bg-light shadow-sm" v-model="historyFilter">
                                <option value="">All Activities</option>
                                <option value="user_registration">User Registrations</option>
                                <option value="appointment_booked">Appointments Booked</option>
                                <option value="appointment_completed">Appointments Completed</option>
                                <option value="user_blocked">Users Blocked/Unblocked</option>
                                <option value="doctor_added">Doctors Added</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label text-muted small fw-bold">DATE FROM</label>
                            <input type="date" class="form-control border-0 bg-light shadow-sm" v-model="historyDateFrom">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label text-muted small fw-bold">DATE TO</label>
                            <input type="date" class="form-control border-0 bg-light shadow-sm" v-model="historyDateTo">
                        </div>
                        <div class="col-md-3 d-flex align-items-end">
                            <button class="btn btn-primary w-100 shadow-sm" @click="fetchSystemHistory">Filter</button>
                        </div>
                    </div>
                </div>

                <div v-if="systemHistory.length > 0" class="timeline">
                    <div v-for="activity in systemHistory" :key="activity.id" class="timeline-item mb-4">
                        <div class="timeline-marker bg-primary"></div>
                        <div class="timeline-content card border-0 shadow-sm">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <div class="d-flex align-items-center">
                                        <span class="badge bg-light text-dark border me-2">{{ activity.type }}</span>
                                        <small class="text-muted">{{ activity.timestamp }}</small>
                                    </div>
                                    <span :class="getActivityIcon(activity.type)" class="fs-5"></span>
                                </div>
                                <p class="mb-1 fw-medium">{{ activity.description }}</p>
                                <small class="text-muted">{{ activity.details }}</small>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-else-if="historyLoaded" class="text-center py-5 text-muted">
                    <div class="display-4 mb-3">📜</div>
                    <p>No system activity found for the selected filters.</p>
                </div>

                <div v-else class="text-center py-5 text-muted opacity-50">
                    <div class="display-4 mb-3">🔄</div>
                    <p>Loading system history...</p>
                </div>
            </div>
        </div>

        <!-- Edit Doctor Modal -->
        <div class="modal fade" id="doctorEditModal" tabindex="-1" ref="doctorEditModal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-header border-0 bg-primary text-white">
                        <h5 class="modal-title fw-bold">Edit Profile</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form @submit.prevent="updateDoctorProfile">
                        <div class="modal-body p-4">
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">FULL NAME</label>
                                <input type="text" class="form-control" v-model="currentEditDoctor.full_name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">SPECIALIZATION</label>
                                <input type="text" class="form-control" v-model="currentEditDoctor.specialization" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">CONTACT INFO</label>
                                <input type="text" class="form-control" v-model="currentEditDoctor.contact_info">
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">BIO</label>
                                <textarea class="form-control" v-model="currentEditDoctor.bio" rows="3"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer border-0 bg-light">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary px-4 fw-bold">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { Modal } from 'bootstrap';

const getToken = () => localStorage.getItem('access_token');

export default {
    name: 'AdminDashboard',
    data() {
        return {
            stats: { total_doctors: 0, total_patients: 0, upcoming_appointments: 0 },
            
            showAddForm: false,
            newDoctor: { username: '', password: '', full_name: '', specialization: '', contact_info: '', bio: '' },
            doctorList: [],
            doctorSearchQuery: '',
            currentEditDoctor: {}, 
            doctorEditModalInstance: null,
            
            searchQuery: '',
            searchResults: [],
            hasSearched: false,
            allAppointments: [],
            
            // History data
            systemHistory: [],
            historyFilter: '',
            historyDateFrom: '',
            historyDateTo: '',
            historyLoaded: false,
        };
    },
    mounted() {
        this.fetchDashboardStats();
        this.fetchDoctors(); 
        if (window.bootstrap && window.bootstrap.Modal) {
             this.doctorEditModalInstance = new window.bootstrap.Modal(this.$refs.doctorEditModal);
        }
    },
    methods: {
        logout() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_role');
            this.$router.push('/login');
        },
        clearDoctorSearchAndRefresh() {
            this.doctorSearchQuery = '';
            this.fetchDoctors();
        },
        clearSearchAndRefresh() {
            this.doctorSearchQuery = '';
            this.searchQuery = '';
            this.searchResults = [];
            this.hasSearched = false;
            this.fetchDoctors();
        },
        getStatusBadge(status) {
            const base = 'badge rounded-pill px-2 py-1 ';
            switch (status) {
                case 'Booked': return base + 'bg-soft-primary text-primary';
                case 'Completed': return base + 'bg-soft-success text-success';
                case 'Cancelled': return base + 'bg-soft-danger text-danger';
                default: return base + 'bg-secondary';
            }
        },
        // --- FIX: Method to trigger full list load on tab click ---
        loadAllUsersForTab() {
            this.searchQuery = ''; 
            this.searchResults = []; 
            this.hasSearched = true;
            this.searchUsers(true);
        },
        // ----------------------------------------------------------
        async fetchDashboardStats() {
            try {
                const response = await fetch('/api/admin/stats', { headers: { 'Authorization': `Bearer ${getToken()}` } });
                if (response.ok) {
                    this.stats = await response.json();
                }
            } catch (error) {
                console.error('Error fetching admin stats:', error);
            }
        },
        async fetchDoctors(query = '') {
             try {
                const response = await fetch(`/api/admin/search?query=${query}`, {
                    headers: { 'Authorization': `Bearer ${getToken()}` },
                });
                if (response.ok) {
                    const allUsers = await response.json();
                    this.doctorList = allUsers.filter(u => u.role === 'Doctor');
                }
            } catch (error) {
                console.error('Error fetching doctors:', error);
            }
        },
        async fetchAllAppointments() {
             try {
                const response = await fetch('/api/admin/appointments', { headers: { 'Authorization': `Bearer ${getToken()}` } });
                if (response.ok) {
                    this.allAppointments = await response.json();
                } else {
                    this.allAppointments = [];
                }
            } catch (error) {
                console.error('Error fetching appointments:', error);
            }
        },
        toggleAddForm() {
            this.showAddForm = !this.showAddForm;
        },
        async submitDoctor() {
            try {
                const response = await fetch('/api/admin/doctors', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.newDoctor)
                });

                if (response.ok) {
                    alert('Doctor added successfully!');
                    this.showAddForm = false;
                    this.newDoctor = { username: '', password: '', full_name: '', specialization: '', contact_info: '', bio: '' }; 
                    this.fetchDashboardStats();
                    this.fetchDoctors(); 
                } else {
                    let errorMessage = 'Registration failed due to server error.';
                    try {
                        const errorData = await response.json();
                        errorMessage = errorData.msg || errorMessage;
                    } catch (e) {
                        errorMessage = `Server responded with status ${response.status} but returned invalid data. Check Flask terminal for traceback.`;
                    }
                    alert(`Error: ${errorMessage}`);
                }
            } catch (error) {
                console.error('Network Error:', error);
                alert('A network connection error occurred. Ensure Flask server is running.');
            }
        },
        // --- DOCTOR EDIT LOGIC ---
        openEditModal(doctor) {
            this.currentEditDoctor = JSON.parse(JSON.stringify(doctor)); 
            if (this.doctorEditModalInstance) this.doctorEditModalInstance.show();
        },
        async updateDoctorProfile() {
            const data = {
                full_name: this.currentEditDoctor.full_name,
                specialization: this.currentEditDoctor.specialization,
                contact_info: this.currentEditDoctor.contact_info,
                bio: this.currentEditDoctor.bio,
            };

            try {
                const response = await fetch(`/api/admin/doctors/${this.currentEditDoctor.id}`, {
                    method: 'PUT',
                    headers: { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert('Doctor profile updated successfully!');
                    if (this.doctorEditModalInstance) this.doctorEditModalInstance.hide();
                    this.fetchDoctors();
                } else {
                    const errorData = await response.json();
                    alert(`Error updating profile: ${errorData.msg}`);
                }
            } catch (error) {
                console.error('Error updating doctor:', error);
                alert('Failed to connect to server.');
            }
        },
        // --- USER SEARCH/BLACKLIST LOGIC ---
        searchDoctors() {
            this.fetchDoctors(this.doctorSearchQuery);
        },
        async searchUsers(isAutoLoad = false) {
            // Only block the manual search if the field is empty and it's NOT an auto-load trigger
            if (!isAutoLoad && !this.searchQuery) return;
            
            const queryToUse = this.searchQuery;

            try {
                const response = await fetch(`/api/admin/search?query=${queryToUse}`, {
                    headers: { 'Authorization': `Bearer ${getToken()}` },
                });
                if (response.ok) {
                    const results = await response.json();
                    // Exclude doctors from the user-management list
                    this.searchResults = results.filter(u => u.role !== 'Doctor');
                    this.hasSearched = true;
                }
            } catch (error) {
                console.error('Error searching users:', error);
            }
        },
        async toggleBlacklist(userId, isActive) {
            const action = isActive ? 'Block' : 'Unblock';
            if (!confirm(`Are you sure you want to ${action} this user?`)) return;

            try {
                const response = await fetch(`/api/admin/users/${userId}/blacklist`, {
                    method: 'PUT',
                    headers: { 'Authorization': `Bearer ${getToken()}` },
                });

                if (response.ok) {
                    alert(`User successfully ${action}ed.`);
                    this.searchUsers(true); // Re-run search/load to refresh status in current tab
                    this.fetchDoctors(); // Refresh doctor list in other tab
                } else {
                    alert('Failed to update status.');
                }
            } catch (error) {
                console.error('Error updating user:', error);
            }
        },
        // --- HISTORY METHODS ---
        async fetchSystemHistory() {
            try {
                this.historyLoaded = false;
                let url = '/api/admin/history';
                const params = new URLSearchParams();
                
                if (this.historyFilter) params.append('type', this.historyFilter);
                if (this.historyDateFrom) params.append('date_from', this.historyDateFrom);
                if (this.historyDateTo) params.append('date_to', this.historyDateTo);
                
                if (params.toString()) url += '?' + params.toString();

                const response = await fetch(url, { headers: { 'Authorization': `Bearer ${getToken()}` } });
                if (response.ok) {
                    this.systemHistory = await response.json();
                } else {
                    this.systemHistory = [];
                }
            } catch (error) {
                console.error('Error fetching system history:', error);
                this.systemHistory = [];
            } finally {
                this.historyLoaded = true;
            }
        },
        getActivityIcon(type) {
            const icons = {
                'user_registration': '👤',
                'appointment_booked': '📅',
                'appointment_completed': '✅',
                'user_blocked': '🚫',
                'doctor_added': '👨‍⚕️'
            };
            return icons[type] || '📝';
        },
    },
};
</script>

<style scoped>
.bg-soft-primary { background-color: rgba(14, 165, 233, 0.1); }
.bg-soft-success { background-color: rgba(16, 185, 129, 0.1); }
.bg-soft-danger { background-color: rgba(239, 68, 68, 0.1); }
.bg-soft-info { background-color: rgba(56, 189, 248, 0.1); }
.bg-soft-warning { background-color: rgba(245, 158, 11, 0.1); }

.btn-soft-danger {
    background-color: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
    border: none;
}
.btn-soft-danger:hover {
    background-color: var(--danger-color);
    color: white;
}

.btn-soft-success {
    background-color: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
    border: none;
}
.btn-soft-success:hover {
    background-color: var(--success-color);
    color: white;
}

.nav-pills .nav-link {
    color: var(--text-secondary);
    border-radius: var(--radius-md);
    padding: 1rem;
    transition: all 0.2s;
}
.nav-pills .nav-link:hover {
    background-color: rgba(14, 165, 233, 0.05);
    color: var(--primary-color);
}
.nav-pills .nav-link.active {
    background-color: var(--primary-color);
    color: white;
    box-shadow: var(--shadow-md);
}

/* Timeline Styles */
.timeline {
    position: relative;
    padding-left: 30px;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 0;
    bottom: 0;
    width: 2px;
    background-color: #e9ecef;
}

.timeline-item {
    position: relative;
    margin-left: 30px;
}

.timeline-marker {
    position: absolute;
    left: -22px;
    top: 20px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 3px solid white;
    box-shadow: 0 0 0 2px #e9ecef;
}

.timeline-content {
    margin-left: 20px;
}
</style>