<template>
  <div class="project-list">
    <div class="header">
      <h1>Projects</h1>
      <button @click="$router.push('/projects/new')" class="btn-create" v-if="isManager || isAdmin">
        + New Project
      </button>
    </div>

    <div v-if="projects.length === 0" class="empty-state">
      <p>No projects found</p>
      <button @click="$router.push('/projects/new')" v-if="isManager || isAdmin">
        Create your first project
      </button>
    </div>

    <div class="projects-grid">
      <div v-for="project in projects" :key="project.projectId" class="project-card">
        <h3>{{ project.name }}</h3>
        <p class="description">{{ project.description || 'No description' }}</p>
        
        <div class="project-meta">
          <span class="meta-item">
            <strong>Teams:</strong> {{ project.teams.length }}
          </span>
          <span class="meta-item" v-if="project.jiraKey">
            <a :href="project.jiraUrl" target="_blank" class="jira-link">
              {{ project.jiraKey }}
            </a>
          </span>
        </div>

        <div class="actions">
          <button @click="viewProject(project.projectId)" class="btn-view">
            View Details
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const projects = ref([]);
const role = computed(() => localStorage.getItem('role'));
const isAdmin = computed(() => role.value === 'admin');
const isManager = computed(() => role.value === 'manager' || role.value === 'admin');

const fetchProjects = async () => {
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get('http://localhost:5001/projects', {
      headers: { Authorization: `Bearer ${token}` }
    });
    projects.value = response.data;
  } catch (error) {
    console.error(error);
    alert('Error loading projects');
  }
};

const viewProject = (projectId) => {
  router.push(`/projects/${projectId}`);
};

onMounted(fetchProjects);
</script>

<style scoped>
.project-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.btn-create {
  background: #000;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-create:hover {
  background: #333;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-state button {
  margin-top: 20px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.project-card {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.project-card h3 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
}

.description {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 15px;
  line-height: 1.5;
}

.project-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 13px;
}

.meta-item {
  color: var(--text-secondary);
}

.jira-link {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
}

.jira-link:hover {
  text-decoration: underline;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn-view {
  flex: 1;
  background: #000;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-view:hover {
  background: #333;
}
</style>
