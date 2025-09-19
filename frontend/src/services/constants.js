
// frontend/src/services/constants.js
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const ENDPOINTS = {
  HEALTH: '/api/v1/health',
  OPTIMIZE: '/api/v1/optimize',
  OPTIMIZE_HEALTH: '/api/v1/optimize/health'
};

export const DEFAULT_MAP_CENTER = [
  parseFloat(import.meta.env.VITE_MAP_CENTER_LAT) || 11.1271,
  parseFloat(import.meta.env.VITE_MAP_CENTER_LNG) || 78.6569
];

export const MAP_CONFIG = {
  DEFAULT_ZOOM: 10,
  MIN_ZOOM: 6,
  MAX_ZOOM: 18,
  TILE_URL: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  ATTRIBUTION: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
};

export const STATION_TYPES = {
  FAST: 'fast',
  REGULAR: 'regular',
  ULTRA_FAST: 'ultra_fast'
};

export const BUDGET_OPTIONS = [
  { value: 2500000, label: '₹25 Lakhs' },
  { value: 5000000, label: '₹50 Lakhs' },
  { value: 7500000, label: '₹75 Lakhs' },
  { value: 10000000, label: '₹1 Crore' }
];




