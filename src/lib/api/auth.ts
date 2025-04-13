
import { apiRequest } from './config';

export interface LoginData {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  requires_two_factor?: boolean;
}

export interface UserProfile {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  full_name: string;
  role: string;
}

export const login = async (data: LoginData): Promise<TokenResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', data.username);
  formData.append('password', data.password);
  
  const response = await apiRequest('/auth/login', 'POST', formData.toString(), {
    'Content-Type': 'application/x-www-form-urlencoded',
  });
  
  // Store token in localStorage
  if (response.access_token) {
    localStorage.setItem('token', response.access_token);
  }
  
  return response;
};

export const verifyTwoFactor = async (code: string): Promise<TokenResponse> => {
  const response = await apiRequest('/auth/verify-two-factor', 'POST', { code });
  
  // Update token in localStorage
  if (response.access_token) {
    localStorage.setItem('token', response.access_token);
  }
  
  return response;
};

export const logout = async (): Promise<void> => {
  await apiRequest('/auth/logout', 'POST');
  localStorage.removeItem('token');
};

export const getCurrentUser = async (): Promise<UserProfile> => {
  return apiRequest('/auth/me');
};

export const refreshToken = async (): Promise<TokenResponse> => {
  const response = await apiRequest('/auth/refresh-token', 'POST');
  
  if (response.access_token) {
    localStorage.setItem('token', response.access_token);
  }
  
  return response;
};
