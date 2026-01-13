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
              <div @click="viewProjectDetails(project)" class="menu-item">Project Details</div>
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
        <div class="header-actions" v-if="selectedProject">
             <button @click="$router.push(`/projects/${selectedProject.projectId}/whiteboard`)" class="btn-whiteboard-home">
              🎨 Whiteboard
            </button>
        </div>
      </div>

      <!-- Tasks View -->
      <div class="tasks-container">
        <div v-if="!selectedProject" class="empty-project-state">
          <div class="empty-icon">📋</div>
          <h2>No Project Selected</h2>
          <p>Select a project from the left sidebar to view tasks and details</p>
        </div>
        
        <div v-else class="tasks-toolbar">
          <div class="task-filter-tabs">
            <button 
              :class="['filter-tab', { active: taskFilter === 'all' }]"
              @click="taskFilter = 'all'"
            >
              All Tasks ({{ allTasks.length }})
            </button>
            <button 
              :class="['filter-tab', { active: taskFilter === 'my' }]"
              @click="taskFilter = 'my'"
            >
              My Tasks ({{ myTasksCount }})
            </button>
          </div>
          
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
                <th>Assignees</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in filteredTasks" :key="task.taskId" class="task-row">
                <!-- Task Actions (Context Menu Trigger) -->
                <td class="task-actions">
                  <button 
                    v-if="task.status === 'to_do' && task.assignees?.some(a => a.userId === getUserId())"
                    @click="startTask(task, $event)" 
                    class="start-btn"
                    title="Start working on this task"
                  >
                    ▶
                  </button>
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
                <!-- Assignees Dropdown (List View) -->
                <td class="task-assignees">
                  <div class="assignees-display">
                    <span v-if="!task.assignees || task.assignees.length === 0" class="no-assignees">
                      Unassigned
                    </span>
                    <div v-else class="assignees-compact">
                      <span v-for="(assignee, index) in task.assignees.slice(0, 2)" :key="assignee.userId" class="assignee-chip-sm">
                        {{ assignee.firstName[0] }}{{ assignee.lastName[0] }}
                      </span>
                      <span v-if="task.assignees.length > 2" class="more-assignees">
                        +{{ task.assignees.length - 2 }}
                      </span>
                    </div>
                  </div>
                  <div class="assignees-dropdown-container table-dropdown">
                    <div class="assignees-trigger" @click.stop="toggleAssigneesDropdown(task.taskId)">
                      {{ task.assignees ? task.assignees.length : 0 }} ▼
                    </div>
                    <div v-if="showAssigneesDropdown === task.taskId" class="assignees-dropdown-list right-aligned">
                      <div v-if="!task.assignees || task.assignees.length === 0" class="empty-assignees">
                        No assignees
                      </div>
                      <div v-else v-for="assignee in task.assignees" :key="assignee.userId" class="assignee-list-item">
                        <div class="assignee-avatar-small">{{ assignee.firstName[0] }}{{ assignee.lastName[0] }}</div>
                        <span>{{ assignee.firstName }} {{ assignee.lastName }}</span>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid-view">
          <div v-for="task in filteredTasks" :key="task.taskId" class="task-card">
            <!-- Card Header & Actions -->
            <div class="card-header">
              <span class="task-id">{{ task.jiraKey || `TASK-${task.taskId.substring(0, 5)}` }}</span>
              <div class="card-actions">
                <button 
                  v-if="task.status === 'to_do' && task.assignees?.some(a => a.userId === getUserId())"
                  @click="startTask(task, $event)" 
                  class="start-btn-card"
                  title="Start working on this task"
                >
                  ▶ Start
                </button>
                <button @click.stop="toggleMenu(task.taskId, $event)" class="menu-btn" :ref="`menuBtn_${task.taskId}`">⋯</button>
              </div>
              <div v-if="activeMenu === task.taskId" 
                   :ref="'contextMenu_' + task.taskId"
                   class="context-menu" 
                   :style="menuPosition"
                   @mouseleave="showSubmenu = null">
                <div @click="viewTaskDetails(task)">View Details</div>
                <div v-if="userRole === 'admin' || userRole === 'manager'" @click="editTask(task)">Edit Task</div>
                <div v-if="userRole === 'admin' || userRole === 'manager'" class="submenu-item" 
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
                    <div v-if="userRole === 'admin' || userRole === 'manager'" @click="updateTaskStatus(task, 'done')">Done</div>
                  </div>
                </div>
                <div v-if="userRole === 'admin' || userRole === 'manager'" @click="deleteTask(task)" class="delete-item">Delete Task</div>
              </div>
            </div>
            <h4>{{ task.name }}</h4>
            <p>{{ task.description || 'No description' }}</p>
            
            <!-- Assignees Display -->
            <div class="assignees-section" v-if="task.assignees && task.assignees.length > 0">
              <div class="assignees-label">Assigned to:</div>
              <div class="assignees-chips">
                <span v-for="assignee in task.assignees" :key="assignee.userId" class="assignee-chip" :title="assignee.firstName + ' ' + assignee.lastName">
                  {{ assignee.firstName[0] }}{{ assignee.lastName[0] }}
                </span>
              </div>
            </div>
            <div class="assignees-section" v-else>
              <span class="no-assignees">Unassigned</span>
            </div>
            
            <!-- Assignees Dropdown -->
            <div class="assignees-dropdown-container">
              <div class="assignees-trigger" @click.stop="toggleAssigneesDropdown(task.taskId)">
                Assignees ({{ task.assignees ? task.assignees.length : 0 }}) ▼
              </div>
              <div v-if="showAssigneesDropdown === task.taskId" class="assignees-dropdown-list">
                <div v-if="!task.assignees || task.assignees.length === 0" class="empty-assignees">
                  No assignees
                </div>
                <div v-else v-for="assignee in task.assignees" :key="assignee.userId" class="assignee-list-item">
                  <div class="assignee-avatar-small">{{ assignee.firstName[0] }}{{ assignee.lastName[0] }}</div>
                  <span>{{ assignee.firstName }} {{ assignee.lastName }}</span>
                </div>
              </div>
            </div>

            <!-- Card Footer -->
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
    </div>

    <!-- Task Detail Modal -->
    <div v-if="detailTask" class="modal-overlay" @click.self="detailTask = null">
      <div class="modal-content modal-with-sidebar" @click.stop>
        <!-- Left Side: Task Details -->
        <div class="task-details-main">
          <h2>{{ detailTask.name }}</h2>
          <p>{{ detailTask.description || 'No description' }}</p>
          
          <div class="task-detail-meta">
            <div><strong>Priority:</strong> {{ detailTask.priority }}</div>
            <div><strong>Status:</strong> {{ formatStatus(detailTask.status) }}</div>
            <div v-if="detailTask.deadline">
              <strong>Deadline:</strong> {{ formatDate(detailTask.deadline) }}
            </div>
            <div v-if="detailTask.epicName">
              <strong>Epic:</strong> {{ detailTask.epicName }}
            </div>
          </div>

          <div class="assignees-section">
            <strong>Assignees:</strong>
            <div v-if="!detailTask.assignees || detailTask.assignees.length === 0" class="no-assignees">
              No assignees
            </div>
            <div v-else v-for="assignee in detailTask.assignees" :key="assignee.userId" class="assignee-item">
              {{ assignee.firstName }} {{ assignee.lastName }} ({{ assignee.email }})
            </div>
          </div>

          <div class="status-update">
            <label><strong>Update Status:</strong></label>
            <select v-model="detailTask.status" @change="updateTaskStatusFromModal">
              <option value="to_do">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="for_review">For Review</option>
              <option v-if="userRole === 'admin' || userRole === 'manager'" value="done">Done</option>
            </select>
          </div>

          <!-- Time Tracking Info -->
          <div v-if="detailTask.timeWorked || detailTask.totalTime || detailTask.startedAt" class="time-tracking-section">
            <hr class="divider" />
            <div class="time-info">
              <div v-if="detailTask.startedAt"><strong>Started:</strong> {{ formatDateTime(detailTask.startedAt) }}</div>
              <div v-if="detailTask.reviewedAt"><strong>Reviewed:</strong> {{ formatDateTime(detailTask.reviewedAt) }}</div>
              <div v-if="detailTask.completedAt"><strong>Completed:</strong> {{ formatDateTime(detailTask.completedAt) }}</div>
              <div v-if="detailTask.timeWorked" class="time-worked">
                <strong>Active Work Time:</strong> 
                <span class="highlight">{{ formatDuration(detailTask.timeWorked) }}</span>
                <span v-if="detailTask.status === 'in_progress'" class="working-now"> (currently working)</span>
              </div>
              <div v-if="detailTask.totalTime" class="time-worked"><strong>Total Time:</strong> <span class="highlight">{{ formatDuration(detailTask.totalTime) }}</span></div>
            </div>
          </div>

          <button @click="detailTask = null" class="btn-close">Close</button>
        </div>

        <!-- Right Side: Activity Timeline -->
        <div class="activity-sidebar">
          <h3>Activity Timeline</h3>
          <div class="activity-timeline-scroll">
            <div v-if="taskActivities.length === 0" class="no-activities">
              Loading activity history...
            </div>
            <div v-else v-for="activity in taskActivities" :key="activity.activityId" class="activity-item">
              <div :class="['activity-icon', getActivityClass(activity)]">
                {{ getActivityIcon(activity) }}
              </div>
              <div class="activity-content">
                <div class="activity-title">{{ getActivityTitle(activity) }}</div>
                <div class="activity-user" v-if="activity.userName">by {{ activity.userName }}</div>
                <div class="activity-time">{{ formatDateTime(activity.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
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
        <div class="form-group">
          <label>Assignees</label>
          <div v-if="availableAssignees.length === 0" class="empty-message">
            No available assignees (add teams to project first)
          </div>
          <div v-else class="assignee-list">
            <label v-for="member in availableAssignees" :key="member.userId" class="assignee-checkbox">
              <input 
                type="checkbox" 
                :value="member.userId" 
                v-model="editingTask.assigneeIds"
              />
              {{ member.firstName }} {{ member.lastName }}
            </label>
          </div>
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
// --- Imports ---
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { apiGet, apiPut, apiDelete, API_BASE_URL } from '../utils/api';
import { getUserRole, getUsername, getUserId } from '../utils/auth';
import { formatDate, formatStatus, formatDuration, formatDateTime } from '../utils/formatters';

const router = useRouter();

// --- State Management ---
// User Info
const userRole = ref(getUserRole());
const userName = ref(getUsername() || 'User');

// Project & Team Data
const projects = ref([]);
const currentTeams = ref([]);
const teamMembers = ref([]);
const allTasks = ref([]);

// Selection State
const selectedProject = ref(null);
const selectedTeam = ref(null);
const selectedUser = ref(null);

// UI State (Menus, Modals, Views)
const activeProjectMenu = ref(null);
const activeTeamMenu = ref(null);
const viewMode = ref('list');
const activeMenu = ref(null);
const currentMenuTask = ref(null);
const showSubmenu = ref(null);
const submenuDirection = ref('right');
const menuPosition = ref({});
const showAssigneesDropdown = ref(null);

// Search & Filters
const searchQuery = ref('');
const projectSearchQuery = ref('');
const teamSearchQuery = ref('');
const memberSearchQuery = ref('');
const taskFilter = ref('all'); // 'all' or 'my'

// Modals
const detailTask = ref(null);
const taskActivities = ref([]);
const editingTask = ref(null);
const showEditModal = ref(false);
const showAssigneesModal = ref(false);
const taskAssignees = ref([]);
const availableAssignees = ref([]);

// Calendar State
const currentMonth = ref(new Date().getMonth());
const currentYear = ref(new Date().getFullYear());
const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// --- Computed Properties ---
// Filtered Lists
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
  
  // Filter by assignee if 'My Tasks' is selected
  if (taskFilter.value === 'my') {
    const currentUserId = getUserId();
    tasks = tasks.filter(t => 
      t.assignees && t.assignees.some(a => a.userId === currentUserId)
    );
  }
  
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

const myTasksCount = computed(() => {
  const currentUserId = getUserId();
  return allTasks.value.filter(t => 
    t.assignees && t.assignees.some(a => a.userId === currentUserId)
  ).length;
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

// --- Methods ---

// Data Fetching
const fetchProjects = async () => {
  try {
    const response = await apiGet('/projects');
    projects.value = response.data;
    
    // Don't auto-select project - let user choose
  } catch (error) {
    console.error(error);
  }
};

// Navigation & Selection
const selectProject = async (project) => {
  selectedProject.value = project;
  currentTeams.value = project.teams || [];
  selectedTeam.value = null;
  teamMembers.value = [];
  activeProjectMenu.value = null;
  await fetchProjectTasks(project.projectId);
  await fetchProjectAssignees(project.projectId);
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

// Task Data Fetching
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

// Context Menu Logic
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
  fetchTaskActivities(task.taskId);
  activeMenu.value = null;
  showSubmenu.value = null;
};

// Fetch activity history for a task
const fetchTaskActivities = async (taskId) => {
  try {
    const response = await apiGet(`/tasks/${taskId}/activities`);
    taskActivities.value = response.data;
  } catch (error) {
    console.error('Failed to fetch task activities:', error);
    taskActivities.value = [];
  }
};

// Get icon and color for activity based on status change
const getActivityIcon = (activity) => {
  if (activity.actionType === 'created') {
    return '📋';
  }
  
  const oldStatus = activity.oldStatus;
  const newStatus = activity.newStatus;
  
  // Moving forward
  if (newStatus === 'in_progress') return '▶️';
  if (newStatus === 'for_review') return '👁️';
  if (newStatus === 'done') return '✅';
  
  // Moving backward (rejections)
  if (oldStatus === 'for_review' && newStatus === 'in_progress') return '↩️';
  if (oldStatus === 'for_review' && newStatus === 'to_do') return '🔄';
  if (oldStatus === 'in_progress' && newStatus === 'to_do') return '🔄';
  if (oldStatus === 'done') return '↩️';
  
  return '🔄';
};

// Get title for activity
const getActivityTitle = (activity) => {
  if (activity.actionType === 'created') {
    return 'Task Created';
  }
  
  const oldStatus = activity.oldStatus;
  const newStatus = activity.newStatus;
  
  // Forward progress
  if (newStatus === 'in_progress' && oldStatus === 'to_do') return 'Work Started';
  if (newStatus === 'for_review') return 'Sent for Review';
  if (newStatus === 'done') return 'Task Completed';
  
  // Backward movements (rejections)
  if (oldStatus === 'for_review' && newStatus === 'in_progress') return 'Rejected - Returned to In Progress';
  if (oldStatus === 'for_review' && newStatus === 'to_do') return 'Rejected - Returned to To Do';
  if (oldStatus === 'in_progress' && newStatus === 'to_do') return 'Moved Back to To Do';
  if (oldStatus === 'done' && newStatus === 'in_progress') return 'Reopened - Returned to In Progress';
  if (oldStatus === 'done' && newStatus === 'for_review') return 'Reopened - Returned to Review';
  if (oldStatus === 'done' && newStatus === 'to_do') return 'Reopened - Returned to To Do';
  
  return `Status Changed: ${formatStatus(oldStatus)} → ${formatStatus(newStatus)}`;
};

// Get CSS class for activity icon
const getActivityClass = (activity) => {
  if (activity.actionType === 'created') return 'created';
  
  const newStatus = activity.newStatus;
  const oldStatus = activity.oldStatus;
  
  if (newStatus === 'in_progress' && oldStatus === 'to_do') return 'in-progress';
  if (newStatus === 'for_review') return 'review';
  if (newStatus === 'done') return 'completed';
  
  // Rejections/backward movements
  if (oldStatus && newStatus && oldStatus > newStatus) return 'rejected';
  
  return 'status-change';
};

// Assignee Management
const fetchProjectAssignees = async (projectId) => {
  try {
    const projectResponse = await apiGet(`/projects/${projectId}`);
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
    availableAssignees.value = members.sort((a, b) => 
      `${a.firstName} ${a.lastName}`.localeCompare(`${b.firstName} ${b.lastName}`)
    );
  } catch (error) {
    console.error(error);
    alert('Error loading project members');
  }
};

const isAssigned = (task, user) => {
  if (!task || !task.assignees) return false;
  return task.assignees.some(a => a.userId === user.userId);
};

const toggleAssignee = async (task, user) => {
  const currentAssigneeIds = task.assignees ? task.assignees.map(a => a.userId) : [];
  const isCurrentlyAssigned = currentAssigneeIds.includes(user.userId);
  
  let newAssigneeIds;
  if (isCurrentlyAssigned) {
    newAssigneeIds = currentAssigneeIds.filter(id => id !== user.userId);
  } else {
    newAssigneeIds = [...currentAssigneeIds, user.userId];
  }
  
  try {
    await apiPut(`/tasks/${task.taskId}`, {
      assigneeIds: newAssigneeIds
    });
    
    // Update local state
    const taskIndex = allTasks.value.findIndex(t => t.taskId === task.taskId);
    if (taskIndex !== -1) {
      // We need to update the assignees list locally. 
      // Since we have the full user object, we can just add/remove it.
      let newAssignees = [...(task.assignees || [])];
      if (isCurrentlyAssigned) {
        newAssignees = newAssignees.filter(a => a.userId !== user.userId);
      } else {
        newAssignees.push(user);
      }
      
      allTasks.value[taskIndex] = {
        ...allTasks.value[taskIndex],
        assignees: newAssignees
      };
      
      // Update currentMenuTask if it's the same
      if (currentMenuTask.value && currentMenuTask.value.taskId === task.taskId) {
        currentMenuTask.value = allTasks.value[taskIndex];
      }
    }
  } catch (error) {
    console.error(error);
    alert('Error updating assignees');
  }
};

// Task Editing & CRUD
const editTask = async (task) => {
  editingTask.value = {
    ...task,
    deadlineDate: task.deadline ? new Date(task.deadline * 1000).toISOString().split('T')[0] : '',
    assigneeIds: task.assignees ? task.assignees.map(u => u.userId) : []
  };
  
  await fetchProjectAssignees(task.projectId);
  
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
      deadline: deadlineTimestamp,
      assigneeIds: editingTask.value.assigneeIds
    });

    // Update the task in the list
    const taskIndex = allTasks.value.findIndex(t => t.taskId === editingTask.value.taskId);
    if (taskIndex !== -1) {
      // Fetch updated task to get full assignee objects
      const updatedTaskResponse = await apiGet(`/tasks/${editingTask.value.taskId}/assignees`);
      const updatedAssignees = updatedTaskResponse.data;

      allTasks.value[taskIndex] = {
        ...allTasks.value[taskIndex],
        name: editingTask.value.name,
        description: editingTask.value.description,
        priority: editingTask.value.priority,
        status: editingTask.value.status,
        deadline: deadlineTimestamp,
        assignees: updatedAssignees
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
    alert(error.response?.data?.error || 'Error changing status');
  }
};

// Quick start task (set to in_progress)
const startTask = async (task, event) => {
  event.stopPropagation();
  try {
    await apiPut(`/tasks/${task.taskId}/status`, { status: 'in_progress' });
    task.status = 'in_progress';
  } catch (error) {
    console.error('Failed to start task:', error);
    alert(error.response?.data?.error || 'Failed to start task');
  }
};

// Update task status from detail modal
const updateTaskStatusFromModal = async () => {
  try {
    await apiPut(`/tasks/${detailTask.value.taskId}/status`, {
      status: detailTask.value.status
    });
    
    // Update the task in the list
    const task = allTasks.value.find(t => t.taskId === detailTask.value.taskId);
    if (task) {
      task.status = detailTask.value.status;
    }
  } catch (error) {
    console.error('Failed to update task status:', error);
    alert(error.response?.data?.error || 'Failed to update task status');
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

const toggleAssigneesDropdown = (taskId) => {
  if (showAssigneesDropdown.value === taskId) {
    showAssigneesDropdown.value = null;
  } else {
    showAssigneesDropdown.value = taskId;
  }
};

// Calendar Navigation
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

// Lifecycle Hooks
onMounted(() => {
  fetchProjects();
  
  // Close menu on outside click
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.context-menu') && !e.target.closest('.menu-btn')) {
      activeMenu.value = null;
      currentMenuTask.value = null;
      showSubmenu.value = null;
    }
    if (!e.target.closest('.assignees-dropdown-container')) {
      showAssigneesDropdown.value = null;
    }
  });
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
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  padding: 20px 0;
}

.sidebar-section {
  margin-bottom: 30px;
  padding: 0 16px;
}

.sidebar-section h3 {
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sidebar-search {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
  border: 2px solid transparent;
  border-radius: 3px;
  font-size: 14px;
  background: rgba(9, 30, 66, 0.04);
  color: var(--text-primary);
  transition: all 0.2s;
}

.sidebar-search:focus {
  background: #fff;
  border-color: var(--primary-color);
  outline: none;
}

.sidebar-search::placeholder {
  color: var(--text-secondary);
}

.project-list,
.team-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.project-item,
.team-item {
  padding: 8px 10px;
  border-radius: 3px;
  cursor: pointer;
  transition: background 0.1s;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  justify-content: space-between;
  color: var(--text-primary);
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
  font-size: 16px;
  cursor: pointer;
  padding: 2px 6px;
  color: var(--text-secondary);
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 3px;
}

.project-item:hover .project-menu-btn,
.team-item:hover .team-menu-btn {
  opacity: 1;
}

.project-menu-btn:hover,
.team-menu-btn:hover {
  background-color: rgba(9, 30, 66, 0.08);
  color: var(--text-primary);
}

.project-context-menu,
.team-context-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 3px;
  box-shadow: var(--shadow-md);
  z-index: 1000;
  min-width: 180px;
  margin-top: 4px;
}

.project-context-menu .menu-item,
.team-context-menu .menu-item {
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.1s;
  font-size: 14px;
  white-space: nowrap;
  color: var(--text-primary);
}

.project-context-menu .menu-item:hover,
.team-context-menu .menu-item:hover {
  background: var(--bg-tertiary);
}

.project-context-menu .menu-item:first-child,
.team-context-menu .menu-item:first-child {
  border-radius: 3px 3px 0 0;
}

.project-context-menu .menu-item:last-child,
.team-context-menu .menu-item:last-child {
  border-radius: 0 0 3px 3px;
}

.project-item.active,
.team-item.active {
  background: var(--bg-tertiary);
  color: var(--primary-color);
  font-weight: 500;
}

.project-item:hover,
.team-item:hover {
  background: var(--bg-tertiary);
}

.project-indicator {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  background: var(--text-secondary);
  margin-right: 8px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: white;
}

.project-indicator.active {
  background: var(--primary-color);
}

.team-indicator,
.member-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-secondary);
  margin-right: 8px;
  flex-shrink: 0;
}

.team-indicator.active,
.member-indicator.active {
  background: var(--success-color);
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
  flex-wrap: wrap;
  gap: 15px;
}

.task-filter-tabs {
  display: flex;
  gap: 8px;
  background: var(--bg-secondary);
  padding: 4px;
  border-radius: 6px;
}

.filter-tab {
  padding: 8px 16px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.filter-tab:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.filter-tab.active {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-sm);
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
  gap: 4px;
  background: var(--bg-secondary);
  padding: 2px;
  border-radius: 3px;
}

.view-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 3px;
  cursor: pointer;
  font-size: 16px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: rgba(9, 30, 66, 0.08);
  color: var(--text-primary);
}

.view-btn.active {
  background: var(--card-bg);
  color: var(--primary-color);
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
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

/* Assignee Display Styles */
.assignees-compact {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.assignee-chip-sm {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}

.no-assignees-text {
  color: var(--text-secondary);
  font-size: 13px;
  font-style: italic;
}

.assignees-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}

.assignee-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
  display: block;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.assignee-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  margin-right: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.no-assignees {
  color: var(--text-secondary);
  font-size: 13px;
  font-style: italic;
}

.more-assignees {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  margin-left: 4px;
}

.task-actions {
  position: relative;
  width: 80px;
  text-align: center;
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
}

.start-btn {
  background: var(--primary-color);
  border: none;
  color: white;
  font-size: 12px;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 4px;
  line-height: 1;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.start-btn:hover {
  background: #0052cc;
  transform: scale(1.05);
}

.start-btn:active {
  transform: scale(0.95);
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

.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.start-btn-card {
  background: var(--primary-color);
  border: none;
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.start-btn-card:hover {
  background: #0052cc;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.start-btn-card:active {
  transform: translateY(0);
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

/* Assignees Dropdown in Card */
.assignees-dropdown-container {
  position: relative;
  margin-bottom: 10px;
}

.assignees-dropdown-container.table-dropdown {
  margin-bottom: 0;
  display: inline-block;
}

.assignees-trigger {
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  border-radius: 4px;
  background: var(--bg-secondary);
  transition: background 0.2s;
}

.assignees-trigger:hover {
  background: #e0e0e0;
  color: var(--text-primary);
}

.assignees-dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 100;
  min-width: 200px;
  margin-top: 4px;
  padding: 8px 0;
  max-height: 200px;
  overflow-y: auto;
}

.assignees-dropdown-list.right-aligned {
  left: auto;
  right: 0;
}

.assignee-list-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  font-size: 13px;
  color: var(--text-primary);
}

.assignee-list-item:hover {
  background: var(--bg-secondary);
}

.assignee-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #000;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
}

.empty-assignees {
  padding: 8px 12px;
  color: var(--text-secondary);
  font-size: 13px;
  font-style: italic;
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



.manager-view {
  display: flex;
  width: 100%;
  height: 100%;
}

/* Modals */
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
  padding: 24px;
  border-radius: 3px;
  max-width: 500px;
  width: 90%;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
  max-height: 85vh;
  overflow-y: auto;
}

.modal-with-sidebar {
  display: flex;
  gap: 0;
  max-width: 1000px;
  padding: 0;
  overflow: hidden;
  max-height: 85vh;
}

.task-details-main {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  max-height: 85vh;
}

.activity-sidebar {
  width: 350px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  padding: 20px;
  display: flex;
  flex-direction: column;
  max-height: 85vh;
}

.activity-sidebar h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  flex-shrink: 0;
}

.activity-timeline-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 10px;
}

.activity-timeline-scroll::-webkit-scrollbar {
  width: 6px;
}

.activity-timeline-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.activity-timeline-scroll::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.activity-timeline-scroll::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

.modal-content h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: var(--text-primary);
}

