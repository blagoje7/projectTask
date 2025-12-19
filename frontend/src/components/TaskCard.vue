<template>
  <div class="task-item">
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
      <button @click="$emit('view', task)" class="btn-view">View</button>
      <button 
        v-if="isManager" 
        @click="$emit('delete', task.taskId)"
        class="btn-delete"
      >
        Delete
      </button>
    </div>
  </div>
</template>

<script setup>
// --- Imports ---
import { formatStatus, formatDate } from '../utils/formatters';

// --- Props ---
defineProps({
  task: {
    type: Object,
    required: true
  },
  isManager: {
    type: Boolean,
    default: false
  }
});

defineEmits(['view', 'delete']);
</script>

<style scoped>
.task-item {
  background: var(--card-bg);
  padding: 16px;
  border-radius: 3px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 12px;
  border: 1px solid var(--border-color);
  transition: box-shadow 0.2s;
}

.task-item:hover {
  box-shadow: var(--shadow-md);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.task-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.task-description {
  color: var(--text-secondary);
  font-size: 12px;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 11px;
  align-items: center;
}

.priority-badge {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

/* Using hardcoded colors for badges to ensure visibility, but could be variables */
.priority-high { background: #FFEBE6; color: #BF2600; } /* Jira Red */
.priority-medium { background: #FFFAE6; color: #FF8B00; } /* Jira Orange */
.priority-low { background: #E3FCEF; color: #006644; } /* Jira Green */

[data-theme="dark"] .priority-high { background: #42221F; color: #FF8F73; }
[data-theme="dark"] .priority-medium { background: #332E1B; color: #F5CD47; }
[data-theme="dark"] .priority-low { background: #1C3329; color: #6CC9A6; }

.status-badge {
  padding: 2px 6px;
  border-radius: 3px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-weight: 600;
  text-transform: uppercase;
}

.status-in_progress { background: #DEEBFF; color: #0747A6; }
[data-theme="dark"] .status-in_progress { background: #192B4D; color: #579DFF; }

.status-done { background: #E3FCEF; color: #006644; }
[data-theme="dark"] .status-done { background: #1C3329; color: #6CC9A6; }

.epic-tag {
  background: #EAE6FF;
  color: #403294;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}
[data-theme="dark"] .epic-tag { background: #28243D; color: #9F8FEF; }

.deadline {
  color: var(--danger-color);
  font-weight: 500;
}

.assignees {
  color: var(--text-secondary);
}

.task-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.btn-view, .btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  flex: 1;
  font-weight: 500;
  transition: background 0.1s;
}

.btn-view {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-view:hover {
  background: var(--hover-bg);
}

.btn-delete {
  background: transparent;
  color: var(--danger-color);
  border: 1px solid var(--danger-color);
}

.btn-delete:hover {
  background: var(--danger-color);
  color: white;
}
</style>
