const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Generic fetch function with error handling
 */
async function fetchFromApi(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, options);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `API request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API fetch error:', error);
    throw error;
  }
}

/**
 * Fetch containers with optional filter parameters
 */
export async function fetchContainers(params = {}) {
  let url = '/upload/containers';
  
  // Add query parameters if provided
  const queryParams = new URLSearchParams();
  if (params.name) queryParams.append('name', params.name);
  if (params.is_active !== undefined) queryParams.append('is_active', params.is_active);
  
  if (queryParams.toString()) {
    url += `?${queryParams.toString()}`;
  }
  
  return fetchFromApi(url);
}

/**
 * Fetch items with optional filter parameters
 */
export async function fetchItems(params = {}) {
  let url = '/upload/items';
  
  // Add query parameters if provided
  const queryParams = new URLSearchParams();
  if (params.name) queryParams.append('name', params.name);
  if (params.container_id) queryParams.append('container_id', params.container_id);
  if (params.is_placed !== undefined) queryParams.append('is_placed', params.is_placed);
  if (params.priority_min) queryParams.append('priority_min', params.priority_min);
  if (params.priority_max) queryParams.append('priority_max', params.priority_max);
  
  if (queryParams.toString()) {
    url += `?${queryParams.toString()}`;
  }
  
  return fetchFromApi(url);
}

/**
 * Upload a CSV file
 */
export async function uploadCsv(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  return fetchFromApi('/upload/csv', {
    method: 'POST',
    body: formData,
  });
}

export default {
  fetchContainers,
  fetchItems,
  uploadCsv
}; 