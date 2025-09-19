// frontend/src/services/api.js
import axios from 'axios';
import { API_BASE_URL, ENDPOINTS } from './constants';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for optimization requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || 
                     error.response.data?.message || 
                     `Server error: ${error.response.status}`;
      throw new Error(message);
    } else if (error.request) {
      // Request made but no response
      throw new Error('Network error: Unable to connect to server');
    } else {
      // Something else happened
      throw new Error(`Request failed: ${error.message}`);
    }
  }
);

// API methods
export const optimizationAPI = {
  // Optimize charging station locations
  optimize: async (requestData) => {
    const response = await api.post(ENDPOINTS.OPTIMIZE, requestData);
    return response.data;
  },

  // Check optimization service health
  checkHealth: async () => {
    const response = await api.get(ENDPOINTS.OPTIMIZE_HEALTH);
    return response.data;
  }
};

export const healthAPI = {
  // Check overall system health
  checkHealth: async () => {
    const response = await api.get(ENDPOINTS.HEALTH);
    return response.data;
  }
};

export default api;
