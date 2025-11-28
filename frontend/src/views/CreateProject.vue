<template>
  <div class="create-project">
    <h1>Create New Project</h1>
    
    <form @submit.prevent="createProject" class="project-form">
      <div class="form-group">
        <label>Project Name *</label>
        <input 
          v-model="name" 
          type="text"
          placeholder="Enter project name" 
          required 
        />
      </div>

      <div class="form-group">
        <label>Description</label>
        <textarea 
          v-model="description" 
          placeholder="Enter project description"
          rows="4"
        ></textarea>
      </div>

      <div class="form-group">
        <label>Assign Teams</label>
        <div class="teams-selector">
          <div v-for="team in availableTeams" :key="team.teamId" class="team-checkbox">
            <input 
              type="checkbox" 
              :id="'team-' + team.teamId"
              :value="team.teamId"
              v-model="selectedTeamIds"
            />
            <label :for="'team-' + team.teamId">{{ team.name }}</label>
          </div>
        </div>
        <p v-if="availableTeams.length === 0" class="no-teams">
          No teams available. Please create teams first.
        </p>
      </div>

      <div class="form-actions">
        <button type="button" @click="$router.back()" class="btn-cancel">
          Cancel
        </button>
        <button type="submit" class="btn-submit">
          Create Project
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const name = ref('');
const description = ref('');
const selectedTeamIds = ref([]);
const availableTeams = ref([]);

const fetchTeams = async () => {
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get('http://localhost:5000/teams', {
      headers: { Authorization: `Bearer ${token}` }
    });
    availableTeams.value = response.data;
  } catch (error) {
    console.error(error);
    alert('Error loading teams');
  }
};

const createProject = async () => {
  const token = localStorage.getItem('token');
  try {
    await axios.post('http://localhost:5000/projects', {
      name: name.value,
      description: description.value,
      teamIds: selectedTeamIds.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    alert('Project created successfully!');
    router.push('/projects');
  } catch (error) {
    console.error(error);
    alert(error.response?.data?.msg || 'Error creating project');
  }
};

onMounted(fetchTeams);
</script>

<style scoped>
.create-project {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
}

.project-form {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #000;
}

.teams-selector {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 15px;
  max-height: 200px;
  overflow-y: auto;
}

.team-checkbox {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.team-checkbox input[type="checkbox"] {
  width: auto;
  margin-right: 10px;
  cursor: pointer;
}

.team-checkbox label {
  cursor: pointer;
  margin: 0;
  font-weight: normal;
}

.no-teams {
  color: #999;
  font-size: 14px;
  font-style: italic;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
}

.btn-cancel,
.btn-submit {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-cancel {
  background: #e0e0e0;
  color: #333;
}

.btn-cancel:hover {
  background: #d0d0d0;
}

.btn-submit {
  background: #000;
  color: white;
}

.btn-submit:hover {
  background: #333;
}
</style>
