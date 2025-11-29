<template>
  <div class="project-details">
    <div class="header">
      <div>
        <h1>{{ project.name }}</h1>
        <p class="description">{{ project.description }}</p>
      </div>
      <div class="header-actions">
        <a v-if="project.jiraUrl" :href="project.jiraUrl" target="_blank" class="jira-link">
          View in Jira ({{ project.jiraKey }})
        </a>
        <button @click="$router.back()" class="btn-back">← Back</button>
      </div>
    </div>

    <div class="project-meta">
      <div class="meta-card">
        <strong>Teams Assigned:</strong>
        <div class="teams-list">
          <span v-for="team in project.teams" :key="team.teamId" class="team-badge">
            {{ team.name }}
          </span>
          <span v-if="project.teams.length === 0" class="empty">No teams assigned</span>
        </div>
        <button v-if="isManager" @click="showTeamModal = true" class="btn-manage-teams">
          Manage Teams
        </button>
      </div>
    </div>

    <div class="tabs">
      <button 
        @click="activeTab = 'epics'" 
        :class="{ active: activeTab === 'epics' }"
      >
        Epics
      </button>
      <button 
        @click="activeTab = 'tasks'" 
        :class="{ active: activeTab === 'tasks' }"
      >
        Tasks
      </button>
    </div>

    <!-- Tasks Tab -->
    <div v-if="activeTab === 'tasks'" class="tab-content">
      <div class="section-header">
        <h2>Tasks</h2>
        <button 
          v-if="isManager" 
          @click="$router.push(`/projects/${projectId}/tasks/new`)"
          class="btn-create"
        >
          + New Task
        </button>
      </div>

      <div v-if="tasks.length === 0" class="empty-state">
        <p>No tasks yet</p>
      </div>

      <div class="tasks-list">
        <div v-for="task in tasks" :key="task.taskId" class="task-item">
          <div class="task-header">
            <h3>{{ task.name }}</h3>
            <span class="priority-badge" :class="'priority-' + task.priority">
              {{ task.priority }}
            </span>
          </div>
          
          <p class="task-description">{{ task.description || 'No description' }}</p>
          
          <div class="task-meta">
            <span v-if="task.epicName" class="epic-tag">{{ task.epicName }}</span>
            <span class="status-badge" :class="'status-' + task.status">
              {{ formatStatus(task.status) }}
            </span>
            <span v-if="task.deadline" class="deadline">
              Due: {{ formatDate(task.deadline) }}
            </span>
            <span class="assignees">
              {{ task.assignees.length }} assignee(s)
            </span>
          </div>

          <div class="task-actions">
            <button @click="viewTask(task)" class="btn-view">View</button>
            <button 
              v-if="isManager" 
              @click="deleteTask(task.taskId)"
              class="btn-delete"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Epics Tab -->
    <div v-if="activeTab === 'epics'" class="tab-content">
      <div class="section-header">
        <h2>Epics</h2>
        <button 
          v-if="isManager"
          @click="showCreateEpic = true"
          class="btn-create"
        >
          + New Epic
        </button>
      </div>

      <div v-if="epics.length === 0" class="empty-state">
        <p>No epics yet</p>
      </div>

      <div class="epics-list">
        <div v-for="epic in epics" :key="epic.epicId" class="epic-item">
          <h3>{{ epic.name }}</h3>
          <p>{{ epic.description || 'No description' }}</p>
          <div class="epic-actions" v-if="isManager">
            <button @click="deleteEpic(epic.epicId)" class="btn-delete">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Epic Modal -->
    <div v-if="showCreateEpic" class="modal-overlay" @click="showCreateEpic = false">
      <div class="modal-content" @click.stop>
        <h2>Create Epic</h2>
        <form @submit.prevent="createEpic">
          <input v-model="newEpic.name" placeholder="Epic name" required />
          <textarea v-model="newEpic.description" placeholder="Description" rows="3"></textarea>
          <div class="modal-actions">
            <button type="button" @click="showCreateEpic = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">Create</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Task Details Modal -->
    <div v-if="selectedTask" class="modal-overlay" @click="selectedTask = null">
      <div class="modal-content" @click.stop>
        <h2>{{ selectedTask.name }}</h2>
        <p>{{ selectedTask.description }}</p>
        
        <div class="task-detail-meta">
          <div><strong>Priority:</strong> {{ selectedTask.priority }}</div>
          <div><strong>Status:</strong> {{ formatStatus(selectedTask.status) }}</div>
          <div v-if="selectedTask.deadline">
            <strong>Deadline:</strong> {{ formatDate(selectedTask.deadline) }}
          </div>
          <div v-if="selectedTask.epicName">
            <strong>Epic:</strong> {{ selectedTask.epicName }}
          </div>
        </div>

        <div class="assignees-section">
          <strong>Assignees:</strong>
          <div v-for="assignee in selectedTask.assignees" :key="assignee.userId" class="assignee-item">
            {{ assignee.firstName }} {{ assignee.lastName }} ({{ assignee.email }})
          </div>
        </div>

        <div class="status-update">
          <label><strong>Update Status:</strong></label>
          <select v-model="selectedTask.status" @change="updateTaskStatus">
            <option value="to_do">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="for_review">For Review</option>
            <option value="done">Done</option>
          </select>
        </div>

        <button @click="selectedTask = null" class="btn-close">Close</button>
      </div>
    </div>

    <!-- Team Management Modal -->
    <div v-if="showTeamModal" class="modal-overlay" @click="showTeamModal = false">
      <div class="modal-content" @click.stop>
        <h2>Manage Project Teams</h2>
        <div class="team-checkboxes">
          <label v-for="team in allTeams" :key="team.teamId" class="team-checkbox">
            <input 
              type="checkbox" 
              :value="team.teamId" 
              :checked="isTeamAssigned(team.teamId)"
              @change="toggleTeam(team.teamId)"
            />
            {{ team.name }}
          </label>
        </div>
        <div class="modal-actions">
          <button @click="showTeamModal = false" class="btn-cancel">Cancel</button>
          <button @click="saveTeams" class="btn-submit">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiGet, apiPost, apiPut, apiDelete } from '../utils/api';
