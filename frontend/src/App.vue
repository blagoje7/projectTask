<template>
  <nav v-if="$route.path !== '/login' && $route.path !== '/reset-password'">
    <router-link to="/">Home</router-link> |
    <router-link to="/projects">Projects</router-link> |
    <router-link to="/my-tasks">My Tasks</router-link> |
    <span v-if="role === 'admin'">
      <router-link to="/newUser">New User</router-link> |
      <router-link to="/users">Manage Users</router-link> |
      <router-link to="/teams">Manage Teams</router-link> |
    </span>
    <span v-if="role === 'manager'">
      <router-link to="/teams">Manage Teams</router-link> |
    </span>
    <button @click="logout">Logout</button>
  </nav>
  <router-view />
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const role = ref(localStorage.getItem('role'));

watch(route, () => {
  role.value = localStorage.getItem('role');
});

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  router.push('/login');
};
</script>

<style>
nav {
  padding: 1rem;
  background: #eee;
}
nav a {
  margin: 0 0.5rem;
}
</style>
