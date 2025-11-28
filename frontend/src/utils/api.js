/**
 * API utility functions
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

/**
 * Get authentication headers with JWT token
 */
export function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    Authorization: `Bearer ${token}`
  };
}

/**
 * Make authenticated GET request
 */
export async function apiGet(endpoint) {
  try {
    const response = await axios.get(`${API_BASE_URL}${endpoint}`, {
      headers: getAuthHeaders()
    });
    return { data: response.data, error: null };
  } catch (error) {
    console.error(`GET ${endpoint} error:`, error);
    return { data: null, error: error.response?.data?.msg || error.message };
  }
}

/**
 * Make authenticated POST request
 */
export async function apiPost(endpoint, data) {
  try {
    const response = await axios.post(`${API_BASE_URL}${endpoint}`, data, {
      headers: getAuthHeaders()
    });
    return { data: response.data, error: null };
  } catch (error) {
    console.error(`POST ${endpoint} error:`, error);
    return { data: null, error: error.response?.data?.msg || error.message };
  }
}

/**
 * Make authenticated PUT request
 */
export async function apiPut(endpoint, data) {
  try {
    const response = await axios.put(`${API_BASE_URL}${endpoint}`, data, {
      headers: getAuthHeaders()
    });
    return { data: response.data, error: null };
  } catch (error) {
    console.error(`PUT ${endpoint} error:`, error);
    return { data: null, error: error.response?.data?.msg || error.message };
  }
}

/**
 * Make authenticated DELETE request
 */
export async function apiDelete(endpoint) {
  try {
    const response = await axios.delete(`${API_BASE_URL}${endpoint}`, {
      headers: getAuthHeaders()
    });
    return { data: response.data, error: null };
  } catch (error) {
    console.error(`DELETE ${endpoint} error:`, error);
    return { data: null, error: error.response?.data?.msg || error.message };
  }
}
