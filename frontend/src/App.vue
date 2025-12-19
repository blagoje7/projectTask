<template>
  <div :class="{ 'dark-mode': isDarkMode }">
    <nav v-if="$route.path !== '/login' && $route.path !== '/reset-password'">
      <div class="nav-content">
        <div class="nav-links">
          <router-link to="/">Home</router-link> |
          <router-link to="/projects">Projects</router-link> |
          <span v-if="role === 'admin'">
            <router-link to="/newUser">New User</router-link> |
            <router-link to="/users">Manage Users</router-link> |
            <router-link to="/teams">Manage Teams</router-link> |
          </span>
          <span v-if="role === 'manager'">
            <router-link to="/teams">Manage Teams</router-link> |
          </span>
          <button @click="logout">Logout</button>
        </div>
        <button @click="toggleTheme" class="theme-toggle" :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
          {{ isDarkMode ? '☀️' : '🌙' }}
        </button>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { getUserRole, clearAuthData } from './utils/auth';
import { isAdmin, isManager } from './utils/auth';

const router = useRouter();
const route = useRoute();
const role = ref(getUserRole());
const isDarkMode = ref(localStorage.getItem('theme') === 'dark');

watch(route, () => {
  role.value = getUserRole();
});

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', isDarkMode.value ? 'dark' : 'light');
};

const logout = () => {
  clearAuthData();
  router.push('/login');
};

onMounted(() => {
  document.documentElement.setAttribute('data-theme', isDarkMode.value ? 'dark' : 'light');
});
</script>

<style>
:root {
  /* Jira Light Theme */
  --bg-primary: #ffffff;
  --bg-secondary: #F4F5F7; /* Jira Light Gray */
  --bg-tertiary: #EBECF0;
  --text-primary: #172B4D; /* Jira Dark Blue Text */
  --text-secondary: #5E6C84;
  --border-color: #DFE1E6;
  --nav-bg: #ffffff;
  --card-bg: #ffffff;
  --hover-bg: #EBECF0;
  --modal-overlay: rgba(9, 30, 66, 0.54);
  
  /* Brand Colors */
  --primary-color: #0052CC;
  --primary-hover: #0065FF;
  --success-color: #36B37E;
  --warning-color: #FFAB00;
  --danger-color: #FF5630;
  --info-color: #42526E;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(9, 30, 66, 0.25);
  --shadow-md: 0 3px 6px rgba(9, 30, 66, 0.25);
  --shadow-lg: 0 8px 16px -4px rgba(9, 30, 66, 0.25);
}

[data-theme="dark"] {
  /* Jira Dark Theme */
  --bg-primary: #1D2125;
  --bg-secondary: #22272B; /* Jira Dark Gray */
  --bg-tertiary: #2C333A;
  --text-primary: #B6C2CF;
  --text-secondary: #8C9BAB;
  --border-color: #454F59;
  --nav-bg: #1D2125;
  --card-bg: #22272B;
  --hover-bg: #2C333A;
  --modal-overlay: rgba(0, 0, 0, 0.7);

  /* Brand Colors (Adjusted for Dark Mode) */
  --primary-color: #579DFF;
  --primary-hover: #85B8FF;
  --success-color: #6CC9A6;
  --warning-color: #F5CD47;
  --danger-color: #FF8F73;
  --info-color: #A1BDD9;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.5);
  --shadow-md: 0 3px 6px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 8px 16px -4px rgba(0, 0, 0, 0.5);
}

* {
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  background: var(--bg-primary);
  min-height: 100vh;
}

/* Navigation Styles */
nav {
  background-color: var(--nav-bg);
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
  height: 56px;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-content {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-links a {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 3px;
  transition: all 0.2s;
}

.nav-links a:hover {
  background-color: var(--bg-tertiary);
  color: var(--primary-color);
}

.nav-links a.router-link-active {
  color: var(--primary-color);
  background-color: var(--bg-secondary);
}

.nav-links button {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  padding: 8px 12px;
  font-size: 14px;
}

.nav-links button:hover {
  color: var(--danger-color);
  background-color: var(--bg-tertiary);
  border-radius: 3px;
}

.theme-toggle {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}

.theme-toggle:hover {
  background-color: var(--bg-tertiary);
}
</style>
