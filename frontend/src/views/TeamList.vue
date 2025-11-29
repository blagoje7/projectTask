<template>
  <div class="team-management">
    <h1>Team Management</h1>
    
    <div class="create-team">
      <h2>Create New Team</h2>
      <div class="form-group">
        <input v-model="newTeamName" placeholder="Team Name" required />
        <button @click="createTeam" :disabled="!newTeamName">Create Team</button>
      </div>
    </div>
    
    <hr />
    
    <div class="teams-list">
      <h2>Existing Teams</h2>
      <div v-if="teams.length === 0" class="no-teams">
        <p>No teams yet. Create your first team above!</p>
      </div>
      <div v-else class="team-card" v-for="team in teams" :key="team.teamId">
        <h3>{{ team.name }}</h3>
        <div class="team-actions">
          <router-link :to="'/teams/' + team.teamId" class="btn-primary">Manage Members</router-link>
          <button @click="deleteTeam(team.teamId)" class="btn-danger">Delete Team</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const teams = ref([]);
const newTeamName = ref('');

const fetchTeams = async () => {
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get('http://localhost:5001/teams', {
      headers: { Authorization: `Bearer ${token}` }
    });
    teams.value = response.data;
  } catch (error) {
    console.error(error);
    alert('Error loading teams');
  }
};

const createTeam = async () => {
  if (!newTeamName.value.trim()) {
    alert('Please enter a team name');
    return;
  }
  
  const token = localStorage.getItem('token');
  try {
    await axios.post('http://localhost:5001/teams', {
      name: newTeamName.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    newTeamName.value = '';
    alert('Team created successfully!');
    fetchTeams();
  } catch (error) {
    console.error(error);
    alert(error.response?.data?.msg || 'Error creating team');
  }
};

const deleteTeam = async (id) => {
  if (!confirm('Are you sure you want to delete this team?')) return;
  
  const token = localStorage.getItem('token');
  try {
    await axios.delete(`http://localhost:5001/teams/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    alert('Team deleted successfully!');
    fetchTeams();
  } catch (error) {
    console.error(error);
    alert(error.response?.data?.msg || 'Error deleting team');
  }
};

onMounted(fetchTeams);
</script>

<style scoped>
.team-management {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.create-team {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.form-group input {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  background: var(--card-bg);
  color: var(--text-primary);
}

.form-group button {
  padding: 10px 20px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.form-group button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.form-group button:hover:not(:disabled) {
  background: #359268;
}

.teams-list {
  margin-top: 20px;
}

.no-teams {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.team-card {
  border: 1px solid var(--border-color);
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 8px;
  background: var(--card-bg);
}

.team-card h3 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
}

.team-actions {
  display: flex;
  gap: 10px;
}

.btn-primary, .btn-danger {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  font-size: 14px;
  display: inline-block;
}

.btn-primary {
  background: #42b983;
  color: white;
}

.btn-primary:hover {
  background: #359268;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

hr {
  margin: 30px 0;
  border: none;
  border-top: 1px solid var(--border-color);
}
</style>
