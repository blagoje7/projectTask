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
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-tertiary: #e0e0e0;
  --text-primary: #000000;
  --text-secondary: #666666;
  --border-color: #e0e0e0;
  --nav-bg: #eeeeee;
  --card-bg: #ffffff;
  --hover-bg: #f5f5f5;
  --modal-overlay: rgba(0, 0, 0, 0.5);
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.2);
}

[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --bg-tertiary: #404040;
  --text-primary: #ffffff;
  --text-secondary: #b0b0b0;
  --border-color: #404040;
  --nav-bg: #2d2d2d;
  --card-bg: #2d2d2d;
  --hover-bg: #404040;
  --modal-overlay: rgba(0, 0, 0, 0.8);
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
}

* {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

#app {
  background: var(--bg-primary);
  min-height: 100vh;
}

nav {
  padding: 1rem;
  background: var(--nav-bg);
  border-bottom: 1px solid var(--border-color);
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

nav a {
  margin: 0 0.5rem;
  color: var(--text-primary);
  text-decoration: none;
}

nav a:hover {
  text-decoration: underline;
}

nav a.router-link-active {
  font-weight: bold;
}

nav button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

nav button:hover {
  background: var(--hover-bg);
}

.theme-toggle {
  font-size: 20px;
  padding: 0.5rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.theme-toggle:hover {
  background: var(--hover-bg);
  transform: scale(1.1);
}
</style>
