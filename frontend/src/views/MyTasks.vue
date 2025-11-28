<template>
  <div class="my-tasks">
    <h1>My Tasks</h1>

    <div class="filters">
      <select v-model="statusFilter">
        <option value="">All Statuses</option>
        <option value="to_do">To Do</option>
        <option value="in_progress">In Progress</option>
        <option value="for_review">For Review</option>
        <option value="done">Done</option>
      </select>

      <select v-model="priorityFilter">
        <option value="">All Priorities</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>
    </div>

    <div v-if="filteredTasks.length === 0" class="empty-state">
      <p>No tasks assigned to you</p>
    </div>

    <div class="tasks-grid">
      <div v-for="task in filteredTasks" :key="task.taskId" class="task-card">
        <div class="task-header">
          <h3>{{ task.name }}</h3>
          <div class="header-right">
            <span class="priority-badge" :class="'priority-' + task.priority">
              {{ task.priority }}
            </span>
            <button @click.stop="toggleMenu(task.taskId)" class="menu-btn">⋯</button>
            <div v-if="activeMenu === task.taskId" class="context-menu">
              <div @click="showTaskDetails(task)" class="menu-item">Prikaži detalje</div>
              <div @click="viewAssignedUsers(task)" class="menu-item">Prikaži zaduzene</div>
              <div @click="changePriority(task)" class="menu-item">Promeni prioritet</div>
              <div @click="changeDeadline(task)" class="menu-item">Promeni datum</div>
            </div>
          </div>
        </div>

        <p class="task-description">{{ task.description || 'No description' }}</p>

        <div class="task-meta">
          <span v-if="task.epicName" class="epic-tag">{{ task.epicName }}</span>
          <span v-if="task.deadline" class="deadline" :class="{ overdue: isOverdue(task.deadline) }">
            Due: {{ formatDate(task.deadline) }}
          </span>
        </div>

        <div class="status-section">
          <label>Status:</label>
          <select v-model="task.status" @change="updateStatus(task)" class="status-select">
            <option value="to_do">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="for_review">For Review</option>
            <option value="done">Done</option>
          </select>
        </div>

        <div class="task-actions">
          <button @click="viewProject(task.projectId)" class="btn-project">
            View Project
          </button>
        </div>
      </div>
    </div>

    <!-- Task Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="showDetailsModal = false">
      <div class="modal-content" @click.stop>
        <h2>Task Details</h2>
        <div class="detail-row">
          <strong>Name:</strong> {{ selectedTask?.name }}
        </div>
        <div class="detail-row">
          <strong>Description:</strong> {{ selectedTask?.description || 'No description' }}
        </div>
        <div class="detail-row">
          <strong>Priority:</strong> 
          <span class="priority-badge" :class="'priority-' + selectedTask?.priority">
            {{ selectedTask?.priority }}
          </span>
        </div>
        <div class="detail-row">
          <strong>Status:</strong> {{ formatStatus(selectedTask?.status) }}
        </div>
        <div class="detail-row">
          <strong>Epic:</strong> {{ selectedTask?.epicName || 'None' }}
        </div>
        <div class="detail-row">
          <strong>Deadline:</strong> {{ formatDate(selectedTask?.deadline) }}
        </div>
        <button @click="showDetailsModal = false" class="btn-close">Close</button>
      </div>
    </div>

    <!-- Assigned Users Modal -->
    <div v-if="showUsersModal" class="modal-overlay" @click="showUsersModal = false">
      <div class="modal-content" @click.stop>
        <h2>Assigned Users</h2>
        <div v-if="assignedUsers.length === 0" class="empty-state">
          <p>No users assigned to this task</p>
        </div>
        <div v-else class="users-list">
          <div v-for="user in assignedUsers" :key="user.userId" class="user-item">
            <div class="user-info">
              <strong>{{ user.firstName }} {{ user.lastName }}</strong>
              <span class="user-email">{{ user.email }}</span>
            </div>
          </div>
        </div>
        <button @click="showUsersModal = false" class="btn-close">Close</button>
      </div>
    </div>

    <!-- Change Priority Modal -->
    <div v-if="showPriorityModal" class="modal-overlay" @click="showPriorityModal = false">
      <div class="modal-content" @click.stop>
        <h2>Change Priority</h2>
        <div class="form-group">
          <label>Select new priority:</label>
          <select v-model="newPriority" class="priority-select">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click="savePriority" class="btn-save">Save</button>
          <button @click="showPriorityModal = false" class="btn-cancel">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Change Deadline Modal -->
    <div v-if="showDeadlineModal" class="modal-overlay" @click="showDeadlineModal = false">
      <div class="modal-content" @click.stop>
        <h2>Change Deadline</h2>
        <div class="form-group">
          <label>Select new deadline:</label>
          <input type="date" v-model="newDeadline" class="date-input" />
        </div>
        <div class="modal-actions">
          <button @click="saveDeadline" class="btn-save">Save</button>
          <button @click="showDeadlineModal = false" class="btn-cancel">Cancel</button>
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
const tasks = ref([]);
const statusFilter = ref('');
const priorityFilter = ref('');
const activeMenu = ref(null);
const showDetailsModal = ref(false);
const showUsersModal = ref(false);
const showPriorityModal = ref(false);
const showDeadlineModal = ref(false);
const selectedTask = ref(null);
const assignedUsers = ref([]);
const newPriority = ref('');
const newDeadline = ref('');

