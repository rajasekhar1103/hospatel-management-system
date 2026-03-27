<template>
    <div class="card shadow-sm doctor-profile-card mb-3">
        <div class="card-body">
            <h5 class="card-title text-success">Dr. {{ doctor.full_name }}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{{ doctor.specialization_name }}</h6>
            
            <p class="card-text small">{{ doctor.bio || 'Detailed profile information is not available.' }}</p>
            
            <div class="availability-info mt-3">
                <strong>Available Slots:</strong>
                <span v-if="doctor.available_times && doctor.available_times.length > 0">
                    <span v-for="time in doctor.available_times" :key="time" class="badge bg-info text-dark me-1">
                        {{ time }}
                    </span>
                </span>
                <span v-else class="text-danger small">
                    Not available today.
                </span>
            </div>

            <slot></slot>
        </div>
    </div>
</template>

<script>
export default {
    name: 'DoctorProfileCard',
    props: {
        // Doctor object passed from parent component (PatientDashboard)
        doctor: {
            type: Object,
            required: true,
        }
    }
};
</script>

<style scoped>
.doctor-profile-card {
    border-left: 5px solid #198754; /* Success color */
}
</style>