/**
 * Authentication utility functions
 */
import { LS_TOKEN, LS_ROLE, LS_USER_ID, LS_USERNAME } from './constants';

/**
 * Get current user's role
 */
export function getUserRole() {
  return localStorage.getItem(LS_ROLE);
}

/**
 * Get current user ID
 */
export function getUserId() {
  return localStorage.getItem(LS_USER_ID);
}

/**
 * Get current username
 */
export function getUsername() {
  return localStorage.getItem(LS_USERNAME);
}

/**
 * Get authentication token
 */
export function getToken() {
  return localStorage.getItem(LS_TOKEN);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
  return !!getToken();
}

/**
 * Check if user has specific role
 */
export function hasRole(role) {
  return getUserRole() === role;
}

/**
 * Check if user has any of the specified roles
 */
export function hasAnyRole(roles) {
  const userRole = getUserRole();
  return roles.includes(userRole);
}

/**
 * Set authentication data
 */
export function setAuthData(token, role, userId, username) {
  localStorage.setItem(LS_TOKEN, token);
  localStorage.setItem(LS_ROLE, role);
  localStorage.setItem(LS_USER_ID, userId);
  localStorage.setItem(LS_USERNAME, username);
}

/**
 * Clear authentication data
 */
export function clearAuthData() {
  localStorage.removeItem(LS_TOKEN);
  localStorage.removeItem(LS_ROLE);
  localStorage.removeItem(LS_USER_ID);
  localStorage.removeItem(LS_USERNAME);
}

/**
 * Check if user is admin
 */
export function isAdmin() {
  return hasRole('admin');
}

/**
 * Check if user is manager
 */
export function isManager() {
  return hasRole('manager');
}

/**
 * Check if user is admin or manager
 */
export function isAdminOrManager() {
  return hasAnyRole(['admin', 'manager']);
}
