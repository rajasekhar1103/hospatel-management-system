<template>
    <div class="card shadow-sm doctor-profile-card mb-3">
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h5 class="card-title text-success">Dr. {{ doctor.name || doctor.full_name }}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">{{ doctor.specialization }}</h6>
                </div>
                <div class="rating-badge" v-if="doctor.rating">
                    <span class="stars">★</span> {{ doctor.rating }}/5
                    <small class="text-muted">({{ doctor.review_count }} reviews)</small>
                </div>
            </div>
            
            <p class="card-text small">{{ doctor.bio || 'Detailed profile information is not available.' }}</p>
            
            <div class="availability-info mt-3">
                <strong>Available Slots:</strong>
                <span v-if="doctor.slots && doctor.slots.length > 0">
                    <span v-for="time in doctor.slots" :key="time" class="badge bg-info text-dark me-1">
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

.rating-badge {
    background-color: #fff3cd;
    padding: 0.5rem 0.75rem;
    border-radius: 0.25rem;
    font-weight: bold;
    color: #856404;
}

.stars {
    color: #ffc107;
    font-size: 1.2rem;
}
</style>