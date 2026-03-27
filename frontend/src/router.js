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
    { path: '/admin/dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'Admin' } },
    { path: '/doctor/dashboard', name: 'DoctorDashboard', component: DoctorDashboard, meta: { requiresAuth: true, role: 'Doctor' } },
    { path: '/patient/dashboard', name: 'PatientDashboard', component: PatientDashboard, meta: { requiresAuth: true, role: 'Patient' } },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach((to, from, next) => {
    const isAuthenticated = localStorage.getItem('access_token')
    const userRole = localStorage.getItem('user_role') 

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login') 
    } else if (to.meta.role && userRole !== to.meta.role) {
        // Redirect if user role doesn't match
        next('/') 
    } else {
        next()
    }
})

export default router