import { getUserRole, isAdminOrManager } from '../utils/auth';
import { formatDate, formatStatus } from '../utils/formatters';

const route = useRoute();
const router = useRouter();
const projectId = route.params.id;

const project = ref({ teams: [] });
const tasks = ref([]);
const epics = ref([]);
const activeTab = ref('epics');
const showCreateEpic = ref(false);
const selectedTask = ref(null);
const newEpic = ref({ name: '', description: '' });
const showTeamModal = ref(false);
const allTeams = ref([]);
const selectedTeamIds = ref([]);

const role = computed(() => getUserRole());
const isManager = computed(() => isAdminOrManager());

const fetchProject = async () => {
  try {
    const response = await apiGet(`/projects/${projectId}`);
    project.value = response.data;
    tasks.value = response.data.tasks || [];
    epics.value = response.data.epics || [];
    selectedTeamIds.value = (project.value.teams || []).map(t => t.teamId);
  } catch (error) {
    console.error(error);
    alert('Error loading project');
  }
};

const createEpic = async () => {
  try {
    await apiPost(`/projects/${projectId}/epics`, newEpic.value);
    showCreateEpic.value = false;
    newEpic.value = { name: '', description: '' };
    fetchProject();
  } catch (error) {
    console.error(error);
    alert('Error creating epic');
  }
};

const deleteEpic = async (epicId) => {
  if (!confirm('Delete this epic?')) return;
  try {
    await apiDelete(`/epics/${epicId}`);
    fetchProject();
  } catch (error) {
    console.error(error);
    alert('Error deleting epic');
  }
};

const deleteTask = async (taskId) => {
  if (!confirm('Delete this task?')) return;
  try {
    await apiDelete(`/tasks/${taskId}`);
    fetchProject();
  } catch (error) {
    console.error(error);
    alert('Error deleting task');
  }
};

const viewTask = (task) => {
  selectedTask.value = { ...task };
};

