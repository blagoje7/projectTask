<template>
  <div class="manager-dashboard">
    <!-- Left Sidebar -->
    <aside class="left-sidebar">
      <div class="sidebar-section">
        <h3>Projects</h3>
        <div class="project-list">
          <div
            v-for="project in projects"
            :key="project.projectId"
            :class="['project-item', { active: selectedProject?.projectId === project.projectId }]"
            @click="selectProject(project)"
          >
            <span class="project-indicator"></span>
            {{ project.name }}
          </div>
        </div>
      </div>

      <div class="sidebar-section" v-if="selectedProject">
        <h3>Teams</h3>
        <div class="team-list">
          <div
            v-for="team in currentTeams"
            :key="team.teamId"
            :class="['team-item', { active: selectedTeam?.teamId === team.teamId }]"
            @click="selectTeam(team)"
          >
            {{ team.name }}
          </div>
        </div>
      </div>

      <div class="sidebar-section" v-if="selectedTeam">
        <h3>Team Members</h3>
        <div class="member-list">
          <div v-for="member in teamMembers" :key="member.userId" class="member-item">
            <div class="member-avatar">{{ member.firstName[0] }}{{ member.lastName[0] }}</div>
            <span>{{ member.firstName }} {{ member.lastName }}</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <div class="content-header">
        <h1>Active Issues</h1>
      </div>

      <!-- Tasks View -->
      <div class="tasks-container">
        <div v-if="!selectedProject" class="empty-project-state">
          <div class="empty-icon">📋</div>
          <h2>No Project Selected</h2>
          <p>Select a project from the left sidebar to view tasks and details</p>
        </div>
        
        <div v-else class="tasks-toolbar">
          <div class="search-filter">
            <input type="text" v-model="searchQuery" placeholder="Search tickets..." />
            <button class="filter-btn">
              <span>Filter</span>
            </button>
          </div>

          <div class="view-toggles">
            <button 
              :class="['view-btn', { active: viewMode === 'list' }]" 
              @click="viewMode = 'list'"
              title="List view"
            >
              ☰
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'grid' }]" 
              @click="viewMode = 'grid'"
              title="Grid view"
            >
              ⊞
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'calendar' }]" 
              @click="viewMode = 'calendar'"
              title="Calendar view"
            >
              📅
            </button>
          </div>
        </div>

        <!-- List View -->
        <div v-if="viewMode === 'list'" class="list-view">
          <table class="tasks-table">
            <thead>
              <tr>
                <th>Task ID</th>
                <th>Title</th>
                <th>Project</th>
                <th>Priority</th>
                <th>Date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in filteredTasks" :key="task.taskId" class="task-row">
                <td class="task-id">{{ task.jiraKey || `TASK-${task.taskId.substring(0, 5)}` }}</td>
                <td class="task-title">{{ task.name }}</td>
                <td class="task-project">{{ task.projectName }}</td>
                <td>
                  <span :class="['priority-badge', 'priority-' + task.priority]">
                    {{ task.priority }}
                  </span>
                </td>
                <td class="task-date">{{ formatDate(task.deadline) }}</td>
                <td class="task-actions">
                  <button @click.stop="toggleMenu(task.taskId)" class="menu-btn">⋮</button>
                  <div v-if="activeMenu === task.taskId" class="context-menu">
                    <div @click="viewTaskDetails(task)">View Details</div>
                    <div @click="editTask(task)">Edit Task</div>
                    <div @click="changePriority(task)">Change Priority</div>
                    <div @click="changeStatus(task)">Change Status</div>
                    <div @click="deleteTask(task)">Delete Task</div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid-view">
          <div v-for="task in filteredTasks" :key="task.taskId" class="task-card">
            <div class="card-header">
              <span class="task-id">{{ task.jiraKey || `TASK-${task.taskId.substring(0, 5)}` }}</span>
              <button @click.stop="toggleMenu(task.taskId)" class="menu-btn">⋮</button>
              <div v-if="activeMenu === task.taskId" class="context-menu">
                <div @click="viewTaskDetails(task)">View Details</div>
                <div @click="editTask(task)">Edit Task</div>
                <div @click="changePriority(task)">Change Priority</div>
                <div @click="changeStatus(task)">Change Status</div>
                <div @click="deleteTask(task)">Delete Task</div>
              </div>
            </div>
            <h4>{{ task.name }}</h4>
            <p>{{ task.description || 'No description' }}</p>
            <div class="card-footer">
              <span :class="['priority-badge', 'priority-' + task.priority]">
                {{ task.priority }}
              </span>
              <span class="deadline">{{ formatDate(task.deadline) }}</span>
            </div>
          </div>
        </div>

        <!-- Calendar View -->
        <div v-if="viewMode === 'calendar'" class="calendar-view">
          <div class="calendar-header">
            <button @click="previousMonth">‹</button>
            <h3>{{ currentMonthName }} {{ currentYear }}</h3>
            <button @click="nextMonth">›</button>
          </div>
          <div class="calendar-grid">
            <div class="calendar-weekdays">
              <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
            </div>
            <div class="calendar-days">
              <div
                v-for="day in calendarDays"
                :key="day.date"
                :class="['calendar-day', { 'other-month': day.otherMonth, 'today': day.isToday }]"
              >
                <div class="day-number">{{ day.day }}</div>
                <div class="day-tasks">
                  <div
                    v-for="task in day.tasks"
                    :key="task.taskId"
                    :class="['calendar-task', 'priority-' + task.priority]"
                    @click="viewTaskDetails(task)"
                  >
                    {{ task.name }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Right Sidebar - Progress -->
    <aside class="right-sidebar" v-if="selectedProject">
      <h3>Project Progress</h3>
      <div class="progress-container">
        <div class="progress-percentage">{{ projectProgress }}%</div>
        <div class="progress-bar-wrapper">
          <div class="progress-bar" :style="{ height: projectProgress + '%' }"></div>
        </div>
        <div class="progress-stats">
          <div class="stat">
            <span class="stat-label">Done</span>
            <span class="stat-value">{{ doneTasks }}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Total</span>
            <span class="stat-value">{{ totalTasks }}</span>
          </div>
        </div>
      </div>

      <button @click="openWhiteboard" class="btn-whiteboard">
        🎨 Open Whiteboard
      </button>
    </aside>

    <!-- Whiteboard Modal -->
    <div v-if="showWhiteboard" class="modal-overlay" @click.self="closeWhiteboard">
      <div class="whiteboard-modal">
        <div class="whiteboard-modal-header">
          <h2>{{ selectedProject.name }} - Whiteboard</h2>
          <button @click="closeWhiteboard" class="btn-close-modal">✕</button>
        </div>

        <div class="whiteboard-toolbar">
          <button @click="selectTool('pen')" :class="{ active: drawingTool === 'pen' }">✏️ Pen</button>
          <button @click="selectTool('eraser')" :class="{ active: drawingTool === 'eraser' }">🧹 Eraser</button>
          <input type="color" v-model="drawingColor" />
          <button @click="saveWhiteboardManually">💾 Save</button>
          <button @click="clearWhiteboard">Clear All</button>
          <button @click="toggleHistory">History</button>
        </div>

        <canvas
          ref="whiteboardCanvas"
          @mousedown="startDrawing"
          @mousemove="draw"
          @mouseup="stopDrawing"
          @mouseleave="stopDrawing"
          class="whiteboard-canvas"
        ></canvas>

        <div v-if="showHistory" class="history-panel">
          <h4>Drawing History</h4>
          <div v-for="entry in whiteboardHistory" :key="entry.whiteboardId" class="history-entry">
            <strong>{{ entry.userName }}</strong> - {{ formatDateTime(entry.createdAt) }}
            <button @click="restoreDrawing(entry)">Restore</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Detail Modal -->
    <div v-if="detailTask" class="modal-overlay" @click.self="detailTask = null">
      <div class="modal-content">
        <h2>{{ detailTask.name }}</h2>
        <p><strong>ID:</strong> {{ detailTask.jiraKey || detailTask.taskId }}</p>
        <p><strong>Description:</strong> {{ detailTask.description || 'No description' }}</p>
        <p><strong>Priority:</strong> 
          <span :class="['priority-badge', 'priority-' + detailTask.priority]">
            {{ detailTask.priority }}
          </span>
        </p>
        <p><strong>Status:</strong> {{ formatStatus(detailTask.status) }}</p>
        <p><strong>Deadline:</strong> {{ formatDate(detailTask.deadline) }}</p>
        <p><strong>Assignees:</strong> {{ detailTask.assigneeCount || 0 }}</p>
        <button @click="detailTask = null" class="btn-close">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import axios from 'axios';
import { io } from 'socket.io-client';

let socket = null;

// State
const projects = ref([]);
const selectedProject = ref(null);
const currentTeams = ref([]);
const selectedTeam = ref(null);
const teamMembers = ref([]);
const allTasks = ref([]);
const viewMode = ref('list');
const searchQuery = ref('');
const activeMenu = ref(null);
const detailTask = ref(null);

// Whiteboard state
const showWhiteboard = ref(false);
const whiteboardCanvas = ref(null);
const drawingTool = ref('pen');
const drawingColor = ref('#000000');
const isDrawing = ref(false);
const canvasContext = ref(null);
const showHistory = ref(false);
const whiteboardHistory = ref([]);
const activeCursors = ref({});
const currentStroke = ref([]);

// Calendar state
const currentMonth = ref(new Date().getMonth());
const currentYear = ref(new Date().getFullYear());
const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// Computed
const filteredTasks = computed(() => {
  let tasks = allTasks.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    tasks = tasks.filter(t => 
      t.name.toLowerCase().includes(query) ||
      (t.description && t.description.toLowerCase().includes(query))
    );
  }
  
  return tasks;
});

