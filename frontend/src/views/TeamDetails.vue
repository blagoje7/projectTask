<template>
  <div class="team-details" v-if="team">
    <div class="header">
      <h1>Team: {{ team.name }}</h1>
      <router-link to="/teams" class="btn-back">← Back to Teams</router-link>
    </div>
    
    <div class="section">
      <h2>Current Members ({{ team.users?.length || 0 }})</h2>
      <div v-if="!team.users || team.users.length === 0" class="no-members">
        <p>No members yet. Add members below!</p>
      </div>
      <div v-else>
        <!-- Managers Section -->
        <div v-if="groupedCurrentMembers.managers.length > 0" class="role-group">
          <h3 class="role-header">Managers ({{ groupedCurrentMembers.managers.length }})</h3>
          <ul class="members-list">
            <li v-for="user in groupedCurrentMembers.managers" :key="user.userId" class="member-item">
              <div class="member-info">
                <strong>{{ user.email }}</strong>
                <span v-if="user.firstName || user.lastName" class="member-name">
                  ({{ user.firstName }} {{ user.lastName }})
                </span>
                <span class="member-role">{{ user.role?.name || 'N/A' }}</span>
              </div>
              <button @click="removeMember(user.email)" class="btn-remove">Remove</button>
            </li>
          </ul>
        </div>
        
        <!-- Users Section -->
        <div v-if="groupedCurrentMembers.users.length > 0" class="role-group">
          <h3 class="role-header">Users ({{ groupedCurrentMembers.users.length }})</h3>
          <ul class="members-list">
            <li v-for="user in groupedCurrentMembers.users" :key="user.userId" class="member-item">
              <div class="member-info">
                <strong>{{ user.email }}</strong>
                <span v-if="user.firstName || user.lastName" class="member-name">
                  ({{ user.firstName }} {{ user.lastName }})
                </span>
                <span class="member-role">{{ user.role?.name || 'N/A' }}</span>
              </div>
              <button @click="removeMember(user.email)" class="btn-remove">Remove</button>
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="section add-member-section">
      <h2>Add Member</h2>
      <div class="add-member-form">
        <div class="form-group">
          <select v-model="newMemberEmail" class="user-select">
            <option value="">-- Select a user --</option>
            <optgroup v-if="groupedAvailableUsers.managers.length > 0" label="Managers">
              <option 
                v-for="user in groupedAvailableUsers.managers" 
                :key="user.userId" 
                :value="user.email"
              >
                {{ user.email }} ({{ user.firstName }} {{ user.lastName }})
              </option>
            </optgroup>
            <optgroup v-if="groupedAvailableUsers.users.length > 0" label="Users">
              <option 
                v-for="user in groupedAvailableUsers.users" 
                :key="user.userId" 
                :value="user.email"
              >
                {{ user.email }} ({{ user.firstName }} {{ user.lastName }})
              </option>
            </optgroup>
          </select>
          <button @click="addMember" :disabled="!newMemberEmail" class="btn-add">Add to Team</button>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="loading">
    <p>Loading team...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { apiGet, apiPost, apiDelete } from '../utils/api';
import { useRoute } from 'vue-router';

const route = useRoute();
const team = ref(null);
const allUsers = ref([]);
const newMemberEmail = ref('');

const availableUsers = computed(() => {
  if (!team.value || !allUsers.value) return [];
  const teamUserEmails = team.value.users?.map(u => u.email) || [];
  return allUsers.value.filter(user => !teamUserEmails.includes(user.email));
});

const groupedAvailableUsers = computed(() => {
  const users = availableUsers.value;
  
  const managers = users
    .filter(u => (u.role?.name || u.role) === 'manager')
    .sort((a, b) => {
      const emailA = a.email.toLowerCase();
      const emailB = b.email.toLowerCase();
      return emailA.localeCompare(emailB);
    });
  
  const regularUsers = users
    .filter(u => (u.role?.name || u.role) === 'user')
    .sort((a, b) => {
      const emailA = a.email.toLowerCase();
      const emailB = b.email.toLowerCase();
      return emailA.localeCompare(emailB);
    });
  
  return {
    managers,
    users: regularUsers
  };
});

const groupedCurrentMembers = computed(() => {
  if (!team.value || !team.value.users) return { managers: [], users: [] };
  
  const managers = team.value.users
    .filter(u => (u.role?.name || u.role) === 'manager')
    .sort((a, b) => {
      const emailA = a.email.toLowerCase();
      const emailB = b.email.toLowerCase();
      return emailA.localeCompare(emailB);
    });
  
  const regularUsers = team.value.users
    .filter(u => (u.role?.name || u.role) === 'user')
    .sort((a, b) => {
      const emailA = a.email.toLowerCase();
      const emailB = b.email.toLowerCase();
      return emailA.localeCompare(emailB);
    });
  
  return {
    managers,
    users: regularUsers
  };
});

const fetchTeam = async () => {
  try {
    const response = await apiGet(`/teams/${route.params.id}`);
    team.value = response.data;
  } catch (error) {
    console.error(error);
    alert('Error loading team details');
  }
};

const fetchAllUsers = async () => {
  try {
    const response = await apiGet('/users');
    allUsers.value = response.data;
  } catch (error) {
    console.error('Error loading users:', error);
  }
};

const addMember = async () => {
  if (!newMemberEmail.value) {
    alert('Please select a user');
    return;
  }
  
  try {
    await apiPost(`/teams/${route.params.id}/users`, {
      email: newMemberEmail.value
    });
    newMemberEmail.value = '';
    alert('Member added successfully!');
    await fetchTeam();
  } catch (error) {
    console.error(error);
    alert(error.response?.data?.msg || 'Error adding member');
  }
};

const removeMember = async (email) => {
  if (!confirm(`Remove ${email} from this team?`)) return;
  
  try {
    await apiDelete(`/teams/${route.params.id}/users`, {
      email
    });
    alert('Member removed successfully!');
    await fetchTeam();
  } catch (error) {
    console.error(error);
    alert(error.response?.data?.msg || 'Error removing member');
  }
};

onMounted(async () => {
  await Promise.all([fetchTeam(), fetchAllUsers()]);
});
</script>

<style scoped>
.team-details {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h1 {
  margin: 0;
}

.btn-back {
  padding: 8px 16px;
  background: #666;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
}

.btn-back:hover {
  background: #555;
}

.role-group {
  margin-bottom: 20px;
}

.role-header {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 10px 0;
  padding-bottom: 5px;
  border-bottom: 2px solid var(--border-color);
}

.section {
  background: var(--card-bg);
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.section h2 {
  margin-top: 0;
  color: var(--text-primary);
  font-size: 18px;
}

.no-members {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
}

.members-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

.member-item:last-child {
  border-bottom: none;
}

.member-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.member-info strong {
  color: var(--text-primary);
}

.member-name {
  color: var(--text-secondary);
  font-size: 14px;
}

.member-role {
  background: #42b983;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  text-transform: capitalize;
}

.btn-remove {
  padding: 6px 12px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.btn-remove:hover {
  background: #c0392b;
}

.add-member-section {
  background: var(--bg-secondary);
  
}

.form-group {
  display: flex;
  gap: 10px;
}

.user-select {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  background: var(--card-bg);
  color: var(--text-primary);
}

.btn-add {
  padding: 10px 20px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
}

.btn-add:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-add:hover:not(:disabled) {
  background: #359268;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}
</style>
