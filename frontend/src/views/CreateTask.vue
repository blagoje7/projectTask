<template>
  <div class="create-task">
    <div class="card">
      <h1>Create New Task</h1>

      <form @submit.prevent="submitTask">
        <div class="form-group">
          <label>Task Name *</label>
          <input 
            type="text" 
            v-model="task.name" 
            required 
            placeholder="Enter task name"
          />
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea 
            v-model="task.description" 
            rows="4"
            placeholder="Task description (optional)"
          ></textarea>
        </div>

        <div class="form-group">
          <label>Priority *</label>
          <select v-model="task.priority" required>
            <option value="">Select priority</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div class="form-group">
          <label>Deadline</label>
          <input 
            type="date" 
            v-model="task.deadline"
          />
        </div>

        <div class="form-group">
          <label>Assign To (Optional)</label>
          <div v-if="teamMembers.length === 0" class="empty-message">
            Loading team members...
          </div>
          <div v-else class="assignee-list">
            <label v-for="member in teamMembers" :key="member.userId" class="assignee-checkbox">
              <input 
                type="checkbox" 
                :value="member.userId" 
                v-model="task.assigneeIds"
              />
              {{ member.firstName }} {{ member.lastName }}
            </label>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" @click="cancel" class="btn-cancel">Cancel</button>
          <button type="submit" class="btn-submit">Create Task</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { apiGet, apiPost } from '../utils/api';

const router = useRouter();
const route = useRoute();
const projectId = route.params.id;

const teamMembers = ref([]);

const task = ref({
  name: '',
  description: '',
  priority: '',
  deadline: '',
  assigneeIds: []
});

const fetchProjectData = async () => {
  try {
    // Fetch project
    const projectResponse = await apiGet(`/projects/${projectId}`);
    
    // Fetch team members from all teams assigned to the project
    const teams = projectResponse.data.teams || [];
    const memberSet = new Set();
    const members = [];

    for (const team of teams) {
      const teamResponse = await apiGet(`/teams/${team.teamId}`);
      
      for (const member of teamResponse.data.users || []) {
        if (!memberSet.has(member.userId)) {
          memberSet.add(member.userId);
          members.push(member);
        }
      }
    }

    teamMembers.value = members.sort((a, b) => 
      `${a.firstName} ${a.lastName}`.localeCompare(`${b.firstName} ${b.lastName}`)
    );
  } catch (error) {
    console.error(error);
    alert('Error loading project data');
  }
};

const submitTask = async () => {
  if (!task.value.name || !task.value.priority) {
    alert('Please fill in all required fields');
    return;
  }

  const payload = {
    name: task.value.name,
    description: task.value.description || '',
    priority: task.value.priority,
    assigneeIds: task.value.assigneeIds || []
  };

  if (task.value.deadline) {
    const dateObj = new Date(task.value.deadline);
    payload.deadline = Math.floor(dateObj.getTime() / 1000);
  }

  try {
    await apiPost(`/projects/${projectId}/tasks`, payload);
    alert('Task created successfully');
    router.push(`/projects/${projectId}`);
  } catch (error) {
    console.error(error);
    alert(error.response?.data?.error || 'Error creating task');
  }
};

const cancel = () => {
  router.push(`/projects/${projectId}`);
};

onMounted(fetchProjectData);
</script>

<style scoped>
.create-task {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
}

.card {
  background: var(--card-bg);
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="date"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}

.form-group textarea {
  resize: vertical;
}

.empty-message {
  color: var(--text-secondary);
  font-style: italic;
}

.assignee-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 10px;
}

.assignee-checkbox {
  display: block;
  padding: 8px;
  cursor: pointer;
  user-select: none;
}

.assignee-checkbox:hover {
  background: var(--bg-secondary);
  border-radius: 4px;
}

.assignee-checkbox input {
  margin-right: 10px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn-cancel,
.btn-submit {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
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
