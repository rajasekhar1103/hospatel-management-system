<template>
    <div class="container-fluid vh-100">
        <div class="row h-100">
            <!-- Left Side: Hero Image -->
            <div class="col-md-6 d-none d-md-block p-0 position-relative overflow-hidden">
                <img src="@/assets/hospital_hero.png" alt="Hospital" class="img-fluid h-100 w-100 object-fit-cover fade-in">
                <div class="position-absolute top-0 start-0 w-100 h-100 bg-dark opacity-25"></div>
                <div class="position-absolute bottom-0 start-0 p-5 text-white fade-in" style="z-index: 2;">
                    <h1 class="display-4 fw-bold mb-3">Join Us Today</h1>
                    <p class="lead">Create your patient account to book appointments and manage your health records.</p>
                </div>
            </div>

            <!-- Right Side: Registration Form -->
            <div class="col-md-6 d-flex align-items-center justify-content-center bg-light overflow-auto">
                <div class="w-75 mw-500 fade-in py-5" style="animation-delay: 0.2s;">
                    <div class="text-center mb-4">
                        <h2 class="fw-bold text-primary">Create Account</h2>
                        <p class="text-muted">Fill in your details to register</p>
                    </div>

                    <form @submit.prevent="handleRegister" class="glass-panel p-4 p-md-5 bg-white shadow-lg border-0">
                        
                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="username" v-model="formData.username" placeholder="Username" required>
                            <label for="username">Username</label>
                        </div>
                        
                        <div class="form-floating mb-3">
                            <input type="password" class="form-control" id="password" v-model="formData.password" placeholder="Password" required>
                            <label for="password">Password</label>
                        </div>

                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="full_name" v-model="formData.full_name" placeholder="Full Name" required>
                            <label for="full_name">Full Name</label>
                        </div>

                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="contact_info" v-model="formData.contact_info" placeholder="Contact Info" required>
                            <label for="contact_info">Contact Information</label>
                        </div>

                        <div class="form-floating mb-4">
                            <textarea class="form-control" id="address" v-model="formData.address" placeholder="Address" style="height: 100px"></textarea>
                            <label for="address">Address</label>
                        </div>
                        
                        <button type="submit" class="btn btn-success w-100 py-3 mb-3 fw-bold text-uppercase letter-spacing-1">
                            Register
                        </button>
                        
                        <div class="text-center">
                            <span class="text-muted">Already have an account? </span>
                            <router-link to="/login" class="text-decoration-none fw-bold text-accent">Login here</router-link>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import router from '../router';

export default {
    name: 'PatientRegister',
    data() {
        return {
            formData: {
                username: '',
                password: '',
                full_name: '',
                contact_info: '',
                address: '',
            },
        };
    },
    methods: {
        async handleRegister() {
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.formData),
                });

                if (response.ok) {
                    alert('Registration successful! Please log in.');
                    router.push('/login');
                } else {
                    const errorData = await response.json();
                    alert(`Registration failed: ${errorData.msg || 'Username may already exist.'}`);
                }
            } catch (error) {
                console.error('Registration error:', error);
                alert('An error occurred during registration.');
            }
        },
    },
};
</script>

<style scoped>
.object-fit-cover {
    object-fit: cover;
}
.mw-500 {
    max-width: 500px;
}
.letter-spacing-1 {
    letter-spacing: 1px;
}
.text-accent {
    color: var(--accent-color);
}
</style>