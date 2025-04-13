
import { apiRequest } from './config';

// Types for patient data
export interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  medical_record_number: string;
  email: string;
  phone_number: string;
  address: string;
  emergency_contact: string;
  medical_history: string;
  allergies: string;
  current_medications: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PatientCreateData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  medical_record_number: string;
  email?: string;
  phone_number?: string;
  address?: string;
  emergency_contact?: string;
  medical_history?: string;
  allergies?: string;
  current_medications?: string;
}

interface PatientQueryParams {
  search?: string;
  is_active?: boolean;
  skip?: number;
  limit?: number;
}

// Function to fetch patients with optional filtering
export const fetchPatients = async (params: PatientQueryParams = {}): Promise<Patient[]> => {
  const queryParams = new URLSearchParams();
  
  if (params.search) queryParams.append('search', params.search);
  if (params.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());
  if (params.skip !== undefined) queryParams.append('skip', params.skip.toString());
  if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());
  
  const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
  return apiRequest(`/patients${queryString}`);
};

// Function to fetch a single patient by ID
export const fetchPatient = async (id: string): Promise<Patient> => {
  return apiRequest(`/patients/${id}`);
};

// Function to create a new patient
export const createPatient = async (data: PatientCreateData): Promise<Patient> => {
  return apiRequest('/patients', 'POST', data);
};

// Function to update a patient
export const updatePatient = async (id: string, data: Partial<PatientCreateData>): Promise<Patient> => {
  return apiRequest(`/patients/${id}`, 'PUT', data);
};

// Function to change a patient's active status
export const updatePatientStatus = async (id: string, isActive: boolean): Promise<Patient> => {
  return apiRequest(`/patients/${id}/status`, 'PUT', { is_active: isActive });
};
