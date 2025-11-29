# Code Refactoring Plan - Sustainability & Maintainability Improvements

## Executive Summary
This document outlines issues found during code review that could make future maintenance difficult. The good news: **NO FUNCTIONALITY WILL BE LOST**. All changes are refactoring to use existing utility functions that were already created but not being used.

---

## Issues Identified

### 1. ❌ Hardcoded API URLs (CRITICAL)
**Problem**: `http://localhost:5001` appears 100+ times across the codebase  
**Impact**: Impossible to change API URL for production/staging without editing 100+ files  
**Solution**: Use `API_BASE_URL` from `utils/api.js`

**Example - BEFORE:**
```javascript
const response = await axios.get('http://localhost:5001/projects', {
  headers: { Authorization: `Bearer ${token}` }
});
```

**Example - AFTER:**
```javascript
import { API_BASE_URL, apiGet } from '../utils/api';
const response = await apiGet('/projects');
```

**Files Affected** (30+ files):
- `Home.vue`, `ManagerDashboard.vue`, `TeamDetails.vue`, `UserList.vue`
- `NewUser.vue`, `CreateTask.vue`, `CreateProject.vue`, `TeamList.vue`
- `MyTasks.vue`, `ProjectDetails.vue`, `ProjectList.vue`, `ResetPassword.vue`
- And more...

---

### 2. ❌ Repeated localStorage Token Retrieval (HIGH)
**Problem**: `const token = localStorage.getItem('token')` repeated 30+ times  
**Impact**: Inconsistent auth handling, hard to change storage mechanism  
**Solution**: Use `getToken()`, `getUserRole()`, `getUserId()` from `utils/auth.js`

**Example - BEFORE:**
```javascript
const token = localStorage.getItem('token');
const role = localStorage.getItem('role');
const userId = localStorage.getItem('userId');
```

**Example - AFTER:**
```javascript
import { getToken, getUserRole, getUserId } from '../utils/auth';
const token = getToken();
const role = getUserRole();
const userId = getUserId();
```

**Already Fixed:**
- ✅ `Login.vue` - Now uses `setAuthData()`
- ✅ `App.vue` - Now uses `getUserRole()` and `clearAuthData()`

---

### 3. ❌ Duplicated Formatter Functions (MEDIUM)
**Problem**: `formatDate()` and `formatStatus()` duplicated in Home.vue and ManagerDashboard.vue  
**Impact**: Bug fixes need to be applied multiple times  
**Solution**: Use functions from `utils/formatters.js`

**Example - BEFORE (in Home.vue AND ManagerDashboard.vue):**
```javascript
const formatDate = (timestamp) => {
  if (!timestamp) return 'No deadline';
  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const formatStatus = (status) => {
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};
```

**Example - AFTER:**
```javascript
import { formatDate, formatStatus } from '../utils/formatters';
// Just use the imported functions directly
```

---

### 4. ❌ Not Using API Wrapper Functions (HIGH)
**Problem**: Direct axios calls with manual header management everywhere  
**Impact**: Inconsistent error handling, repeated auth header code  
**Solution**: Use `apiGet()`, `apiPost()`, `apiPut()`, `apiDelete()` from `utils/api.js`

**Example - BEFORE:**
```javascript
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
```

**Example - AFTER:**
```javascript
import { apiGet } from '../utils/api';
try {
  const users = await apiGet('/users');
  users.value = users;
} catch (error) {
  console.error(error);
  alert('Error loading users');
}
```

---

### 5. ❌ Hardcoded Role Checks (MEDIUM)
**Problem**: `userRole === 'admin'` or `role === 'manager'` scattered throughout  
**Impact**: Typos cause security issues, hard to add new roles  
**Solution**: Use `isAdmin()`, `isManager()`, `hasRole()`, `hasAnyRole()` from `utils/auth.js`

**Example - BEFORE:**
```javascript
const userRole = ref(localStorage.getItem('role'));
if (userRole.value === 'admin' || userRole.value === 'manager') {
  // ...
}
```

**Example - AFTER:**
```javascript
import { isAdminOrManager } from '../utils/auth';
if (isAdminOrManager()) {
  // ...
}
```

**In Templates - BEFORE:**
```vue
<button v-if="userRole === 'admin' || userRole === 'manager'">
  Manage Team
</button>
```

**In Templates - AFTER:**
```vue
<script setup>
import { isAdminOrManager } from '../utils/auth';
const canManageTeams = isAdminOrManager();
</script>

<template>
  <button v-if="canManageTeams">
    Manage Team
  </button>
</template>
```

