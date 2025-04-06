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
  if (params.zone) queryParams.append('zone', params.zone);
  
  // Add new fillStatus parameter (full, partially, empty)
  if (params.fillStatus) queryParams.append('fill_status', params.fillStatus);
  
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
  
  // Single value filters instead of ranges
  if (params.weight) queryParams.append('weight', params.weight);
  if (params.priority) queryParams.append('priority', params.priority);
  if (params.expiryDate) queryParams.append('expiry_date', params.expiryDate);
  if (params.usageLimit) queryParams.append('usage_limit', params.usageLimit);
  if (params.preferredZone) queryParams.append('preferred_zone', params.preferredZone);
  
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