<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="app-title">App Name</h1>
      
      <div class="login-form-wrapper">
        <h2 class="login-title">Log in</h2>
        <p class="login-subtitle">Enter your email and password to log in for this app</p>
        
        <form @submit.prevent="login">
          <input 
            v-model="email" 
            type="email"
            placeholder="email@domain.com" 
            required 
            class="input-field"
          />
          <input 
            v-model="password" 
            type="password" 
            placeholder="password" 
            required 
            class="input-field"
          />
          <button type="submit" class="login-button">Log in</button>
        </form>
        
        <div class="divider-container">
          <div class="divider-line"></div>
        </div>
        
        <router-link to="/reset-password" class="forgot-link">Forgot Password?</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { API_BASE_URL } from '../utils/api';
import { setAuthData } from '../utils/auth';
import axios from 'axios';

const email = ref('');
const password = ref('');
const router = useRouter();

const login = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/login`, {
      email: email.value,
      password: password.value
    });
    setAuthData(
      response.data.access_token,
      response.data.role,
      response.data.userId,
      response.data.username
    );
    router.push('/');
  } catch (error) {
    console.error('Login error:', error);
    if (error.response) {
        alert(`Login failed: ${error.response.data.msg || error.response.statusText}`);
    } else {
        alert('Login failed: Network error or server not reachable');
    }
  }
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-secondary);
}

.login-card {
  width: 450px;
  background: var(--card-bg);
  text-align: center;
  padding: 60px 50px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-title {
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 100px;
  color: var(--text-primary);
}

.login-form-wrapper {
  width: 100%;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.login-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 40px;
  line-height: 1.5;
}

form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.input-field {
  width: 100%;
  padding: 14px 18px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 15px;
  color: var(--text-primary);
  background: var(--card-bg);
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.input-field::placeholder {
  color: var(--text-secondary);
}

.input-field:focus {
  outline: none;
  border-color: var(--text-primary);
}

.login-button {
  width: 100%;
  padding: 14px;
  background: #000;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 8px;
}

.login-button:hover {
  background: #333;
}

.divider-container {
  margin: 40px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.divider-line {
  width: 2px;
  height: 50px;
  background: var(--border-color);
}

.forgot-link {
  display: inline-block;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: opacity 0.2s;
}

.forgot-link:hover {
  opacity: 0.7;
}
</style>