const projectProgress = computed(() => {
  if (totalTasks.value === 0) return 0;
  return Math.round((doneTasks.value / totalTasks.value) * 100);
});

const doneTasks = computed(() => {
  return allTasks.value.filter(t => t.status === 'done').length;
});

const totalTasks = computed(() => {
  return allTasks.value.length;
});

const currentMonthName = computed(() => {
  const date = new Date(currentYear.value, currentMonth.value);
  return date.toLocaleString('default', { month: 'long' });
});

const calendarDays = computed(() => {
  const firstDay = new Date(currentYear.value, currentMonth.value, 1);
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0);
  const prevLastDay = new Date(currentYear.value, currentMonth.value, 0);
  
  const days = [];
  const today = new Date();
  
  // Previous month days
  for (let i = firstDay.getDay() - 1; i >= 0; i--) {
    const day = prevLastDay.getDate() - i;
    days.push({
      day,
      date: `${currentYear.value}-${currentMonth.value}-${day}`,
      otherMonth: true,
      isToday: false,
      tasks: []
    });
  }
  
  // Current month days
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const dateStr = `${currentYear.value}-${currentMonth.value + 1}-${i}`;
    const isToday = today.getDate() === i && 
                    today.getMonth() === currentMonth.value && 
                    today.getFullYear() === currentYear.value;
    
    const dayTasks = allTasks.value.filter(task => {
      if (!task.deadline) return false;
      const taskDate = new Date(task.deadline * 1000);
      return taskDate.getDate() === i && 
             taskDate.getMonth() === currentMonth.value && 
             taskDate.getFullYear() === currentYear.value;
    });
    
    days.push({
      day: i,
      date: dateStr,
      otherMonth: false,
      isToday,
      tasks: dayTasks
    });
  }
  
  // Next month days
  const remainingDays = 42 - days.length;
  for (let i = 1; i <= remainingDays; i++) {
    days.push({
      day: i,
      date: `${currentYear.value}-${currentMonth.value + 2}-${i}`,
      otherMonth: true,
      isToday: false,
      tasks: []
    });
  }
  
  return days;
});

