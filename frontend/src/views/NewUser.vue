<template>
  <div>
    <h1>New User</h1>
    <p>Create a new user (Admin only)</p>
    <form @submit.prevent="createUser">
      <input v-model="email" placeholder="Email" required />
      <input v-model="firstName" placeholder="First Name" />
      <input v-model="lastName" placeholder="Last Name" />
      <input v-model="password" type="password" placeholder="Password" required />
      <select v-model="role">
        <option value="user">User</option>
        <option value="manager">Manager</option>
        <option value="admin">Administrator</option>
      </select>
      <button type="submit">Create</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const email = ref('');
const firstName = ref('');
const lastName = ref('');
const password = ref('');
const role = ref('user');

const createUser = async () => {
  try {
    const token = localStorage.getItem('token');
    await axios.post('http://localhost:5000/users', {
      email: email.value,
      firstName: firstName.value,
      lastName: lastName.value,
      password: password.value,
      role: role.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
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


form {
  display: flex;
  flex-direction: column;
  gap: 10px;

}

input, select {
  padding: 8px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

</style>