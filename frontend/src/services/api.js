import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions for containers
export const fetchContainers = async (params = {}) => {
  try {
    const response = await api.get('/search/containers', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching containers:', error);
    throw error;
  }
};

export const createContainer = async (containerData) => {
  try {
    const response = await api.post('/containers', containerData);
    return response.data;
  } catch (error) {
    console.error('Error creating container:', error);
    throw error;
  }
};

// API functions for items
export const fetchItems = async (params = {}) => {
  try {
    const response = await api.get('/search/items', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching items:', error);
    throw error;
  }
};

export const createItem = async (itemData) => {
  try {
    const response = await api.post('/items', itemData);
    return response.data;
  } catch (error) {
    console.error('Error creating item:', error);
    throw error;
  }
};

export const placeItem = async (itemId, containerId) => {
  try {
    const response = await api.post('/placement/items', {
      item_id: itemId,
      container_id: containerId,
    });
    return response.data;
  } catch (error) {
    console.error('Error placing item:', error);
    throw error;
  }
};

// API function for CSV upload
export const uploadCSV = async (file, type) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post(`/upload/${type}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading CSV:', error);
    throw error;
  }
};

export default api; 