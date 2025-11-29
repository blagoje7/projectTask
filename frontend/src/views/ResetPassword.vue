<template>
  <div class="reset-password">
    <h1>Reset Password</h1>
    <form @submit.prevent="requestReset">
      <input v-model="email" placeholder="Enter your email" required />
      <button type="submit">Reset Password</button>
    </form>
    <router-link to="/login" class="back-link">Back to Login</router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { API_BASE_URL } from '../utils/api';
import axios from 'axios';

const router = useRouter();
const email = ref('');

const requestReset = async () => {
  const userEmail = email.value;
  
  // First, check if user exists
  try {
    const response = await axios.post(`${API_BASE_URL}/reset-password`, {
      email: userEmail
    });
    
    if (response.status === 200) {
      // Prompt for new password
      const newPassword = prompt(`Enter new password for ${userEmail}:`);
      
      if (newPassword && newPassword.length >= 6) {
        // Confirm password
        const confirmPassword = prompt('Confirm new password:');
        
        if (newPassword === confirmPassword) {
          // Update password
          await axios.post(`${API_BASE_URL}/update-password`, {
            email: userEmail,
            newPassword: newPassword
          });
          
          alert('Password reset successfully! Please login with your new password.');
          router.push('/login');
        } else {
          alert('Passwords do not match!');
        }
      } else {
        alert('Password must be at least 6 characters long!');
      }
    }
  } catch (error) {
    if (error.response?.status === 404) {
      alert('Email not found!');
    } else {
      alert('Error resetting password');
    }
  }
};
</script>

<style scoped>
.reset-password {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

input {
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 10px;
  background: #000000;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

button:hover {
  background: #0000004f;
}

.back-link {
  color: #000000;
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}
</style>
