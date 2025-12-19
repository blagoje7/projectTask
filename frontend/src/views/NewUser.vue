<template>
  <div class="new-user-container">
    <div class="header">
      <h1>Create New User</h1>
      <p class="subtitle">Add a new user to the system</p>
    </div>

    <div class="form-card">
      <form @submit.prevent="createUser">
        <div class="form-group">
          <label for="email">Email Address *</label>
          <input 
            id="email"
            v-model="email" 
            type="email"
            placeholder="user@example.com" 
            required 
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="firstName">First Name</label>
            <input 
              id="firstName"
              v-model="firstName" 
              type="text"
              placeholder="John" 
            />
          </div>

          <div class="form-group">
            <label for="lastName">Last Name</label>
            <input 
              id="lastName"
              v-model="lastName" 
              type="text"
              placeholder="Doe" 
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">Password *</label>
          <input 
            id="password"
            v-model="password" 
            type="password" 
            placeholder="Enter secure password" 
            required 
          />
        </div>

        <div class="form-group">
          <label for="role">Role *</label>
          <select id="role" v-model="role">
            <option value="user">User</option>
            <option value="manager">Manager</option>
            <option value="admin">Administrator</option>
          </select>
        </div>

        <div class="form-actions">
          <button type="submit" class="primary">
            Create User
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { apiPost } from '../utils/api';

const email = ref('');
const firstName = ref('');
const lastName = ref('');
const password = ref('');
const role = ref('user');

const createUser = async () => {
  try {
    await apiPost('/users', {
      email: email.value,
      firstName: firstName.value,
      lastName: lastName.value,
      password: password.value,
      role: role.value
    });
    alert('User created');
  } catch (error) {
    console.error('Create user error:', error);
    if (error.response) {
        alert(`Error creating user: ${error.response.data.msg || error.response.statusText}`);
    } else {
        alert('Error creating user: Network error or server not reachable');
    }
  }
};
</script>

<style scoped>
.new-user-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 30px;
}

.header h1 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-size: 24px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

.form-card {
  background: var(--card-bg);
  padding: 30px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-primary);
}

.form-group input,
.form-group select {
  width: 100%;
  box-sizing: border-box;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.form-actions button {
  min-width: 140px;
  padding: 10px 24px;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }
}
</style>