.modal-content p {
  margin: 10px 0;
  color: var(--text-primary);
}

.time-tracking-section {
  margin-top: 20px;
  padding-top: 16px;
}

.time-tracking-section .divider {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 16px 0;
}

.time-tracking-section .time-info {
  padding: 15px;
  background: var(--bg-secondary);
  border-radius: 6px;
}

.time-tracking-section .time-info > div {
  margin: 8px 0;
  font-size: 14px;
}

.time-tracking-section p {
  margin: 8px 0;
  font-size: 14px;
}

.time-worked {
  font-size: 16px;
  margin-top: 12px;
}

.time-worked .highlight {
  color: var(--success-color);
  font-weight: 600;
  font-size: 18px;
}

.time-worked .working-now {
  color: var(--primary-color);
  font-size: 13px;
  font-style: italic;
  margin-left: 8px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.task-detail-meta, .assignees-section, .status-update {
  margin: 20px 0;
  padding: 15px;
  background: var(--bg-secondary);
  border-radius: 6px;
}

.task-detail-meta > div {
  margin: 8px 0;
  font-size: 14px;
}

.assignee-item {
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
}

.assignee-item:last-child {
  border-bottom: none;
}

.status-update label {
  display: block;
  margin-bottom: 8px;
}

.status-update select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  font-size: 14px;
}