const updateTaskStatus = async () => {
  try {
    await apiPut(`/tasks/${selectedTask.value.taskId}/status`, {
      status: selectedTask.value.status
    });
    fetchProject();
    alert('Status updated');
  } catch (error) {
    console.error(error);
    alert('Error updating status');
  }
};

const fetchAllTeams = async () => {
  try {
    const response = await apiGet('/teams');
    allTeams.value = response.data;
  } catch (error) {
    console.error(error);
  }
};

const isTeamAssigned = (teamId) => {
  return selectedTeamIds.value.includes(teamId);
};

const toggleTeam = (teamId) => {
  const index = selectedTeamIds.value.indexOf(teamId);
  if (index > -1) {
    selectedTeamIds.value.splice(index, 1);
  } else {
    selectedTeamIds.value.push(teamId);
  }
};

const saveTeams = async () => {
  try {
    await apiPut(`/projects/${projectId}`, {
      name: project.value.name,
      description: project.value.description,
      teamIds: selectedTeamIds.value
    });
    showTeamModal.value = false;
    fetchProject();
    alert('Teams updated successfully');
  } catch (error) {
    console.error(error);
    alert('Error updating teams');
  }
};

onMounted(() => {
  fetchProject();
  fetchAllTeams();
});
</script>

<style scoped>
.project-details {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0 0 10px 0;
}

.description {
  color: var(--text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.jira-link {
  color: #3498db;
  text-decoration: none;
  font-size: 14px;
}

.jira-link:hover {
  text-decoration: underline;
}

.btn-back {
  background: #e0e0e0;
  color: #333;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.project-meta {
  background: var(--card-bg);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.meta-card strong {
  display: block;
  margin-bottom: 10px;
}

.btn-manage-teams {
  margin-top: 10px;
  padding: 8px 16px;
  background: #000;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-manage-teams:hover {
  background: #333;
}

.teams-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.team-badge {
  background: #3498db;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.tabs button {
  background: none;
  border: none;
  padding: 12px 24px;
  cursor: pointer;
  font-size: 16px;
  color: var(--text-secondary);
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
}

.tabs button.active {
  color: var(--text-primary);
  border-bottom-color: var(--text-primary);
  font-weight: 500;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.btn-create {
  background: #000;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.tasks-list, .epics-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item, .epic-item {
  background: var(--card-bg);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-header h3 {
  margin: 0;
}

.priority-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-low {
  background: #95a5a6;
  color: white;
}

.priority-medium {
  background: #f39c12;
  color: white;
}

.priority-high {
  background: #e74c3c;
  color: white;
}

.task-description {
  color: var(--text-secondary);
  margin: 10px 0;
}

.task-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  margin: 15px 0;
  font-size: 13px;
}

.epic-tag {
  background: #9b59b6;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: 500;
}

.status-to_do {
  background: #e0e0e0;
  color: #333;
}

.status-in_progress {
  background: #3498db;
  color: white;
}

.status-for_review {
  background: #f39c12;
  color: white;
}

.status-done {
  background: #27ae60;
  color: white;
}

.task-actions, .epic-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.btn-view, .btn-delete {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.btn-view {
  background: #000;
  color: white;
}

.btn-delete {
  background: #e74c3c;
  color: white;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--card-bg);
  padding: 30px;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-top: 0;
}

.modal-content input,
.modal-content textarea,
.modal-content select {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-sizing: border-box;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-cancel {
  background: #e0e0e0;
  color: #333;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-submit, .btn-close {
  background: #000;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.task-detail-meta, .assignees-section, .status-update {
  margin: 20px 0;
  padding: 15px;
  background: var(--bg-secondary);
  border-radius: 6px;
}

.assignee-item {
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
}

.assignee-item:last-child {
  border-bottom: none;
}

.team-checkboxes {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.team-checkbox {
  display: block;
  padding: 10px;
  cursor: pointer;
  user-select: none;
  border-radius: 4px;
}

.team-checkbox:hover {
  background: var(--bg-secondary);
}

.team-checkbox input {
  margin-right: 10px;
  cursor: pointer;
  width: auto;
}
</style>
