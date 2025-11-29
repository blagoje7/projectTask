<template>
  <div class="user-management">
    <h1>User Management</h1>
    
    <div class="filters">
      <input v-model="searchQuery" placeholder="Search by email or name..." class="search-input" />
      <select v-model="filterRole" class="filter-select">
        <option value="">All Roles</option>
        <option value="admin">Admin</option>
        <option value="manager">Manager</option>
        <option value="user">User</option>
      </select>
      <select v-model="filterActive" class="filter-select">
        <option value="">All Status</option>
        <option value="true">Active</option>
        <option value="false">Inactive</option>
      </select>
    </div>

    <div class="user-count">
      Total Users: {{ allFilteredUsers.length }}
    </div>

    <div v-for="group in groupedUsers" :key="group.role" class="role-group">
      <div class="group-header">
        <h3 class="role-header">{{ group.role }}s ({{ group.filteredCount }})</h3>
        <input 
          v-model="groupSearchQueries[group.role.toLowerCase()]" 
          :placeholder="`Filter ${group.role}s by name...`" 
          class="group-search-input" 
        />
      </div>
      
      <table class="user-table">
        <thead>
          <tr>
            <th>Email</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Role</th>
            <th>Status</th>
            <th>Created</th>
            <th>Teams</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in group.users" :key="user.userId" :class="{ inactive: !user.isActive }">
            <td class="email-cell">{{ user.email }}</td>
            <td>{{ user.firstName || '-' }}</td>
            <td>{{ user.lastName || '-' }}</td>
            <td>
              <span class="role-badge" :class="'role-' + (user.role?.name || user.role)">
                {{ user.role?.name || user.role }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="user.isActive ? 'active' : 'inactive'">
                {{ user.isActive ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="date-cell">{{ formatDate(user.createdAt) }}</td>
            <td class="teams-cell">
              <span v-if="user.teams && user.teams.length > 0" class="teams-count">
                {{ user.teams.length }} team(s)
              </span>
              <span v-else class="no-teams">No teams</span>
            </td>
            <td class="actions-cell">
              <button 
                @click="toggleActive(user)" 
                :class="user.isActive ? 'btn-deactivate' : 'btn-activate'"
              >
                {{ user.isActive ? 'Deactivate' : 'Activate' }}
              </button>
              <button @click="viewDetails(user)" class="btn-details">Details</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="allFilteredUsers.length === 0" class="no-data-message">
      No users found
    </div>

    <!-- User Details Modal -->
    <div v-if="selectedUser" class="modal-overlay" @click="selectedUser = null">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>User Details</h2>
          <button @click="selectedUser = null" class="btn-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <strong>User ID:</strong>
            <span>{{ selectedUser.userId }}</span>
          </div>
          <div class="detail-row">
            <strong>Email:</strong>
            <span>{{ selectedUser.email }}</span>
          </div>
          <div class="detail-row">
            <strong>First Name:</strong>
            <span>{{ selectedUser.firstName || 'Not set' }}</span>
          </div>
          <div class="detail-row">
            <strong>Last Name:</strong>
            <span>{{ selectedUser.lastName || 'Not set' }}</span>
          </div>
          <div class="detail-row">
            <strong>Role:</strong>
            <span class="role-badge" :class="'role-' + (selectedUser.role?.name || selectedUser.role)">
              {{ selectedUser.role?.name || selectedUser.role }}
            </span>
          </div>
          <div class="detail-row">
            <strong>Status:</strong>
            <span class="status-badge" :class="selectedUser.isActive ? 'active' : 'inactive'">
              {{ selectedUser.isActive ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="detail-row">
            <strong>Created:</strong>
            <span>{{ formatDate(selectedUser.createdAt) }}</span>
          </div>
          <div class="detail-row">
            <strong>Teams:</strong>
            <div v-if="selectedUser.teams && selectedUser.teams.length > 0" class="teams-list">
              <router-link 
                v-for="team in selectedUser.teams" 
                :key="team.teamId" 
                :to="`/teams/${team.teamId}`"
                class="team-item"
              >
                {{ team.name }}
              </router-link>
            </div>
            <span v-else>Not assigned to any teams</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const users = ref([]);
const selectedUser = ref(null);
const searchQuery = ref('');
const filterRole = ref('');
const filterActive = ref('');

const filteredUsers = computed(() => {
  let result = users.value;
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(user => 
      user.email.toLowerCase().includes(query) ||
      (user.firstName && user.firstName.toLowerCase().includes(query)) ||
      (user.lastName && user.lastName.toLowerCase().includes(query))
    );
  }
  
  // Role filter
  if (filterRole.value) {
    result = result.filter(user => user.role === filterRole.value);
  }
  
  // Active status filter
  if (filterActive.value !== '') {
    const isActive = filterActive.value === 'true';
    result = result.filter(user => user.isActive === isActive);
  }
  
  return result;
});

const allFilteredUsers = computed(() => filteredUsers.value);

const groupSearchQueries = ref({
  admin: '',
  manager: '',
  user: ''
});

const groupedUsers = computed(() => {
  const groups = {
    admin: [],
    manager: [],
    user: []
  };

  filteredUsers.value.forEach(user => {
    const roleName = (user.role?.name || user.role).toLowerCase();
    if (groups[roleName]) {
      groups[roleName].push(user);
    }
  });

  // Sort each group alphabetically by email
  Object.keys(groups).forEach(role => {
    groups[role].sort((a, b) => a.email.toLowerCase().localeCompare(b.email.toLowerCase()));
  });

  // Return only non-empty groups in order: admin, manager, user
  return ['admin', 'manager', 'user']
    .filter(role => groups[role].length > 0)
    .map(role => {
      const allUsers = groups[role];
      const searchQuery = groupSearchQueries.value[role];
      
      // Filter users within the group by search query
      const filteredGroupUsers = searchQuery
        ? allUsers.filter(user => 
            user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (user.firstName && user.firstName.toLowerCase().includes(searchQuery.toLowerCase())) ||
            (user.lastName && user.lastName.toLowerCase().includes(searchQuery.toLowerCase()))
          )
        : allUsers;
      
      return {
        role: role.charAt(0).toUpperCase() + role.slice(1),
        users: filteredGroupUsers,
        filteredCount: filteredGroupUsers.length
      };
    });
});

const fetchUsers = async () => {
  const token = localStorage.getItem('token');
  try {
    const response = await axios.get('http://localhost:5001/users', {
      headers: { Authorization: `Bearer ${token}` }
    });
    users.value = response.data;
  } catch (error) {
    console.error(error);
    alert('Error loading users');
  }
};

const toggleActive = async (user) => {
  const action = user.isActive ? 'deactivate' : 'activate';
  if (!confirm(`Are you sure you want to ${action} ${user.email}?`)) return;
  
  const token = localStorage.getItem('token');
  try {
    await axios.put(`http://localhost:5001/users/${user.userId}`, {
      isActive: !user.isActive
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    alert(`User ${action}d successfully!`);
    fetchUsers();
  } catch (error) {
    console.error(error);
    alert(error.response?.data?.msg || 'Error updating user');
  }
};

const viewDetails = (user) => {
  selectedUser.value = user;
};

const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

onMounted(fetchUsers);
</script>

<style scoped>
.user-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  background: var(--card-bg);
  color: var(--text-primary);
}

.filter-select {
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  background: var(--card-bg);
  color: var(--text-primary);
}

.user-count {
  margin-bottom: 10px;
  color: var(--text-secondary);
  font-size: 14px;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--card-bg);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-table th,
.user-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.user-table th {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.user-table tbody tr:hover {
  background: var(--hover-bg);
}

.user-table tbody tr.inactive {
  opacity: 0.6;
}

.email-cell {
  font-weight: 500;
  color: var(--text-primary);
}

.date-cell {
  font-size: 13px;
  color: var(--text-secondary);
}

.teams-cell {
  font-size: 13px;
}

.teams-count {
  color: #42b983;
  font-weight: 500;
}

.no-teams {
  color: #999;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.role-admin {
  background: #e74c3c;
  color: white;
}

.role-manager {
  background: #3498db;
  color: white;
}

.role-user {
  background: #95a5a6;
  color: white;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: #27ae60;
  color: white;
}

.status-badge.inactive {
  background: #95a5a6;
  color: white;
}

.actions-cell {
  display: flex;
  gap: 5px;
}

.btn-deactivate,
.btn-activate,
.btn-details {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.btn-deactivate {
  background: #e74c3c;
  color: white;
}

.btn-deactivate:hover {
  background: #c0392b;
}

.btn-activate {
  background: #27ae60;
  color: white;
}

.btn-activate:hover {
  background: #229954;
}

.btn-details {
  background: #3498db;
  color: white;
}

.btn-details:hover {
  background: #2980b9;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--card-bg);
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #999;
  line-height: 1;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.detail-row {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row strong {
  width: 150px;
  color: var(--text-secondary);
  font-size: 14px;
}

.detail-row span {
  flex: 1;
  color: #333;
  font-size: 14px;
}

.teams-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.team-item {
  padding: 6px 10px;
  background: #3498db;
  border-radius: 4px;
  font-size: 13px;
  text-decoration: none;
  color: white;
  transition: background 0.2s;
}

.team-item:hover {
  background: #2980b9;
  color: white;
}

.role-group {
  margin-bottom: 40px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.role-header {
  color: var(--text-primary);
  font-size: 20px;
  margin: 0;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--border-color);
  flex: 1;
}

.group-search-input {
  width: 300px;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  background: var(--card-bg);
  color: var(--text-primary);
}

.no-data-message {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
  font-size: 16px;
}
</style>