// Methods
const fetchProjects = async () => {
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get('http://localhost:5000/projects', {
      headers: { Authorization: `Bearer ${token}` }
    });
    projects.value = response.data;
    
    // Don't auto-select project - let user choose
  } catch (error) {
    console.error(error);
  }
};

const selectProject = async (project) => {
  selectedProject.value = project;
  currentTeams.value = project.teams || [];
  selectedTeam.value = null;
  teamMembers.value = [];
  await fetchProjectTasks(project.projectId);
};

const selectTeam = async (team) => {
  selectedTeam.value = team;
  await fetchTeamMembers(team.teamId);
};

const fetchProjectTasks = async (projectId) => {
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get(`http://localhost:5000/projects/${projectId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    allTasks.value = (response.data.tasks || []).map(task => ({
      ...task,
      projectName: selectedProject.value.name
    }));
  } catch (error) {
    console.error(error);
  }
};

const fetchTeamMembers = async (teamId) => {
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get(`http://localhost:5000/teams/${teamId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    teamMembers.value = response.data.users || [];
  } catch (error) {
    console.error(error);
  }
};

const toggleMenu = (taskId) => {
  activeMenu.value = activeMenu.value === taskId ? null : taskId;
};

const viewTaskDetails = (task) => {
  detailTask.value = task;
  activeMenu.value = null;
};

