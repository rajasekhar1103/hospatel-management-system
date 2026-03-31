<template>
    <div class="review-form-container mt-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Rate & Review Doctor</h5>
            </div>
            <div class="card-body">
                <div v-if="successMessage" class="alert alert-success alert-dismissible fade show">
                    {{ successMessage }}
                    <button type="button" class="btn-close" @click="successMessage = ''"></button>
                </div>

                <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show">
                    {{ errorMessage }}
                    <button type="button" class="btn-close" @click="errorMessage = ''"></button>
                </div>

                <div class="mb-3">
                    <label for="doctor-select" class="form-label">Select Doctor</label>
                    <select 
                        id="doctor-select"
                        v-model="selectedDoctorId" 
                        class="form-select"
                        @change="loadDoctorInfo"
                    >
                        <option value="">Choose a doctor...</option>
                        <option v-for="doctor in completedDoctors" :key="doctor.id" :value="doctor.id">
                            Dr. {{ doctor.doctor_name }} - {{ doctor.specialization }}
                        </option>
                    </select>
                </div>

                <div v-if="selectedDoctorId" class="mb-3">
                    <label for="rating" class="form-label">Rating (Stars)</label>
                    <div class="rating-input">
                        <span 
                            v-for="star in 5" 
                            :key="star"
                            @click="rating = star"
                            @mouseover="hoverRating = star"
                            @mouseleave="hoverRating = 0"
                            :class="['star', { filled: star <= (hoverRating || rating) }]"
                        >
                            ★
                        </span>
                        <span class="ms-2">{{ rating || hoverRating || 0 }} / 5</span>
                    </div>
                </div>

                <div v-if="selectedDoctorId" class="mb-3">
                    <label for="comment" class="form-label">Comment (Optional)</label>
                    <textarea
                        id="comment"
                        v-model="comment"
                        class="form-control"
                        rows="4"
                        placeholder="Share your experience with this doctor..."
                        maxlength="500"
                    ></textarea>
                    <small class="text-muted">{{ comment.length }}/500</small>
                </div>

                <button 
                    v-if="selectedDoctorId && rating > 0"
                    @click="submitReview"
                    :disabled="isSubmitting"
                    class="btn btn-primary"
                >
                    <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
                    {{ isSubmitting ? 'Submitting...' : 'Submit Review' }}
                </button>
                <button 
                    v-if="!selectedDoctorId || rating === 0"
                    disabled
                    class="btn btn-secondary"
                >
                    Select Doctor & Rating
                </button>
            </div>
        </div>

        <div v-if="reviews.length > 0" class="mt-4">
            <h5>My Reviews</h5>
            <div v-for="review in reviews" :key="review.id" class="card mb-2">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h6 class="card-title">Dr. {{ review.doctor_name }}</h6>
                            <div class="stars-display">
                                <span v-for="s in review.rating" :key="s" class="star-filled">★</span>
                                <span v-for="s in (5 - review.rating)" :key="'empty-' + s" class="star-empty">☆</span>
                            </div>
                        </div>
                        <small class="text-muted">{{ formatDate(review.created_at) }}</small>
                    </div>
                    <p class="card-text mt-2">{{ review.comment }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'ReviewForm',
    data() {
        return {
            selectedDoctorId: '',
            rating: 0,
            hoverRating: 0,
            comment: '',
            isSubmitting: false,
            successMessage: '',
            errorMessage: '',
            completedDoctors: [],
            reviews: []
        };
    },
    mounted() {
        this.loadCompletedDoctors();
        this.loadMyReviews();
    },
    methods: {
        async loadCompletedDoctors() {
            try {
                const response = await fetch('/api/patient/history', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                const data = await response.json();
                
                // Get unique doctors from completed appointments
                const doctorMap = new Map();
                data.forEach(appt => {
                    if (appt.status === 'Completed' && !doctorMap.has(appt.doctor_name)) {
                        doctorMap.set(appt.doctor_name, {
                            id: appt.id, // This needs to be doctor_id ideally
                            doctor_name: appt.doctor_name,
                            specialization: appt.specialization
                        });
                    }
                });
                this.completedDoctors = Array.from(doctorMap.values());
            } catch (error) {
                console.error('Error loading completed doctors:', error);
            }
        },
        async loadMyReviews() {
            try {
                const response = await fetch('/api/patient/my-reviews', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                if (response.ok) {
                    this.reviews = await response.json();
                }
            } catch (error) {
                console.error('Error loading reviews:', error);
            }
        },
        async submitReview() {
            if (!this.selectedDoctorId || this.rating === 0) {
                this.errorMessage = 'Please select a doctor and rating';
                return;
            }

            this.isSubmitting = true;
            this.errorMessage = '';
            this.successMessage = '';

            try {
                const response = await fetch('/api/patient/review', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify({
                        doctor_id: parseInt(this.selectedDoctorId),
                        rating: this.rating,
                        comment: this.comment
                    })
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.successMessage = data.msg || 'Review submitted successfully!';
                    this.selectedDoctorId = '';
                    this.rating = 0;
                    this.comment = '';
                    this.loadMyReviews();
                } else {
                    this.errorMessage = data.msg || 'Failed to submit review';
                }
            } catch (error) {
                this.errorMessage = 'Error submitting review: ' + error.message;
            } finally {
                this.isSubmitting = false;
            }
        },
        formatDate(dateStr) {
            return new Date(dateStr).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }
    }
};
</script>

<style scoped>
.review-form-container {
    max-width: 600px;
}

.rating-input {
    font-size: 2rem;
}

.star {
    cursor: pointer;
    color: #ddd;
    margin-right: 0.5rem;
    transition: color 0.2s;
    user-select: none;
}

.star.filled {
    color: #ffc107;
}

.star:hover {
    color: #ffc107;
}

.stars-display .star-filled {
    color: #ffc107;
    font-size: 1rem;
}

.stars-display .star-empty {
    color: #ddd;
    font-size: 1rem;
}

textarea {
    resize: vertical;
}
</style>
