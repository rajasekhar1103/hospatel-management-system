import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import DoctorDashboard from './components/DoctorDashboard.vue'
import PatientDashboard from './components/PatientDashboard.vue'

const routes = [
    { path: '/', name: 'Home', component: Home },
    { path: '/login', name: 'Login', component: Login },
    { path: '/register', name: 'Register', component: Register },
    { 
        path: '/admin/dashboard', 
        name: 'AdminDashboard', 
        component: AdminDashboard, 
        meta: { requiresAuth: true, role: 'Admin' } 
    },
    { 
        path: '/doctor/dashboard', 
        name: 'DoctorDashboard', 
        component: DoctorDashboard, 
        meta: { requiresAuth: true, role: 'Doctor' } 
    },
    { 
        path: '/patient/dashboard', 
        name: 'PatientDashboard', 
        component: PatientDashboard, 
        meta: { requiresAuth: true, role: 'Patient' } 
    },
    // Default 404 route (must be last)
    { 
        path: '/:pathMatch(.*)*', 
        name: 'NotFound',
        component: { 
            template: `
                <div class="not-found-container" style="text-align: center; padding: 50px;">
                    <h1>404 - Page Not Found</h1>
                    <p>The page you're looking for doesn't exist.</p>
                    <router-link to="/" style="color: #0066cc; text-decoration: none;">
                        ← Go back to home
                    </router-link>
                </div>
            `
        }
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

/**
 * Global navigation guard for authentication and authorization
 */
router.beforeEach((to, from, next) => {
    const isAuthenticated = localStorage.getItem('access_token')
    const userRole = localStorage.getItem('user_role')

    // Check if route requires authentication
    if (to.meta.requiresAuth && !isAuthenticated) {
        // Redirect to login if not authenticated
        next('/login') 
    } 
    // Check if user role matches required role
    else if (to.meta.role && userRole !== to.meta.role) {
        // Redirect to home if role doesn't match
        next('/') 
    } 
    // Allow navigation
    else {
        next()
    }
})

export default router