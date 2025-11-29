<template>
  <div class="dashboard">
    <!-- Dashboard (Shared for all roles) -->
    <div class="manager-view">
    <!-- Left Sidebar -->
    <aside class="left-sidebar">
      <div class="sidebar-section">
        <h3>Projects</h3>
        <input v-model="projectSearchQuery" placeholder="Filter projects..." class="sidebar-search" />
        <div class="project-list">
          <div
            v-for="project in filteredProjects"
            :key="project.projectId"
            :class="['project-item', { active: selectedProject?.projectId === project.projectId }]"
          >
            <div class="project-main" @click="selectProject(project)">
              <span class="project-indicator" :class="{ active: selectedProject?.projectId === project.projectId }"></span>
              {{ project.name }}
            </div>
            <button @click.stop="toggleProjectMenu(project.projectId)" class="project-menu-btn">⋯</button>
            <div v-if="activeProjectMenu === project.projectId" class="project-context-menu">
              <div @click="viewMyTasks(project)" class="menu-item">📄 My Tasks</div>
              <div @click="viewProjectDetails(project)" class="menu-item">📊 Project Details</div>
            </div>
          </div>
        </div>
      </div>

      <div class="sidebar-section" v-if="selectedProject">
        <h3>Teams</h3>
        <input v-model="teamSearchQuery" placeholder="Filter teams..." class="sidebar-search" />
        <div class="team-list">
          <div
            v-for="team in filteredTeams"
            :key="team.teamId"
            :class="['team-item', { active: selectedTeam?.teamId === team.teamId }]"
          >
            <div class="team-main" @click="selectTeam(team)">
              <span class="team-indicator" :class="{ active: selectedTeam?.teamId === team.teamId }"></span>
              {{ team.name }}
            </div>
            <button v-if="userRole === 'admin' || userRole === 'manager'" @click.stop="toggleTeamMenu(team.teamId)" class="team-menu-btn">⋯</button>
            <div v-if="activeTeamMenu === team.teamId" class="team-context-menu">
              <div @click="manageTeam(team)" class="menu-item">⚙️ Manage Team</div>
            </div>
          </div>
        </div>
      </div>

      <div class="sidebar-section" v-if="selectedTeam">
        <h3>Team Members</h3>
        <input v-model="memberSearchQuery" placeholder="Filter members..." class="sidebar-search" />
        <div class="member-list">
          <div v-for="member in filteredMembers" :key="member.userId" 
               :class="['member-item', { active: selectedUser?.userId === member.userId }]"
               @click="selectUser(member)">
            <span class="member-indicator" :class="{ active: selectedUser?.userId === member.userId }"></span>
            <div class="member-avatar">{{ member.firstName[0] }}{{ member.lastName[0] }}</div>
            <span>{{ member.firstName }} {{ member.lastName }}</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- User Details Sidebar -->
    <aside v-if="selectedUser" class="user-details-sidebar">
      <div class="user-details-header">
        <h3>User Details</h3>
        <button @click="selectedUser = null" class="btn-close-sidebar">×</button>
      </div>
      <div class="user-details-content">
        <div class="detail-group">
          <label>First Name</label>
          <p>{{ selectedUser.firstName }}</p>
        </div>
        <div class="detail-group">
          <label>Last Name</label>
          <p>{{ selectedUser.lastName }}</p>
        </div>
        <div class="detail-group">
          <label>Email</label>
          <p>{{ selectedUser.email }}</p>
        </div>
        <div class="detail-group">
          <label>Role</label>
          <p>{{ selectedUser.role?.name || 'N/A' }}</p>
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
            <input type="text" v-model="searchQuery" placeholder="Search tasks..." />
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
                <th></th>
                <th>Task ID</th>
                <th>Title</th>
                <th>Project</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in filteredTasks" :key="task.taskId" class="task-row">
                <td class="task-actions">
                  <button @click.stop="toggleMenu(task.taskId, $event)" class="menu-btn">⋯</button>
                </td>
                <td class="task-id">{{ task.jiraKey || `TASK-${task.taskId.substring(0, 5)}` }}</td>
                <td class="task-title">{{ task.name }}</td>
                <td class="task-project">{{ task.projectName }}</td>
                <td>
                  <span :class="['priority-badge', 'priority-' + task.priority]">
                    {{ task.priority }}
                  </span>
                </td>
                <td>
                  <span :class="['status-badge', 'status-' + task.status]">
                    {{ formatStatus(task.status) }}
                  </span>
                </td>
                <td class="task-date">{{ formatDate(task.deadline) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid-view">
          <div v-for="task in filteredTasks" :key="task.taskId" class="task-card">
            <div class="card-header">
              <span class="task-id">{{ task.jiraKey || `TASK-${task.taskId.substring(0, 5)}` }}</span>
              <button @click.stop="toggleMenu(task.taskId, $event)" class="menu-btn" :ref="`menuBtn_${task.taskId}`">⋯</button>
              <div v-if="activeMenu === task.taskId" 
                   :ref="'contextMenu_' + task.taskId"
                   class="context-menu" 
                   :style="menuPosition"
                   @mouseleave="showSubmenu = null">
                <div @click="viewTaskDetails(task)">View Details</div>
                <div @click="editTask(task)">Edit Task</div>
                <div class="submenu-item" 
                     @mouseenter="checkSubmenuSpace($event, 'priority')"
                     :ref="'submenuItem_priority_' + task.taskId">
                  <span>Change Priority</span>
                  <span class="arrow">{{ submenuDirection === 'left' && showSubmenu === 'priority' ? '‹' : '›' }}</span>
                  <div v-if="showSubmenu === 'priority'" 
                       :class="['submenu', submenuDirection === 'left' ? 'submenu-left' : 'submenu-right']">
                    <div @click="updateTaskPriority(task, 'low')">Low</div>
                    <div @click="updateTaskPriority(task, 'medium')">Medium</div>
                    <div @click="updateTaskPriority(task, 'high')">High</div>
                  </div>
                </div>
                <div class="submenu-item" 
                     @mouseenter="checkSubmenuSpace($event, 'status')"
                     :ref="'submenuItem_status_' + task.taskId">
                  <span>Change Status</span>
                  <span class="arrow">{{ submenuDirection === 'left' && showSubmenu === 'status' ? '‹' : '›' }}</span>
                  <div v-if="showSubmenu === 'status'" 
                       :class="['submenu', submenuDirection === 'left' ? 'submenu-left' : 'submenu-right']">
                    <div @click="updateTaskStatus(task, 'to_do')">To Do</div>
                    <div @click="updateTaskStatus(task, 'in_progress')">In Progress</div>
                    <div @click="updateTaskStatus(task, 'for_review')">For Review</div>
                    <div @click="updateTaskStatus(task, 'done')">Done</div>
                  </div>
                </div>
                <div @click="deleteTask(task)" class="delete-item">Delete Task</div>
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

    <!-- Project Progress Footer -->
    <div v-if="selectedProject" class="progress-footer">
      <div class="progress-container">
        <h3>Project Progress</h3>
        <div class="progress-info">
          <div class="progress-percentage">{{ projectProgress }}%</div>
          <div class="progress-bar-wrapper">
            <div class="progress-bar" :style="{ width: projectProgress + '%' }"></div>
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
      </div>

      <button @click="openWhiteboard" class="btn-whiteboard">
        🎨 Open Whiteboard
      </button>
    </div>

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

    <!-- Edit Task Modal -->
    <div v-if="showEditModal && editingTask" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-content edit-modal">
        <h2>Edit Task</h2>
        <div class="form-group">
          <label>Task Name</label>
          <input v-model="editingTask.name" type="text" class="form-input" />
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="editingTask.description" class="form-textarea" rows="4"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Priority</label>
            <select v-model="editingTask.priority" class="form-select">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="editingTask.status" class="form-select">
              <option value="to_do">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="for_review">For Review</option>
              <option value="done">Done</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>Deadline</label>
          <input v-model="editingTask.deadlineDate" type="date" class="form-input" />
        </div>
        <div class="modal-actions">
          <button @click="saveTaskEdit" class="btn-save">Save Changes</button>
          <button @click="showEditModal = false" class="btn-cancel">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Assignees Modal -->
    <div v-if="showAssigneesModal" class="modal-overlay" @click.self="showAssigneesModal = false">
      <div class="modal-content assignees-modal">
        <h2>Task Assignees</h2>
        <div v-if="taskAssignees.length === 0" class="empty-state">
          <p>No assignees for this task</p>
        </div>
        <div v-else class="assignees-list">
          <div v-for="assignee in taskAssignees" :key="assignee.userId" class="assignee-item">
            <div class="assignee-avatar">{{ assignee.firstName[0] }}{{ assignee.lastName[0] }}</div>
            <div class="assignee-info">
              <strong>{{ assignee.firstName }} {{ assignee.lastName }}</strong>
              <span class="assignee-email">{{ assignee.email }}</span>
            </div>
          </div>
        </div>
        <button @click="showAssigneesModal = false" class="btn-close">Close</button>
      </div>
    </div>
    </div>
  </div>

  <!-- Context Menu (Portal) -->
  <Teleport to="body">
    <!-- Manager/Admin Menu -->
    <div v-if="activeMenu && (userRole === 'manager' || userRole === 'admin')" 
         class="context-menu" 
         :style="menuPosition"
         @mouseleave="showSubmenu = null">
      <div @click="handleMenuAction(viewTaskDetails)">View Details</div>
      <div @click="handleMenuAction(editTask)">Edit Task</div>
      <div class="submenu-item" 
           @mouseenter="checkSubmenuSpace($event, 'priority')">
        <span>Change Priority</span>
        <span class="arrow">{{ submenuDirection === 'left' && showSubmenu === 'priority' ? '‹' : '›' }}</span>
        <div v-if="showSubmenu === 'priority'" 
             :class="['submenu', submenuDirection === 'left' ? 'submenu-left' : 'submenu-right']">
          <div @click="handleMenuAction(() => updateTaskPriority(currentMenuTask, 'low'))">Low</div>
          <div @click="handleMenuAction(() => updateTaskPriority(currentMenuTask, 'medium'))">Medium</div>
          <div @click="handleMenuAction(() => updateTaskPriority(currentMenuTask, 'high'))">High</div>
        </div>
      </div>
      <div class="submenu-item" 
           @mouseenter="checkSubmenuSpace($event, 'status')">
        <span>Change Status</span>
        <span class="arrow">{{ submenuDirection === 'left' && showSubmenu === 'status' ? '‹' : '›' }}</span>
        <div v-if="showSubmenu === 'status'" 
             :class="['submenu', submenuDirection === 'left' ? 'submenu-left' : 'submenu-right']">
          <div @click="handleMenuAction(() => updateTaskStatus(currentMenuTask, 'to_do'))">To Do</div>
          <div @click="handleMenuAction(() => updateTaskStatus(currentMenuTask, 'in_progress'))">In Progress</div>
          <div @click="handleMenuAction(() => updateTaskStatus(currentMenuTask, 'for_review'))">For Review</div>
          <div @click="handleMenuAction(() => updateTaskStatus(currentMenuTask, 'done'))">Done</div>
        </div>
      </div>
      <div @click="handleMenuAction(deleteTask)" class="delete-item">Delete Task</div>
    </div>

    <!-- User Menu -->
    <div v-else-if="activeMenu" 
         class="context-menu" 
         :style="menuPosition">
      <div @click="handleMenuAction(viewTaskDetails)">View Details</div>
      <div @click="handleMenuAction(viewTaskAssignees)">View Assignees</div>
      <div @click="handleMenuAction(setTaskForReview)">Set for Review</div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import { io } from 'socket.io-client';
import { useRouter } from 'vue-router';
import { apiGet, apiPut, apiDelete, API_BASE_URL } from '../utils/api';
import { getUserRole, getUsername, getUserId } from '../utils/auth';
import { formatDate, formatStatus } from '../utils/formatters';

const router = useRouter();
let socket = null;

// User role
const userRole = ref(getUserRole());
const userName = ref(getUsername() || 'User');

// State
const projects = ref([]);
const activeProjectMenu = ref(null);
const activeTeamMenu = ref(null);
const selectedProject = ref(null);
const currentTeams = ref([]);
const selectedTeam = ref(null);
const teamMembers = ref([]);
const allTasks = ref([]);
const viewMode = ref('list');
const searchQuery = ref('');
const projectSearchQuery = ref('');
const teamSearchQuery = ref('');
const memberSearchQuery = ref('');
const activeMenu = ref(null);
const currentMenuTask = ref(null);
const showSubmenu = ref(null);
const submenuDirection = ref('right');
const menuPosition = ref({});
const detailTask = ref(null);
const editingTask = ref(null);
const showEditModal = ref(false);
const selectedUser = ref(null);
const taskAssignees = ref([]);
const showAssigneesModal = ref(false);

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
const filteredProjects = computed(() => {
  let sorted = [...projects.value].sort((a, b) => a.name.localeCompare(b.name));
  if (projectSearchQuery.value) {
    const query = projectSearchQuery.value.toLowerCase();
    sorted = sorted.filter(p => p.name.toLowerCase().includes(query));
  }
  return sorted;
});

const filteredTeams = computed(() => {
  let sorted = [...currentTeams.value].sort((a, b) => a.name.localeCompare(b.name));
  if (teamSearchQuery.value) {
    const query = teamSearchQuery.value.toLowerCase();
    sorted = sorted.filter(t => t.name.toLowerCase().includes(query));
  }
  return sorted;
});

const filteredMembers = computed(() => {
  let sorted = [...teamMembers.value].sort((a, b) => {
    const nameA = `${a.firstName} ${a.lastName}`.toLowerCase();
    const nameB = `${b.firstName} ${b.lastName}`.toLowerCase();
    return nameA.localeCompare(nameB);
  });
  if (memberSearchQuery.value) {
    const query = memberSearchQuery.value.toLowerCase();
    sorted = sorted.filter(m => 
      `${m.firstName} ${m.lastName}`.toLowerCase().includes(query) ||
      m.email.toLowerCase().includes(query)
    );
  }
  return sorted;
});

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
      
      const createdDate = task.createdAt ? new Date(task.createdAt * 1000) : null;
      const deadlineDate = new Date(task.deadline * 1000);
      const currentDate = new Date(currentYear.value, currentMonth.value, i);
      
      // Reset time parts to compare only dates
      currentDate.setHours(0, 0, 0, 0);
      deadlineDate.setHours(0, 0, 0, 0);
      if (createdDate) createdDate.setHours(0, 0, 0, 0);
      
      // Show task on all days from created date to deadline
      const startDate = createdDate || deadlineDate;
      return currentDate >= startDate && currentDate <= deadlineDate;
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
  try {
    const response = await apiGet('/projects');
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
  activeProjectMenu.value = null;
  await fetchProjectTasks(project.projectId);
};

const toggleProjectMenu = (projectId) => {
  activeProjectMenu.value = activeProjectMenu.value === projectId ? null : projectId;
};

const toggleTeamMenu = (teamId) => {
  activeTeamMenu.value = activeTeamMenu.value === teamId ? null : teamId;
};

const viewMyTasks = (project) => {
  activeProjectMenu.value = null;
  router.push('/my-tasks');
};

const viewProjectDetails = (project) => {
  activeProjectMenu.value = null;
  router.push(`/projects/${project.projectId}`);
};

const manageTeam = (team) => {
  activeTeamMenu.value = null;
  router.push(`/teams/${team.teamId}`);
};

const selectTeam = async (team) => {
  selectedTeam.value = team;
  await fetchTeamMembers(team.teamId);
};

const fetchProjectTasks = async (projectId) => {
  try {
    const response = await apiGet(`/projects/${projectId}`);
    
    allTasks.value = (response.data.tasks || []).map(task => ({
      ...task,
      projectName: selectedProject.value.name
    }));
  } catch (error) {
    console.error(error);
  }
};

const fetchTeamMembers = async (teamId) => {
  try {
    const response = await apiGet(`/teams/${teamId}`);
    teamMembers.value = response.data.users || [];
  } catch (error) {
    console.error(error);
  }
};

const toggleMenu = (taskId, event) => {
  const task = allTasks.value.find(t => t.taskId === taskId);
  
  if (activeMenu.value === taskId) {
    activeMenu.value = null;
    currentMenuTask.value = null;
    menuPosition.value = {};
    showSubmenu.value = null;
  } else {
    activeMenu.value = taskId;
    currentMenuTask.value = task;
    
    const button = event?.target;
    if (!button) return;
    
    const rect = button?.getBoundingClientRect?.();
    if (!rect) return;
    const menuWidth = 180;
    const windowWidth = window.innerWidth;
    
    let left = rect.left;
    
    // Check if menu would go off screen on the right
    if (rect.left + menuWidth > windowWidth - 10) {
      left = rect.right - menuWidth;
    }
    
    menuPosition.value = {
      position: 'fixed',
      top: `${rect.bottom + 4}px`,
      left: `${left}px`,
      zIndex: 10000
    };
  }
};

const checkSubmenuSpace = (event, submenuType) => {
  showSubmenu.value = submenuType;
  
  setTimeout(() => {
    const submenuItem = event.currentTarget;
    if (!submenuItem) return;
    const rect = submenuItem.getBoundingClientRect();
    const submenuWidth = 140;
    const windowWidth = window.innerWidth;
    
    // Check if there's enough space on the right
    if (rect.right + submenuWidth > windowWidth - 20) {
      submenuDirection.value = 'left';
    } else {
      submenuDirection.value = 'right';
    }
  }, 10);
};

const handleMenuAction = (action) => {
  if (typeof action === 'function') {
    action(currentMenuTask.value);
  }
  activeMenu.value = null;
  currentMenuTask.value = null;
  showSubmenu.value = null;
};

const viewTaskDetails = (task) => {
  detailTask.value = task;
  activeMenu.value = null;
  showSubmenu.value = null;
};

const editTask = (task) => {
  editingTask.value = {
    ...task,
    deadlineDate: task.deadline ? new Date(task.deadline * 1000).toISOString().split('T')[0] : ''
  };
  showEditModal.value = true;
  activeMenu.value = null;
  showSubmenu.value = null;
};

const saveTaskEdit = async () => {
  const deadlineTimestamp = editingTask.value.deadlineDate 
    ? Math.floor(new Date(editingTask.value.deadlineDate).getTime() / 1000) 
    : null;

  try {
    await apiPut(`/tasks/${editingTask.value.taskId}`, {
      name: editingTask.value.name,
      description: editingTask.value.description,
      priority: editingTask.value.priority,
      status: editingTask.value.status,
      deadline: deadlineTimestamp
    });

    // Update the task in the list
    const taskIndex = allTasks.value.findIndex(t => t.taskId === editingTask.value.taskId);
    if (taskIndex !== -1) {
      allTasks.value[taskIndex] = {
        ...allTasks.value[taskIndex],
        name: editingTask.value.name,
        description: editingTask.value.description,
        priority: editingTask.value.priority,
        status: editingTask.value.status,
        deadline: deadlineTimestamp
      };
    }

    showEditModal.value = false;
    editingTask.value = null;
  } catch (error) {
    console.error(error);
    alert('Error updating task');
  }
};

const updateTaskPriority = async (task, priority) => {
  try {
    await apiPut(`/tasks/${task.taskId}`, {
      priority
    });
    
    task.priority = priority;
    activeMenu.value = null;
    showSubmenu.value = null;
  } catch (error) {
    console.error(error);
    alert('Error changing priority');
  }
};

const updateTaskStatus = async (task, status) => {
  try {
    await apiPut(`/tasks/${task.taskId}/status`, {
      status
    });
    
    task.status = status;
    activeMenu.value = null;
    showSubmenu.value = null;
  } catch (error) {
    console.error(error);
    alert('Error changing status');
  }
};

const changePriority = async (task) => {
  const priorities = ['low', 'medium', 'high'];
  const currentIndex = priorities.indexOf(task.priority);
  const newPriority = priorities[(currentIndex + 1) % 3];
  
  try {
    await apiPut(`/tasks/${task.taskId}`, {
      priority: newPriority
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
  
  try {
    await apiPut(`/tasks/${task.taskId}/status`, {
      status: newStatus
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
  
  try {
    await apiDelete(`/tasks/${task.taskId}`);
    
    allTasks.value = allTasks.value.filter(t => t.taskId !== task.taskId);
    activeMenu.value = null;
  } catch (error) {
    console.error(error);
    alert('Error deleting task');
  }
};

const selectUser = (user) => {
  selectedUser.value = user;
};

const viewTaskAssignees = async (task) => {
  try {
    const response = await apiGet(`/tasks/${task.taskId}/assignees`);
    taskAssignees.value = response.data;
    showAssigneesModal.value = true;
    activeMenu.value = null;
  } catch (error) {
    console.error(error);
    alert('Error fetching assignees');
  }
};

const setTaskForReview = async (task) => {
  if (!confirm(`Set task "${task.name}" for review?`)) return;
  
  try {
    await apiPut(`/tasks/${task.taskId}/status`, {
      status: 'for_review'
    });
    
    task.status = 'for_review';
    activeMenu.value = null;
    alert('Task set for review. Waiting for manager approval.');
  } catch (error) {
    console.error(error);
    alert('Error setting task for review');
  }
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
  
  socket = io(API_BASE_URL);
  
  const userId = getUserId();
  const username = getUsername() || 'User';
  
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
    const userId = localStorage.getItem('userId');
    socket.emit('leave_whiteboard', {
      projectId: selectedProject.value.projectId,
      userId
    });
    // Wait for message to be sent before disconnecting
    setTimeout(() => {
      if (socket) {
        socket.disconnect();
        socket = null;
      }
    }, 100);
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
  
  const userId = getUserId();
  const username = getUsername() || 'User';
  
  socket.emit('cursor_move', {
    projectId: selectedProject.value.projectId,
    userId,
    username,
    position: { x, y }
  });
};

const loadWhiteboard = async () => {
  if (!selectedProject.value) return;
  
  try {
    const response = await apiGet(`/projects/${selectedProject.value.projectId}/whiteboard`);
    
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
    const userId = getUserId();
    const username = getUsername() || 'User';
    
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
  
  const userId = getUserId();
  const username = getUsername() || 'User';
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
    const userId = localStorage.getItem('userId');
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
    if (!e.target.closest('.context-menu') && !e.target.closest('.menu-btn')) {
      activeMenu.value = null;
      currentMenuTask.value = null;
      showSubmenu.value = null;
    }
  });
});

onBeforeUnmount(() => {
  disconnectWebSocket();
});
</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
  background: var(--bg-secondary);
}

.left-sidebar {
  width: 250px;
  background: var(--card-bg);
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
  color: var(--text-secondary);
  text-transform: uppercase;
}

.sidebar-search {
  width: 100%;
  padding: 6px 10px;
  margin-bottom: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.sidebar-search::placeholder {
  color: var(--text-secondary);
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
  position: relative;
  justify-content: space-between;
}

.project-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.team-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.project-menu-btn,
.team-menu-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  color: var(--text-secondary);
  opacity: 0;
  transition: opacity 0.2s;
}

.project-item:hover .project-menu-btn,
.team-item:hover .team-menu-btn {
  opacity: 1;
  color: var(--text-secondary)
}

.project-menu-btn:hover,
.team-menu-btn:hover {
  color: var(--text-primary);
}

.project-context-menu,
.team-context-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  min-width: 180px;
  margin-top: 4px;
}

.project-context-menu .menu-item,
.team-context-menu .menu-item {
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
  white-space: nowrap;
}

.project-context-menu .menu-item:hover,
.team-context-menu .menu-item:hover {
  background: var(--bg-secondary);
}

.project-context-menu .menu-item:first-child,
.team-context-menu .menu-item:first-child {
  border-radius: 6px 6px 0 0;
}

.project-context-menu .menu-item:last-child,
.team-context-menu .menu-item:last-child {
  border-radius: 0 0 6px 6px;
}

.project-item.active,
.team-item.active {
  background: #000;
  color: white;
}

.project-context-menu .menu-item:last-child {
  border-radius: 0 0 6px 6px;
}

.project-item:hover,
.team-item:hover {
  background: var(--bg-secondary);
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
  background: #666;
  margin-right: 8px;
  flex-shrink: 0;
}

.project-indicator.active {
  background: #4caf50;
}

.team-indicator,
.member-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #666;
  margin-right: 8px;
  flex-shrink: 0;
}

.team-indicator.active,
.member-indicator.active {
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
  padding-bottom: 120px;
}

.content-header {
  padding: 20px 30px;
  background: var(--card-bg);
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
  color: var(--text-secondary);
}

.empty-project-state .empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-project-state h2 {
  font-size: 24px;
  margin: 0 0 10px 0;
  color: var(--text-secondary);
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
  background: var(--card-bg);
  border-radius: 8px;
}

.search-filter {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-filter input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  width: 300px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  color: var(--text-primary);
}

.filter-btn:hover {
  background: var(--bg-secondary);
}

.view-toggles {
  display: flex;
  gap: 5px;
}

.view-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  border-radius: 6px;
  cursor: pointer;
  font-size: 24px;
  color: var(--text-primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.view-btn:hover {
  background: var(--bg-secondary);
}

.view-btn.active {
  background: var(--text-primary);
  color: var(--bg-primary);
  border-color: var(--text-primary);
}

/* List View */
.list-view {
  background: var(--card-bg);
  border-radius: 8px;
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
  color: var(--text-secondary);
}

.task-row {
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
  position: relative;
}

.task-row:hover {
  background: var(--hover-bg);
}

.tasks-table td {
  padding: 16px;
  font-size: 14px;
}

.task-id {
  color: var(--text-secondary);
  font-weight: 500;
}

.task-title {
  font-weight: 500;
  color: var(--text-primary);
}

.task-project {
  color: var(--text-secondary);
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

.status-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.status-to_do {
  background: #e0e0e0;
  color: #333;
}

.status-in_progress {
  background: #2196f3;
  color: white;
}

.status-for_review {
  background: #ff9800;
  color: white;
}

.status-done {
  background: #4caf50;
  color: white;
}

.task-date {
  color: var(--text-secondary);
  font-size: 13px;
}

.task-actions {
  position: relative;
  width: 40px;
  text-align: center;
}

.menu-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  color: var(--text-primary);
  line-height: 1;
  font-weight: bold;
  position: relative;
}

.menu-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.context-menu {
  position: fixed;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  min-width: 180px;
}

.context-menu > div:not(.submenu-item) {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  border-bottom: 1px solid #f0f0f0;
}

.context-menu div:last-child {
  border-bottom: none;
}

.context-menu > div:not(.submenu-item):hover {
  background: var(--bg-secondary);
}

.submenu-item {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  border-bottom: 1px solid #f0f0f0;
}

.submenu-item:hover {
  background: var(--bg-secondary);
}

.submenu-item .arrow {
  margin-left: 10px;
  font-size: 16px;
  color: #999;
}

.submenu {
  position: absolute;
  top: -1px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  min-width: 140px;
  z-index: 101;
  pointer-events: auto;
}

.submenu-right {
  left: 100%;
  margin-left: -8px;
}

.submenu-left {
  right: 100%;
  margin-right: -8px;
}

.submenu div {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  border-bottom: 1px solid #f0f0f0;
}

.submenu div:last-child {
  border-bottom: none;
}

.submenu div:hover {
  background: var(--bg-secondary);
}

.delete-item {
  color: #e74c3c !important;
}

.delete-item:hover {
  background: #fee !important;
}

/* Grid View */
.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.task-card {
  background: var(--card-bg);
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
  position: relative;
}

.task-card h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.task-card p {
  color: var(--text-secondary);
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
  color: var(--text-secondary);
  font-size: 13px;
}

/* Calendar View */
.calendar-view {
  background: var(--card-bg);
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
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 18px;
  color: #333;
  font-weight: bold;
}

.calendar-header button:hover {
  background: var(--bg-secondary);
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
  color: var(--text-secondary);
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e0e0e0;
  border: 1px solid var(--border-color);
}

.calendar-day {
  background: var(--card-bg);
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

/* Progress Footer */
.progress-footer {
  position: fixed;
  bottom: 0;
  left: 250px;
  right: 0;
  background: var(--card-bg);
  border-top: 2px solid #e0e0e0;
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
  pointer-events: none;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 30px;
  pointer-events: none;
}

.progress-container h3 {
  font-size: 16px;
  margin: 0;
  color: var(--text-secondary);
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.progress-percentage {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-secondary);
}

.progress-bar-wrapper {
  width: 200px;
  height: 12px;
  background: #f0f0f0;
  border-radius: 6px;
  position: relative;
  overflow: hidden;
}

.progress-bar {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(to right, #4caf50, #8bc34a);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.progress-stats {
  display: flex;
  gap: 20px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-value {
  font-weight: 600;
  font-size: 18px;
}

.btn-whiteboard {
  padding: 12px 24px;
  background: #000;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
  pointer-events: auto;
}

.btn-whiteboard:hover {
  background: #333;
}

.manager-view {
  display: flex;
  width: 100%;
  height: 100%;
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
  z-index: 1000;
}

.modal-content {
  background: var(--card-bg);
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

.edit-modal {
  max-width: 600px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}

.form-textarea {
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 30px;
}

.btn-save {
  padding: 10px 24px;
  background: #000;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-save:hover {
  background: #333;
}

.btn-cancel {
  padding: 10px 24px;
  background: #e0e0e0;
  color: #333;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-cancel:hover {
  background: #d0d0d0;
}

.whiteboard-modal {
  background: var(--card-bg);
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
  color: var(--text-secondary);
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
  color: var(--text-primary);
}

.whiteboard-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background: var(--bg-secondary);
  border-radius: 8px;
  flex-wrap: wrap;
}

.whiteboard-toolbar button {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  color: var(--text-primary);
}

.whiteboard-toolbar button:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.whiteboard-toolbar button.active {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.whiteboard-toolbar button.active:hover {
  opacity: 0.8;
}

.whiteboard-toolbar input[type="color"] {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
}

.whiteboard-canvas {
  background: white;
  border: 2px solid var(--border-color);
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
  background: var(--card-bg);
  border: 1px solid var(--border-color);
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
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #333;
}

.history-entry button:hover {
  background: var(--bg-secondary);
  color: #333;
}

/* User Dashboard Styles */
.user-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.user-view h1 {
  font-size: 32px;
  margin-bottom: 10px;
}

.user-view > p {
  color: var(--text-secondary);
  margin-bottom: 40px;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--card-bg);
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.stat-number {
  font-size: 48px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 20px 0;
}

.stat-link {
  display: inline-block;
  margin-top: 15px;
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 500;
}

.stat-link:hover {
  text-decoration: underline;
}

.manager-view {
  display: flex;
  width: 100%;
  height: 100%;
}

/* User Details Sidebar */
.user-details-sidebar {
  width: 320px;
  background: var(--card-bg);
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 50;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
}

.user-details-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-details-header h3 {
  margin: 0;
  font-size: 18px;
}

.btn-close-sidebar {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close-sidebar:hover {
  background: var(--bg-secondary);
}

.user-details-content {
  padding: 20px;
  overflow-y: auto;
}

.detail-group {
  margin-bottom: 20px;
}

.detail-group label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin-bottom: 5px;
  font-weight: 600;
}

.detail-group p {
  margin: 0;
  font-size: 16px;
  color: #333;
}

/* Member Item Active State */
.member-item.active {
  background: #e3f2fd;
  border-left: 3px solid #1976d2;
}

/* Assignees Modal */
.assignees-modal {
  max-width: 500px !important;
}

.assignees-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin: 20px 0;
  max-height: 400px;
  overflow-y: auto;
}

.assignee-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.assignee-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  flex-shrink: 0;
}

.assignee-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.assignee-info strong {
  color: #333;
  font-size: 16px;
}

.assignee-email {
  color: var(--text-secondary);
  font-size: 14px;
}

.assignees-modal .empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* User Details Sidebar */
.user-details-sidebar {
  position: fixed;
  right: 0;
  top: 0;
  width: 350px;
  height: 100%;
  background: var(--card-bg);
  border-left: 1px solid #e0e0e0;
  box-shadow: -2px 0 10px rgba(0,0,0,0.1);
  z-index: 50;
  display: flex;
  flex-direction: column;
}

.user-details-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.user-details-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.btn-close-sidebar {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close-sidebar:hover {
  background: #e0e0e0;
  color: #333;
}

.user-details-content {
  padding: 20px;
  overflow-y: auto;
}

.detail-group {
  margin-bottom: 20px;
}

.detail-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

.detail-group p {
  margin: 0;
  font-size: 16px;
  color: #333;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.member-item.active {
  background: #e3f2fd;
  border-left: 3px solid #2196f3;
}
</style>


