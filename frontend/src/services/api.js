
import axios from 'axios';
import { API_BASE_URL, ENDPOINTS } from './constants';


const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, 
  headers: {
    'Content-Type': 'application/json',
  },
});


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


api.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
    
      const message = error.response.data?.detail || 
                     error.response.data?.message || 
                     `Server error: ${error.response.status}`;
      throw new Error(message);
    } else if (error.request) {
      throw new Error('Network error: Unable to connect to server');
    } else {
      throw new Error(`Request failed: ${error.message}`);
    }
  }
);


export const optimizationAPI = {
  optimize: async (requestData) => {
    const response = await api.post(ENDPOINTS.OPTIMIZE, requestData);
    return response.data;
  },


  checkHealth: async () => {
    const response = await api.get(ENDPOINTS.OPTIMIZE_HEALTH);
    return response.data;
  }
};

export const healthAPI = {
  checkHealth: async () => {
    const response = await api.get(ENDPOINTS.HEALTH);
    return response.data;
  }
};

export default api;
