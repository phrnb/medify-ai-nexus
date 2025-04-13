
// Base URL for API calls
export const API_BASE_URL = 'http://localhost:8000/api/v1';

// Default headers for API requests
export const defaultHeaders = {
  'Content-Type': 'application/json',
};

// Function to include auth token in requests
export const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { ...defaultHeaders, Authorization: `Bearer ${token}` } : defaultHeaders;
};

// Generic API request function with error handling
export const apiRequest = async (
  endpoint: string, 
  method: string = 'GET', 
  data?: any, 
  customHeaders: Record<string, string> = {}
) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = {
    ...getAuthHeaders(),
    ...customHeaders,
  };
  
  const config: RequestInit = {
    method,
    headers,
    credentials: 'include',
  };
  
  if (data && method !== 'GET') {
    config.body = JSON.stringify(data);
  }
  
  try {
    const response = await fetch(url, config);
    
    // Handle unauthorized access
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Session expired. Please login again.');
    }
    
    // Parse JSON response if available
    const contentType = response.headers.get('content-type');
    const result = contentType && contentType.includes('application/json') 
      ? await response.json() 
      : await response.text();
    
    // Handle API errors
    if (!response.ok) {
      throw new Error(result.detail || 'An error occurred');
    }
    
    return result;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};