const editTask = (task) => {
  // Navigate to edit
  activeMenu.value = null;
  alert('Edit task: ' + task.name);
};

const changePriority = async (task) => {
  const priorities = ['low', 'medium', 'high'];
  const currentIndex = priorities.indexOf(task.priority);
  const newPriority = priorities[(currentIndex + 1) % 3];
  
  const token = localStorage.getItem('token');
  try {
    await axios.put(`http://localhost:5000/tasks/${task.taskId}`, {
      priority: newPriority
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    task.priority = newPriority;
    activeMenu.value = null;
  } catch (error) {
    console.error(error);
    alert('Error changing priority');
  }
};

const changeStatus = async (task) => {
  const statuses = ['to_do', 'in_progress', 'for_review', 'done'];
  const currentIndex = statuses.indexOf(task.status);
  const newStatus = statuses[(currentIndex + 1) % 4];
  
  const token = localStorage.getItem('token');
  try {
    await axios.put(`http://localhost:5000/tasks/${task.taskId}/status`, {
      status: newStatus
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    task.status = newStatus;
    activeMenu.value = null;
  } catch (error) {
    console.error(error);
    alert('Error changing status');
  }
};

const deleteTask = async (task) => {
  if (!confirm(`Delete task "${task.name}"?`)) return;
  
  const token = localStorage.getItem('token');
  try {
    await axios.delete(`http://localhost:5000/tasks/${task.taskId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    allTasks.value = allTasks.value.filter(t => t.taskId !== task.taskId);
    activeMenu.value = null;
  } catch (error) {
    console.error(error);
    alert('Error deleting task');
  }
};

const formatDate = (timestamp) => {
  if (!timestamp) return 'No deadline';
  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const formatStatus = (status) => {
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const previousMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11;
    currentYear.value--;
  } else {
    currentMonth.value--;
  }
};

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0;
    currentYear.value++;
  } else {
    currentMonth.value++;
  }
};

// Whiteboard methods
const openWhiteboard = () => {
  showWhiteboard.value = true;
  setTimeout(() => {
    initWhiteboard();
  }, 100);
};

const closeWhiteboard = () => {
  disconnectWebSocket();
  showWhiteboard.value = false;
  showHistory.value = false;
  activeCursors.value = {};
};

const connectWebSocket = () => {
  if (socket) return;
  
  socket = io('http://localhost:5000');
  
  const userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substr(2, 9);
  const username = localStorage.getItem('username') || 'User';
  
  socket.on('connect', () => {
    console.log('WebSocket connected');
    socket.emit('join_whiteboard', {
      projectId: selectedProject.value.projectId,
      userId,
      username
    });
  });
  
  socket.on('whiteboard_state', (data) => {
    console.log('Received whiteboard state from WebSocket');
    if (data.canvasData && canvasContext.value) {
      const img = new Image();
      img.onload = () => {
        canvasContext.value.clearRect(0, 0, whiteboardCanvas.value.width, whiteboardCanvas.value.height);
        canvasContext.value.drawImage(img, 0, 0);
      };
      img.src = data.canvasData;
    }
  });
  
  socket.on('draw', (data) => {
    drawRemoteStroke(data);
  });
  
  socket.on('cursor_update', (data) => {
    activeCursors.value[data.userId] = {
      username: data.username,
      position: data.position
    };
  });
  
  socket.on('user_joined', (data) => {
    console.log(`${data.username} joined the whiteboard`);
  });
  
  socket.on('user_left', (data) => {
    delete activeCursors.value[data.userId];
  });
  
  socket.on('canvas_cleared', () => {
    if (canvasContext.value) {
      canvasContext.value.clearRect(0, 0, whiteboardCanvas.value.width, whiteboardCanvas.value.height);
    }
  });
  
  socket.on('canvas_saved', () => {
    // Reload canvas from server when someone saves
    setTimeout(() => {
      loadWhiteboard();
    }, 100);
  });
};

const disconnectWebSocket = () => {
  if (socket) {
    const userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substr(2, 9);
    socket.emit('leave_whiteboard', {
      projectId: selectedProject.value.projectId,
      userId
    });
    socket.disconnect();
    socket = null;
  }
};

const drawRemoteStroke = (data) => {
  if (!canvasContext.value || !data.points || data.points.length < 2) return;
  
  canvasContext.value.beginPath();
  canvasContext.value.moveTo(data.points[0].x, data.points[0].y);
  
  if (data.tool === 'eraser') {
    canvasContext.value.globalCompositeOperation = 'destination-out';
  } else {
    canvasContext.value.strokeStyle = data.color || '#000000';
    canvasContext.value.globalCompositeOperation = 'source-over';
  }
  
  for (let i = 1; i < data.points.length; i++) {
    canvasContext.value.lineTo(data.points[i].x, data.points[i].y);
  }
  
  canvasContext.value.stroke();
};

const initWhiteboard = async () => {
  const canvas = whiteboardCanvas.value;
  if (!canvas) return;
  
  canvas.width = 800;
  canvas.height = 600;
  canvasContext.value = canvas.getContext('2d');
  canvasContext.value.lineCap = 'round';
  canvasContext.value.lineJoin = 'round';
  canvasContext.value.lineWidth = 2;
  
  // Load from database first
  await loadWhiteboard();
  
  // Then connect WebSocket
  setTimeout(() => {
    connectWebSocket();
  }, 200);
  
  canvas.addEventListener('mousemove', handleCanvasMouseMove);
};

const handleCanvasMouseMove = (e) => {
  if (!socket || !selectedProject.value) return;
  
  const rect = whiteboardCanvas.value.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  
  const userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substr(2, 9);
  const username = localStorage.getItem('username') || 'User';
  
  socket.emit('cursor_move', {
    projectId: selectedProject.value.projectId,
    userId,
    username,
    position: { x, y }
  });
};

const loadWhiteboard = async () => {
  if (!selectedProject.value) return;
  
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get(
      `http://localhost:5000/projects/${selectedProject.value.projectId}/whiteboard`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    canvasContext.value.clearRect(0, 0, whiteboardCanvas.value.width, whiteboardCanvas.value.height);
    
    if (response.data.imageData) {
      const img = new Image();
      img.onload = () => {
        canvasContext.value.drawImage(img, 0, 0);
      };
      img.src = response.data.imageData;
    }
    
    whiteboardHistory.value = response.data.history || [];
  } catch (error) {
    console.error('Error loading whiteboard:', error);
  }
};

const selectTool = (tool) => {
  drawingTool.value = tool;
};

const startDrawing = (e) => {
  if (!canvasContext.value) return;
  isDrawing.value = true;
  currentStroke.value = [];
  
  const rect = whiteboardCanvas.value.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  
  currentStroke.value.push({ x, y });
  
  canvasContext.value.beginPath();
  canvasContext.value.moveTo(x, y);
};

const draw = (e) => {
  if (!isDrawing.value || !canvasContext.value) return;
  
  const rect = whiteboardCanvas.value.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  
  currentStroke.value.push({ x, y });
  
  if (drawingTool.value === 'pen') {
    canvasContext.value.strokeStyle = drawingColor.value;
    canvasContext.value.globalCompositeOperation = 'source-over';
  } else if (drawingTool.value === 'eraser') {
    canvasContext.value.globalCompositeOperation = 'destination-out';
  }
  
  canvasContext.value.lineTo(x, y);
  canvasContext.value.stroke();
};

const stopDrawing = () => {
  if (!isDrawing.value) return;
  
  isDrawing.value = false;
  
  // Emit stroke to other users via WebSocket
  if (socket && selectedProject.value && currentStroke.value.length > 0) {
    const userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substr(2, 9);
    const username = localStorage.getItem('username') || 'User';
    
    socket.emit('draw', {
      projectId: selectedProject.value.projectId,
      userId,
      username,
      tool: drawingTool.value,
      color: drawingColor.value,
      points: currentStroke.value
    });
  }
  
  currentStroke.value = [];
  
  // Auto-save to database via WebSocket
  saveWhiteboardToServer();
};

const saveWhiteboardToServer = async () => {
  if (!selectedProject.value || !socket) return;
  
  const userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substr(2, 9);
  const username = localStorage.getItem('username') || 'User';
  const imageData = whiteboardCanvas.value.toDataURL();
  
  // Save via WebSocket (which now saves to database)
  socket.emit('save_canvas', {
    projectId: selectedProject.value.projectId,
    userId,
    username,
    canvasData: imageData
  });
};

const saveWhiteboardManually = async () => {
  await saveWhiteboardToServer();
  alert('Whiteboard saved successfully');
};

const clearWhiteboard = async () => {
  if (!confirm('Clear whiteboard?')) return;
  
  canvasContext.value.clearRect(
    0, 0, 
    whiteboardCanvas.value.width, 
    whiteboardCanvas.value.height
  );
  
  // Emit clear event via WebSocket
  if (socket && selectedProject.value) {
    const userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substr(2, 9);
    const username = localStorage.getItem('username') || 'User';
    
    socket.emit('clear_canvas', {
      projectId: selectedProject.value.projectId,
      userId,
      username
    });
  }
  
  await saveWhiteboardToServer();
};

const toggleHistory = () => {
  showHistory.value = !showHistory.value;
};

const restoreDrawing = (entry) => {
  if (!confirm('Revert to this version? This will save it as a new version.')) return;
  
  const img = new Image();
  img.onload = () => {
    canvasContext.value.clearRect(
      0, 0, 
      whiteboardCanvas.value.width, 
      whiteboardCanvas.value.height
    );
    canvasContext.value.drawImage(img, 0, 0);
    
    saveWhiteboardToServer();
  };
  img.src = entry.imageData;
  showHistory.value = false;
};

const formatDateTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp * 1000);
  return date.toLocaleString();
};

onMounted(() => {
  fetchProjects();
  
  // Close menu on outside click
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.task-actions')) {
      activeMenu.value = null;
    }
  });
});

