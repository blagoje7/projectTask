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
import axios from 'axios';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const router = useRouter();

const login = async () => {
  try {
    const response = await axios.post('http://localhost:5000/login', {
      email: email.value,
      password: password.value
    });
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('role', response.data.role);
    localStorage.setItem('userId', response.data.userId);
    localStorage.setItem('username', response.data.username);
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
  background-color: #f5f5f5;
}

.login-card {
  width: 450px;
  background: white;
  text-align: center;
  padding: 60px 50px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-title {
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 100px;
  color: #000;
}

.login-form-wrapper {
  width: 100%;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #000;
}

.login-subtitle {
  font-size: 15px;
  color: #666;
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
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 15px;
  color: #333;
  background: white;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.input-field::placeholder {
  color: #999;
}

.input-field:focus {
  outline: none;
  border-color: #000;
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
  background: #e0e0e0;
}

.forgot-link {
  display: inline-block;
  color: #000;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: opacity 0.2s;
}

.forgot-link:hover {
  opacity: 0.7;
}
</style>
