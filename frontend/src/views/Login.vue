<template>
    <div class="container-fluid vh-100">
        <div class="row h-100">
            <!-- Left Side: Hero Image -->
            <div class="col-md-6 d-none d-md-block p-0 position-relative overflow-hidden">
                <img src="@/assets/hospital_hero.png" alt="Hospital" class="img-fluid h-100 w-100 object-fit-cover fade-in">
                <div class="position-absolute top-0 start-0 w-100 h-100 bg-dark opacity-25"></div>
                <div class="position-absolute bottom-0 start-0 p-5 text-white fade-in" style="z-index: 2;">
                    <h1 class="display-4 fw-bold mb-3">Welcome Back</h1>
                    <p class="lead">Manage your hospital operations efficiently and securely.</p>
                </div>
            </div>

            <!-- Right Side: Login Form -->
            <div class="col-md-6 d-flex align-items-center justify-content-center bg-light">
                <div class="w-75 mw-400 fade-in" style="animation-delay: 0.2s;">
                    <div class="text-center mb-5">
                        <h2 class="fw-bold text-primary">HMS Portal</h2>
                        <p class="text-muted">Sign in to your account</p>
                    </div>

                    <form @submit.prevent="handleLogin" class="glass-panel p-4 p-md-5 bg-white shadow-lg border-0">
                        <div v-if="errorMessage" class="alert alert-danger mb-3">
                            {{ errorMessage }}
                        </div>
                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="username" v-model="username" placeholder="Username" required>
                            <label for="username">Username</label>
                        </div>
                        <div class="form-floating mb-4">
                            <input type="password" class="form-control" id="password" v-model="password" placeholder="Password" required>
                            <label for="password">Password</label>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100 py-3 mb-3 fw-bold text-uppercase letter-spacing-1">
                            Sign In
                        </button>
                        
                        <div class="text-center">
                            <span class="text-muted">Don't have an account? </span>
                            <router-link to="/register" class="text-decoration-none fw-bold text-accent">Register here</router-link>
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
    data() {
        return {
            username: '',
            password: '',
            errorMessage: ''
        };
    },
    methods: {
        async handleLogin() {
            this.errorMessage = '';
            try {
                console.log('Attempting login for:', this.username);
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: this.username, password: this.password }),
                });

                console.log('Login response status:', response.status);

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('user_role', data.role); 
                    
                    if (data.role === 'Admin') router.push('/admin/dashboard');
                    else if (data.role === 'Doctor') router.push('/doctor/dashboard');
                    else if (data.role === 'Patient') router.push('/patient/dashboard');

                } else {
                    const data = await response.json();
                    this.errorMessage = data.msg || 'Login failed. Check credentials.';
                }
            } catch (error) {
                console.error('Login error:', error);
                this.errorMessage = `Network/System Error: ${error.message}`;
            }
        },
    },
};
</script>

<style scoped>
.object-fit-cover {
    object-fit: cover;
}
.mw-400 {
    max-width: 450px;
}
.letter-spacing-1 {
    letter-spacing: 1px;
}
.text-accent {
    color: var(--accent-color);
}
</style>