onBeforeUnmount(() => {
  disconnectWebSocket();
});
</script>

<style scoped>
.manager-dashboard {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

.left-sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  padding: 20px 0;
}

.sidebar-section {
  margin-bottom: 30px;
  padding: 0 20px;
}

.sidebar-section h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #666;
  text-transform: uppercase;
}

.project-list,
.team-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.project-item,
.team-item {
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-item:hover,
.team-item:hover {
  background: #f5f5f5;
}

.project-item.active,
.team-item.active {
  background: #000;
  color: white;
}

.project-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
}

.project-item.active .project-indicator {
  background: #4caf50;
}

.member-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  font-size: 13px;
}

.member-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #000;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  padding: 20px 30px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.content-header h1 {
  font-size: 24px;
  margin: 0;
}

.tasks-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 30px;
}

.empty-project-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  text-align: center;
  color: #666;
}

.empty-project-state .empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-project-state h2 {
  font-size: 24px;
  margin: 0 0 10px 0;
  color: #333;
}

.empty-project-state p {
  font-size: 16px;
  margin: 0;
  color: #999;
}

.tasks-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
}

.search-filter {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-filter input {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  width: 300px;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  color: #333;
}

.filter-btn:hover {
  background: #f5f5f5;
}

.view-toggles {
  display: flex;
  gap: 5px;
}

.view-btn {
  width: 40px;
  height: 40px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.view-btn:hover {
  background: #f5f5f5;
}

.view-btn.active {
  background: #000;
  color: white;
  border-color: #000;
}

/* List View */
.list-view {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.tasks-table {
  width: 100%;
  border-collapse: collapse;
}

.tasks-table thead {
  background: #f9f9f9;
  border-bottom: 2px solid #e0e0e0;
}

.tasks-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
  color: #666;
}

.task-row {
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.task-row:hover {
  background: #fafafa;
}

.tasks-table td {
  padding: 16px;
  font-size: 14px;
}

.task-id {
  color: #666;
  font-weight: 500;
}

.task-title {
  font-weight: 500;
}

.task-project {
  color: #666;
}

.priority-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 11px;
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

.task-date {
  color: #666;
  font-size: 13px;
}

.task-actions {
  position: relative;
}

.menu-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.menu-btn:hover {
  background: #f0f0f0;
}

.context-menu {
  position: absolute;
  right: 0;
  top: 100%;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  min-width: 180px;
}

.context-menu div {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  border-bottom: 1px solid #f0f0f0;
}

.context-menu div:last-child {
  border-bottom: none;
}

.context-menu div:hover {
  background: #f5f5f5;
}

/* Grid View */
.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.task-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-card h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.task-card p {
  color: #666;
  font-size: 14px;
  margin: 0 0 15px 0;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
}

.deadline {
  color: #666;
  font-size: 13px;
}

/* Calendar View */
.calendar-view {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.calendar-header button {
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 18px;
}

.calendar-header h3 {
  margin: 0;
  font-size: 18px;
}

.calendar-grid {
  display: flex;
  flex-direction: column;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  margin-bottom: 10px;
}

.weekday {
  text-align: center;
  font-weight: 600;
  font-size: 12px;
  padding: 10px;
  color: #666;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e0e0e0;
  border: 1px solid #e0e0e0;
}

.calendar-day {
  background: white;
  min-height: 100px;
  padding: 8px;
}

.calendar-day.other-month {
  background: #fafafa;
  color: #ccc;
}

.calendar-day.today {
  background: #fff8e1;
}

.day-number {
  font-weight: 600;
  margin-bottom: 5px;
  font-size: 14px;
}

.day-tasks {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.calendar-task {
  padding: 3px 6px;
  border-radius: 3px;
  font-size: 11px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.calendar-task.priority-high {
  background: #e74c3c;
  color: white;
}

.calendar-task.priority-medium {
  background: #f39c12;
  color: white;
}

.calendar-task.priority-low {
  background: #95a5a6;
  color: white;
}

/* Right Sidebar */
.right-sidebar {
  width: 200px;
  background: white;
  border-left: 1px solid #e0e0e0;
  padding: 30px 20px;
}

.right-sidebar h3 {
  font-size: 16px;
  margin-bottom: 20px;
}

.progress-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.progress-percentage {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 20px;
}

.progress-bar-wrapper {
  width: 100px;
  height: 300px;
  background: #f0f0f0;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  margin-bottom: 20px;
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: linear-gradient(to top, #4caf50, #8bc34a);
  border-radius: 20px;
  transition: height 0.3s ease;
}

.progress-stats {
  width: 100%;
}

.stat {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-label {
  font-size: 13px;
  color: #666;
}

.stat-value {
  font-weight: 600;
}

.btn-whiteboard {
  width: 100%;
  margin-top: 20px;
  padding: 12px;
  background: #000;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-whiteboard:hover {
  background: #333;
}

/* Whiteboard Modal */
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
  z-index: 2000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
}

.modal-content h2 {
  margin: 0 0 20px 0;
}

.modal-content p {
  margin: 10px 0;
}

.btn-close {
  margin-top: 20px;
  padding: 10px 20px;
  background: #000;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.whiteboard-modal {
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 900px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.whiteboard-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.whiteboard-modal-header h2 {
  margin: 0;
  font-size: 24px;
}

.btn-close-modal {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close-modal:hover {
  background: #f0f0f0;
  color: #000;
}

.whiteboard-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
  flex-wrap: wrap;
}

.whiteboard-toolbar button {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  color: #333;
}

.whiteboard-toolbar button:hover {
  background: #f5f5f5;
  color: #333;
}

.whiteboard-toolbar button.active {
  background: #000;
  color: white;
}

.whiteboard-toolbar button.active:hover {
  background: #333;
}

.whiteboard-toolbar input[type="color"] {
  width: 40px;
  height: 40px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
}

.whiteboard-canvas {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: crosshair;
  display: block;
  width: 100%;
}

.history-panel {
  position: absolute;
  right: 30px;
  top: 140px;
  width: 280px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  max-height: 400px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  z-index: 100;
}

.history-panel h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
}

.history-entry {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.history-entry:last-child {
  border-bottom: none;
}

.history-entry button {
  margin-top: 5px;
  padding: 5px 10px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #333;
}

.history-entry button:hover {
  background: #f5f5f5;
  color: #333;
}
</style>
