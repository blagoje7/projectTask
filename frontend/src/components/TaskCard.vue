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
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.task-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
}

.task-description {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.priority-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-high { background: #fee2e2; color: #dc2626; }
.priority-medium { background: #fef3c7; color: #d97706; }
.priority-low { background: #d1fae5; color: #059669; }

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: #e5e7eb;
  color: #374151;
}

.status-todo { background: #f3f4f6; }
.status-in_progress { background: #dbeafe; color: #1e40af; }
.status-done { background: #d1fae5; color: #065f46; }

.epic-tag {
  background: #f3e8ff;
  color: #7e22ce;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.deadline {
  color: #dc2626;
}

.assignees {
  color: #6b7280;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: auto;
}

.btn-view, .btn-delete {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  flex: 1;
}

.btn-view {
  background: #f3f4f6;
  color: #374151;
}

.btn-view:hover {
  background: #e5e7eb;
}

.btn-delete {
  background: #fee2e2;
  color: #dc2626;
}

.btn-delete:hover {
  background: #fecaca;
}
</style>
