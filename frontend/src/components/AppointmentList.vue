<template>
    <div class="appointment-list mt-3">
        <div v-if="appointments.length === 0" class="alert alert-light">
            No appointments found for this view.
        </div>
        <ul v-else class="list-group">
            <li v-for="appt in appointments" :key="appt.id" 
                :class="['list-group-item d-flex justify-content-between align-items-center', getStatusClass(appt.status)]">
                
                <div class="appointment-details">
                    <h6 class="mb-1">
                        {{ appt.date }} at {{ appt.time }}
                    </h6>
                    <small v-if="role === 'Admin' || role === 'Doctor'">
                        Patient: **{{ appt.patient_name || appt.patient_id }}**
                    </small>
                    <small v-else-if="role === 'Patient'">
                        Doctor: **Dr. {{ appt.doctor_name || appt.doctor_id }}**
                    </small>
                </div>

                <div class="appointment-status">
                    <span :class="['badge', getBadgeClass(appt.status), 'me-2']">
                        {{ appt.status }}
                    </span>
                    <slot :appointment="appt"></slot>
                </div>
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    name: 'AppointmentList',
    props: {
        // Array of appointment objects
        appointments: {
            type: Array,
            required: true,
        },
        // Role of the user viewing the list ('Admin', 'Doctor', 'Patient')
        role: {
            type: String,
            required: true,
        }
    },
    methods: {
        getBadgeClass(status) {
            switch (status) {
                case 'Booked':
                    return 'bg-primary';
                case 'Completed':
                    return 'bg-success';
                case 'Cancelled':
                    return 'bg-danger';
                default:
                    return 'bg-secondary';
            }
        },
        getStatusClass(status) {
            // Optional styling for list item based on status
            if (status === 'Completed') return 'list-group-item-success';
            if (status === 'Cancelled') return 'list-group-item-danger';
            return '';
        }
    },
};
</script>