.activity-section {
  margin: 20px 0;
  padding: 15px;
  background: var(--bg-secondary);
  border-radius: 6px;
}

.activity-section > strong {
  display: block;
  margin-bottom: 15px;
  font-size: 14px;
  color: var(--text-primary);
}

.activity-timeline {
  position: relative;
  padding-left: 40px;
}

.activity-timeline::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 10px;
  bottom: 10px;
  width: 2px;
  background: #e0e0e0;
}

.activity-timeline-scroll .activity-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  position: relative;
  padding-left: 40px;
}

.activity-timeline-scroll .activity-item:last-child {
  margin-bottom: 0;
}

.activity-timeline-scroll::before {
  content: '';
  position: absolute;
  left: 35px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e0e0e0;
}

.activity-timeline-scroll {
  position: relative;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  position: relative;
}

.activity-item:last-child {
  margin-bottom: 0;
}

.activity-icon {
  position: absolute;
  left: -40px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 50%;
  font-size: 14px;
  z-index: 1;
}

.activity-icon.created {
  border-color: #95a5a6;
}

.activity-icon.in-progress {
  border-color: #2196f3;
}

.activity-icon.review {
  border-color: #ff9800;
}

.activity-icon.completed {
  border-color: #4caf50;
}

.activity-icon.rejected {
  border-color: #e74c3c;
  background: #fff5f5;
}

