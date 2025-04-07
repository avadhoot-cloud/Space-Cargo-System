// frontend/src/services/api.jsx

import axios from 'axios';

// Create axios instance with base URL from environment variable
const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api'
});

// Request interceptor
API.interceptors.request.use(
  (config) => {
    // You can add auth tokens here if needed
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
API.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.data) {
      console.error('API Response Error:', error.response.data);
    } else {
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API service object
const apiService = {
  // Placement APIs
  placement: {
    getStatistics: () => API.get('/placement/statistics'),
    processData: () => API.post('/placement/process'),
    getResults: () => API.get('/placement/results'),
    getRecommendations: () => API.get('/placement/recommendations'),
    placeItem: (itemId, containerId, userId = 'system') => API.post('/placement/place', {
      item_id: itemId,
      container_id: containerId,
      user_id: userId
    }),
  },
  
  // Search and Retrieval APIs
  search: {
    findItem: (itemId, itemName) => {
      const params = {};
      if (itemId) params.item_id = itemId;
      if (itemName) params.item_name = itemName;
      return API.get('/search', { params });
    },
    retrieveItem: (itemId, userId = 'system') => API.post('/retrieve', {
      item_id: itemId,
      user_id: userId
    }),
  },
  
  // Waste Management APIs
  waste: {
    identify: () => API.get('/waste/identify'),
    returnPlan: (undockingContainerId, undockingDate, maxWeight) => API.post('/waste/return-plan', {
      undockingContainerId,
      undockingDate,
      maxWeight
    }),
    completeUndocking: (undockingContainerId) => API.post('/waste/complete-undocking', {
      undockingContainerId
    }),
  },
  
  // Time Simulation API
  simulation: {
    simulateDays: (numOfDays, itemsToBeUsedPerDay = []) => API.post('/simulate/day', {
      numOfDays,
      itemsToBeUsedPerDay
    }),
    simulateToDate: (toTimestamp, itemsToBeUsedPerDay = []) => API.post('/simulate/day', {
      toTimestamp,
      itemsToBeUsedPerDay
    }),
  },
  
  // Import/Export APIs
  data: {
    importItems: (formData) => API.post('/import/items', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }),
    importContainers: (formData) => API.post('/import/containers', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }),
    exportArrangement: () => API.get('/export/arrangement'),
    getContainers: () => API.get('/containers/'),
    getItems: () => API.get('/items/'),
  },
  
  // Logging API
  logs: {
    getLogs: (startDate, endDate, itemId, userId, actionType) => {
      const params = {};
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      if (itemId) params.itemId = itemId;
      if (userId) params.userId = userId;
      if (actionType) params.actionType = actionType;
      return API.get('/logs', { params });
    },
  },
};

export default apiService;