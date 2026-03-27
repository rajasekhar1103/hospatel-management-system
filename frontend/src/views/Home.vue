<template>
    <div class="home-container">
        <div class="hero-overlay"></div>
        <div class="content-wrapper text-center text-white">
            <h1 class="main-title mb-4 animate-fade-in">Hospital Management System</h1>
            <p class="subtitle mb-5 animate-fade-in delay-100">Excellence in Healthcare, Simplified.</p>
            
            <div class="action-buttons animate-fade-in delay-200">
                <router-link to="/login" class="btn btn-primary btn-lg px-5 rounded-pill shadow-lg me-3 hover-lift">Login</router-link>
                <router-link to="/register" class="btn btn-outline-light btn-lg px-5 rounded-pill hover-lift">Register</router-link>
            </div>
        </div>

        <footer class="simple-footer text-white-50">
            <p>&copy; 2025 HMS. All rights reserved.</p>
        </footer>
    </div>
</template>

<script>
export default {
    name: 'Home',
};
</script>

<style scoped>
.home-container {
    position: relative;
    height: 100vh;
    width: 100%;
    background: url('@/assets/hospital_hero.png') no-repeat center center/cover;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.8) 100%);
    z-index: 1;
}

.content-wrapper {
    position: relative;
    z-index: 2;
    padding: 2rem;
    max-width: 800px;
}

.main-title {
    font-size: 4rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 1.5rem;
    background: linear-gradient(to right, #fff, #94a3b8);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    font-size: 1.5rem;
    font-weight: 300;
    opacity: 0.9;
    letter-spacing: 0.5px;
}

.action-buttons .btn {
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
}

.hover-lift:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
}

.simple-footer {
    position: absolute;
    bottom: 20px;
    width: 100%;
    text-align: center;
    z-index: 2;
    font-size: 0.9rem;
}

/* Animations */
.animate-fade-in {
    opacity: 0;
    animation: fadeIn 1s ease-out forwards;
    transform: translateY(20px);
}

.delay-100 { animation-delay: 0.2s; }
.delay-200 { animation-delay: 0.4s; }

@keyframes fadeIn {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 768px) {
    .main-title {
        font-size: 2.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
    }
    .action-buttons {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .action-buttons .btn {
        width: 100%;
        margin-right: 0 !important;
    }
}
</style>