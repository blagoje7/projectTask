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
import { apiGet, apiPost } from '../utils/api';

const router = useRouter();
const name = ref('');
const description = ref('');
const selectedTeamIds = ref([]);
const availableTeams = ref([]);

const fetchTeams = async () => {
  try {
    const response = await apiGet('/teams');
    availableTeams.value = response.data;
  } catch (error) {
    console.error(error);
    alert('Error loading teams');
  }
};

const createProject = async () => {
  try {
    await apiPost('/projects', {
      name: name.value,
      description: description.value,
      teamIds: selectedTeamIds.value
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
  background: var(--card-bg);
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
  color: var(--text-primary);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--text-primary);
}

.teams-selector {
  border: 1px solid var(--border-color);
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
  color: var(--text-primary);
}

.no-teams {
  color: var(--text-secondary);
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
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-cancel:hover {
  background: var(--border-color);
}

.btn-submit {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.btn-submit:hover {
  opacity: 0.8;
}
</style>