const filteredTasks = computed(() => {
  let result = tasks.value;
  
  if (statusFilter.value) {
    result = result.filter(t => t.status === statusFilter.value);
  }
  
  if (priorityFilter.value) {
    result = result.filter(t => t.priority === priorityFilter.value);
  }
  
  return result;
});

const fetchMyTasks = async () => {
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get('http://localhost:5000/tasks/my-tasks', {
      headers: { Authorization: `Bearer ${token}` }
    });
    tasks.value = response.data;
  } catch (error) {
    console.error(error);
    alert('Error loading tasks');
  }
};

const updateStatus = async (task) => {
  const token = localStorage.getItem('token');
  try {
    await axios.put(`http://localhost:5000/tasks/${task.taskId}/status`, {
      status: task.status
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    alert('Status updated successfully');
  } catch (error) {
    console.error(error);
    alert('Error updating status');
    fetchMyTasks(); // Reload to revert
  }
};

const viewProject = (projectId) => {
  router.push(`/projects/${projectId}`);
};

const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString();
};

const isOverdue = (timestamp) => {
  if (!timestamp) return false;
  return timestamp < Math.floor(Date.now() / 1000);
};

const formatStatus = (status) => {
  if (!status) return 'N/A';
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const toggleMenu = (taskId) => {
  activeMenu.value = activeMenu.value === taskId ? null : taskId;
};

const showTaskDetails = (task) => {
  selectedTask.value = task;
  showDetailsModal.value = true;
  activeMenu.value = null;
};

const viewAssignedUsers = async (task) => {
  selectedTask.value = task;
  activeMenu.value = null;
  
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get(
      `http://localhost:5000/tasks/${task.taskId}/users`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    assignedUsers.value = response.data;
    showUsersModal.value = true;
  } catch (error) {
    console.error(error);
    alert('Error loading assigned users');
  }
};

const changePriority = (task) => {
  selectedTask.value = task;
  newPriority.value = task.priority;
  showPriorityModal.value = true;
  activeMenu.value = null;
};

const savePriority = async () => {
  const token = localStorage.getItem('token');
  try {
    await axios.put(
      `http://localhost:5000/tasks/${selectedTask.value.taskId}`,
      { priority: newPriority.value },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    selectedTask.value.priority = newPriority.value;
    showPriorityModal.value = false;
    fetchMyTasks();
    alert('Priority updated successfully');
  } catch (error) {
    console.error(error);
    alert('Error updating priority');
  }
};

const changeDeadline = (task) => {
  selectedTask.value = task;
  if (task.deadline) {
    const date = new Date(task.deadline * 1000);
    newDeadline.value = date.toISOString().split('T')[0];
  } else {
    newDeadline.value = '';
  }
  showDeadlineModal.value = true;
  activeMenu.value = null;
};

const saveDeadline = async () => {
  const token = localStorage.getItem('token');
  const deadlineTimestamp = newDeadline.value ? Math.floor(new Date(newDeadline.value).getTime() / 1000) : null;
  
  try {
    await axios.put(
      `http://localhost:5000/tasks/${selectedTask.value.taskId}`,
      { deadline: deadlineTimestamp },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    selectedTask.value.deadline = deadlineTimestamp;
    showDeadlineModal.value = false;
    fetchMyTasks();
    alert('Deadline updated successfully');
  } catch (error) {
    console.error(error);
    alert('Error updating deadline');
  }
};

onMounted(fetchMyTasks);
</script>

<style scoped>
.my-tasks {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filters select {
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.task-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-header h3 {
  margin: 0;
  font-size: 18px;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

.menu-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 5px 10px;
  color: #666;
  line-height: 1;
}

.menu-btn:hover {
  color: #000;
  background: #f0f0f0;
  border-radius: 4px;
}

.context-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  min-width: 180px;
  margin-top: 5px;
}

.menu-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
}

.menu-item:first-child {
  border-radius: 6px 6px 0 0;
}

.menu-item:last-child {
  border-radius: 0 0 6px 6px;
}

.menu-item:hover {
  background: #f5f5f5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 20px;
}

.detail-row {
  margin-bottom: 15px;
  line-height: 1.6;
}

.detail-row strong {
  display: inline-block;
  min-width: 120px;
}

.users-list {
  margin: 20px 0;
}

.user-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 10px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.user-email {
  color: #666;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.priority-select,
.date-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-save {
  padding: 10px 20px;
  background: #000;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-save:hover {
  background: #333;
}

.btn-cancel,
.btn-close {
  padding: 10px 20px;
  background: #e0e0e0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-cancel:hover,
.btn-close:hover {
  background: #d0d0d0;
}

.btn-close {
  width: 100%;
  margin-top: 20px;
}

.task-header h3 {
  margin: 0;
  font-size: 18px;
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
  color: #666;
  font-size: 14px;
  margin: 10px 0;
  line-height: 1.5;
}

.task-meta {
  display: flex;
  gap: 10px;
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

.deadline {
  color: #666;
  font-weight: 500;
}

.deadline.overdue {
  color: #e74c3c;
  font-weight: 600;
}

.status-section {
  margin: 15px 0;
}

.status-section label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  font-size: 14px;
}

.status-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.task-actions {
  margin-top: 15px;
}

.btn-project {
  width: 100%;
  padding: 10px;
  background: #000;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-project:hover {
  background: #333;
}
</style>
