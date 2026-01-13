/**
 * Vue Router configuration.
 * Defines application routes, navigation guards, and role-based access control.
 */
import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import NewUser from '../views/NewUser.vue';
import ResetPassword from '../views/ResetPassword.vue';
import UserList from '../views/UserList.vue';
import TeamList from '../views/TeamList.vue';
import TeamDetails from '../views/TeamDetails.vue';
import ProjectList from '../views/ProjectList.vue';
import CreateProject from '../views/CreateProject.vue';
import ProjectDetails from '../views/ProjectDetails.vue';
import CreateTask from '../views/CreateTask.vue';
import MyTasks from '../views/MyTasks.vue';
import Whiteboard from '../views/Whiteboard.vue';

const routes = [
  { path: '/', component: Home, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  { path: '/reset-password', component: ResetPassword },
  { 
    path: '/home', 
    component: Home, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/users', 
    component: UserList, 
    meta: { requiresAuth: true, role: 'admin' } 
  },
  { 
    path: '/teams', 
    component: TeamList, 
    meta: { requiresAuth: true, role: 'manager' } 
  },
  { 
    path: '/teams/:id', 
    component: TeamDetails, 
    meta: { requiresAuth: true, role: 'manager' } 
  },
  { 
    path: '/newUser', 
    component: NewUser, 
    meta: { requiresAuth: true, role: 'admin' } 
  },
  { 
    path: '/projects', 
    component: ProjectList,
    meta: { requiresAuth: true }
  },
  { 
    path: '/projects/new', 
    component: CreateProject,
    meta: { requiresAuth: true, role: 'manager' }
  },
  { 
    path: '/projects/:id', 
    component: ProjectDetails,
    meta: { requiresAuth: true }
  },
  { 
    path: '/projects/:id/tasks/new', 
    component: CreateTask,
    meta: { requiresAuth: true, role: 'manager' }
  },
  { 
    path: '/projects/:id/whiteboard', 
    component: Whiteboard,
    meta: { requiresAuth: true }
  },
  { 
    path: '/my-tasks',  
    component: MyTasks,
    meta: { requiresAuth: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  // Allow access to login and reset-password without authentication
  if (to.path === '/login' || to.path === '/reset-password') {
    next();
    return;
  }

  if (!token) {
    next('/login');
  } else if (to.meta.role && to.meta.role !== role && role !== 'admin') {
    // Simple role check: Admin can access everything, otherwise must match specific role
    // Note: The requirement says "newUser(visible only to admin)" and "project/user##(visible to manager)"
    // Admin might be able to see manager stuff too, but let's stick to strict check if implied, 
    // or allow admin to override. For now, I'll assume Admin is superuser.
    // But wait, "project/user##(visible to manager)" might mean ONLY manager. 
    // Let's stick to the requirement: "visible to manager". 
    // If role is admin, I'll allow it for now as they are "super administrator".
    
    if (to.meta.role === 'manager' && role === 'manager') {
        next();
    } else if (to.meta.role === 'admin' && role === 'admin') {
        next();
    } else {
        alert('Unauthorized');
        next(false);
    }
  } else {
    next();
  }
});

export default router;