.activity-icon.status-change {
  border-color: #9b59b6;
}

.no-activities {
  padding: 20px;
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 4px;
}

.activity-user {
  color: var(--primary-color);
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 2px;
}

.activity-time {
  color: var(--text-secondary);
  font-size: 13px;
}

.btn-close {
  margin-top: 20px;
  padding: 8px 16px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-weight: 500;
}

.btn-close:hover {
  background: var(--hover-bg);
}

.edit-modal {
  max-width: 600px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid var(--border-color);
  border-radius: 3px;
  font-size: 14px;
  font-family: inherit;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  border-color: var(--primary-color);
  outline: none;
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
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-save:hover {
  background: var(--primary-hover);
}

.btn-cancel {
  padding: 8px 16px;
  background: transparent;
  color: var(--text-primary);
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-cancel:hover {
  background: var(--bg-tertiary);
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
  padding: 24px;
  border-radius: 3px;
  box-shadow: var(--shadow-sm);
  text-align: center;
  border: 1px solid var(--border-color);
}

.stat-card h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-weight: 600;
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
  color: var(--primary-color);
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
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 1001;
  box-shadow: var(--shadow-lg);
}

.user-details-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-details-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
}

.btn-close-sidebar {
  background: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  transition: background 0.2s, color 0.2s;
}