---

### 6. ❌ Duplicated Whiteboard Logic (LOW)
**Problem**: Whiteboard WebSocket code duplicated in Home.vue and ManagerDashboard.vue (800+ lines each)  
**Impact**: Bug fixes need to be applied twice  
**Solution**: Extract to composable `useWhiteboard.js`

**Recommendation**: Create `composables/useWhiteboard.js` with all whiteboard logic

---

### 7. ℹ️ Unused/Redundant Files (INFO)
**Files that appear to be placeholders or unused:**
- `Project.vue` - Only displays role, seems like a placeholder
- `check_db.py` - Duplicates initialization logic from `__init__.py`
- `node_modules/` in backend folder - Unnecessary for Python project

---

## Implementation Priority

### Phase 1: Critical (Do First) ✅ STARTED
1. ✅ Replace hardcoded API URLs with `API_BASE_URL`
2. ✅ Replace direct localStorage with auth utils  
3. ✅ Update Login.vue and App.vue as examples

### Phase 2: High (Next)
4. Replace all axios calls with API wrapper functions
5. Replace all hardcoded role checks with utility functions

### Phase 3: Medium (After)
6. Replace duplicated formatters with utility imports
7. Extract whiteboard logic to composable

### Phase 4: Cleanup (Optional)
8. Remove unused files
9. Add JSDoc comments to utility functions
10. Create unit tests for utilities

---

## Benefits After Refactoring

1. **Single Source of Truth**: Change API URL in one place
2. **Consistent Auth**: All auth logic centralized
3. **Type Safety**: Easier to add TypeScript later
4. **Easier Testing**: Utilities can be unit tested
5. **Better Error Handling**: Centralized error handling
6. **DRY Principle**: Don't Repeat Yourself
7. **Easier Onboarding**: New devs see patterns immediately

---

## Existing Utility Files (Already Created, Just Not Used!)

### ✅ `utils/api.js`
```javascript
export const API_BASE_URL = 'http://localhost:5001';
export function getAuthHeaders()
export async function apiGet(endpoint)
export async function apiPost(endpoint, data)
export async function apiPut(endpoint, data)
export async function apiDelete(endpoint)
```

### ✅ `utils/auth.js`
```javascript
export function getUserRole()
export function getUserId()
export function getUsername()
export function getToken()
export function isAuthenticated()
export function hasRole(role)
export function hasAnyRole(roles)
export function setAuthData(token, role, userId, username)
export function clearAuthData()
export function isAdmin()
export function isManager()
export function isAdminOrManager()
```

### ✅ `utils/formatters.js`
```javascript
export function formatDate(timestamp)
export function formatDateTime(timestamp)
export function formatStatus(status)
export function capitalize(str)
export function getInitials(firstName, lastName)
```

### ✅ `utils/constants.js`
```javascript
export const ROLE_ADMIN = 'admin';
export const ROLE_MANAGER = 'manager';
export const ROLE_USER = 'user';
export const STATUS_TODO = 'to_do';
export const STATUS_IN_PROGRESS = 'in_progress';
// ... and more
```

---

## Risk Assessment

### ⚠️ Risks
- Large number of files to update
- Need thorough testing after changes

### ✅ Mitigations
- Keep old code in comments during transition
- Test each view after updating
- Use git commits per file/feature
- All utilities already exist and are working

---

## Testing Checklist

After each file is refactored:
- [ ] Login/Logout works
- [ ] Token is properly set and retrieved
- [ ] API calls return data correctly
- [ ] Role-based UI shows/hides correctly
- [ ] Date formatting displays correctly
- [ ] No console errors
- [ ] Dark mode still works

---

## Next Steps

1. Review this plan with team
2. Create feature branch: `refactor/code-sustainability`
3. Update files one by one (or in small batches)
4. Test thoroughly after each batch
5. Merge to main when complete

---

## Sample Refactored File

See `Login.vue` and `App.vue` for completed examples showing:
- ✅ Using `API_BASE_URL` instead of hardcoded URL
- ✅ Using `setAuthData()` instead of multiple localStorage.setItem()
- ✅ Using `clearAuthData()` instead of multiple localStorage.removeItem()
- ✅ Using `getUserRole()` instead of localStorage.getItem('role')

---

**Remember: ALL functionality remains the same. We're just using the utilities that already exist!**
