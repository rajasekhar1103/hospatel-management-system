<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4 shadow-sm">
      <div class="container">
        <router-link class="navbar-brand" to="/">🏥 HMS Portal</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">Register</router-link>
            </li>
            <li class="nav-item">
               <a class="nav-link cursor-pointer" @click="logout" v-if="isLoggedIn">Logout</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      // simple check to see if user is logged in based on token existence
      isLoggedIn: !!localStorage.getItem('access_token')
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      this.isLoggedIn = false;
      this.$router.push('/login');
    }
  },
  // Listen for route changes to update the navbar state
  watch: {
    $route(to, from) {
      this.isLoggedIn = !!localStorage.getItem('access_token');
    }
  }
}
</script>

<style>
/* Global styles */
body {
  background-color: #f8f9fa; /* Light grey background */
  min-height: 100vh;
}
.cursor-pointer {
  cursor: pointer;
}
</style>