.btn-close-sidebar:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
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
  font-size: 14px;
  color: var(--text-primary);
}

/* Member Item Active State */
.member-item.active {
  background: var(--bg-tertiary);
  border-left: 3px solid var(--primary-color);
}



/* Assignees Modal */
.assignees-modal {
  max-width: 500px !important;
}

.assignees-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 20px 0;
  max-height: 400px;
  overflow-y: auto;
}

.assignee-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-radius: 3px;
  border: 1px solid transparent;
}

.assignee-item:hover {
  background: var(--bg-tertiary);
}

.assignee-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--info-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.assignee-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.assignee-info strong {
  color: var(--text-primary);
  font-size: 14px;
}

.assignee-email {
  color: var(--text-secondary);
  font-size: 12px;
}

.assignees-modal .empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

/* Edit Task Modal Assignee List */
.assignee-list {
  max-height: 150px;
  overflow-y: auto;
  border: 2px solid var(--border-color);
  border-radius: 3px;
  padding: 10px;
  margin-top: 5px;
  background: var(--bg-primary);
}

.assignee-checkbox {
  display: block;
  padding: 8px;
  cursor: pointer;
  user-select: none;
  color: var(--text-primary);
  font-size: 14px;
}

.assignee-checkbox:hover {
  background: var(--bg-secondary);
  border-radius: 4px;
}

.assignee-checkbox input {
  margin-right: 10px;
  cursor: pointer;
}

.btn-whiteboard-home {
  padding: 8px 16px;
  background-color: #6610f2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-whiteboard-home:hover {
  background-color: #520dc2;
}

.header-actions {
    display: flex;
    align-items: center;
}
</style>


