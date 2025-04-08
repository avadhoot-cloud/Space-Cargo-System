// frontend/src/services/api.jsx

import axios from 'axios';

// Create axios instance with base URL from environment variable
const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api'
});

// Request interceptor
API.interceptors.request.use(
  (config) => {
    console.log(`DEBUG: API Request: ${config.method.toUpperCase()} ${config.url}`, config);
    // You can add auth tokens here if needed
    return config;
  },
  (error) => {
    console.error('DEBUG: API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
API.interceptors.response.use(
  (response) => {
    console.log(`DEBUG: API Response: ${response.config.method.toUpperCase()} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    if (error.response && error.response.data) {
      console.error('DEBUG: API Response Error:', error.response.data);
    } else {
      console.error('DEBUG: API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API service object
const apiService = {
  // Placement APIs
  placement: {
    getStatistics: async () => {
      console.log("DEBUG: API Request: /placement/statistics/");
      var res = await API.get('/placement/statistics/');
      console.log("DEBUG: API Response: /placement/statistics/", res.data);
      return res;
    },
    processData: () => API.post('/placement/process/'),
    getResults: () => API.get('/placement/results/'),
    getRecommendations: () => API.get('/placement/recommendations/'),
    placeItem: (itemId, containerId, userId = 'system') => API.post('/placement/place/', {
      item_id: itemId,
      container_id: containerId,
      user_id: userId
    }),
  },
  
  // Search and Retrieval APIs
  search: {
    findItem: (itemId, itemName) => {
      console.log("DEBUG: API Request: /placement/search/", { itemId, itemName });
      const params = {};
      if (itemId) params.item_id = itemId;
      if (itemName) params.item_name = itemName;
      return API.get('/placement/search/', { params });
    },
    retrieveItem: (itemId, userId = 'system') => {
      console.log("DEBUG: API Request: /placement/retrieve/", { itemId, userId });
      return API.post('/placement/retrieve/', {
        item_id: itemId,
        user_id: userId
      });
    },
  },
  
  // Waste Management APIs
  waste: {
    identify: () => API.get('/placement/waste/identify/'),
    returnPlan: (undockingContainerId, undockingDate, maxWeight) => API.post('/placement/waste/return-plan/', {
      undockingContainerId,
      undockingDate,
      maxWeight
    }),
    completeUndocking: (undockingContainerId) => API.post('/placement/waste/complete-undocking/', {
      undockingContainerId
    }),
  },
  
  // Time Simulation API
  simulation: {
    simulateDays: (numOfDays, itemsToBeUsedPerDay = []) => API.post('/simulation/simulate/', {
      numOfDays,
      itemsToBeUsedPerDay
    }),
    simulateToDate: (toTimestamp, itemsToBeUsedPerDay = []) => API.post('/simulation/simulate/', {
      toTimestamp,
      itemsToBeUsedPerDay
    }),
  },
  
  // Import/Export APIs
  data: {
    importItems: (formData) => API.post('/upload/items/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }),
    importContainers: (formData) => API.post('/upload/containers/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }),
    exportArrangement: () => API.get('/placement/export/arrangement/'),
    getContainers: () => API.get('/placement/containers/'),
    getItems: () => API.get('/placement/items/'),
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
      return API.get('/placement/logs/', { params });
    },
  },
};

export default apiService;