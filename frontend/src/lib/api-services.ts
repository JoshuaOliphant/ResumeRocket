import axios from 'axios';
import { ApiResponse, JobDescription, Resume, ResumeOptimizationResult, LoginRequest, RegisterRequest, User } from './api-types';

// Function to get CSRF token from cookies
function getCsrfToken(): string | null {
  if (typeof document === 'undefined') return null;
  
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrf_token') {
      return value;
    }
  }
  return null;
}

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Allow passing cookies for CORS
});

// Add request interceptor for auth token and CSRF token
api.interceptors.request.use((config) => {
  // Add Authorization header if token exists
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Add CSRF token if it exists and it's a non-GET request
  if (config.method !== 'get') {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRF-TOKEN'] = csrfToken;
    }
  }
  
  return config;
});

// Resume service for handling resume operations
export const resumeService = {
  // Get all resumes
  getResumes: async (): Promise<ApiResponse<Resume[]>> => {
    const response = await api.get('/resumes');
    return response.data;
  },
  
  // Get a specific resume
  getResume: async (resumeId: number): Promise<ApiResponse<Resume>> => {
    const response = await api.get(`/resume/${resumeId}`);
    return response.data;
  },
  
  // Upload a resume file
  uploadResume: async (file: File): Promise<ApiResponse<Resume>> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/process-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  // Upload resume text
  uploadResumeText: async (text: string): Promise<ApiResponse<Resume>> => {
    const response = await api.post('/process-resume-text', { text });
    return response.data;
  },
  
  // Delete a resume
  deleteResume: async (resumeId: number): Promise<ApiResponse<void>> => {
    const response = await api.delete(`/resume/${resumeId}`);
    return response.data;
  },
};

// Job service for handling job operations
export const jobService = {
  // Get all jobs
  getJobs: async (): Promise<ApiResponse<JobDescription[]>> => {
    const response = await api.get('/jobs');
    return response.data;
  },
  
  // Get a specific job
  getJob: async (jobId: number): Promise<ApiResponse<JobDescription>> => {
    const response = await api.get(`/job/${jobId}`);
    return response.data;
  },
  
  // Submit job URL
  submitJobUrl: async (url: string): Promise<ApiResponse<JobDescription>> => {
    const response = await api.post('/job/url', { url });
    return response.data;
  },
  
  // Submit job text
  submitJobText: async (
    text: string,
    title: string,
    company?: string
  ): Promise<ApiResponse<JobDescription>> => {
    const response = await api.post('/job/text', {
      text,
      title,
      company,
    });
    return response.data;
  },
  
  // Delete a job
  deleteJob: async (jobId: number): Promise<ApiResponse<void>> => {
    const response = await api.delete(`/job/${jobId}`);
    return response.data;
  },
};

// Customization service for resume customization operations
export const customizationService = {
  // Customize a resume
  customizeResume: async (data: {
    resumeId: number;
    jobId: number;
    customizationLevel: string;
    industry?: string;
  }): Promise<ApiResponse<ResumeOptimizationResult>> => {
    const response = await api.post('/customize-resume', {
      resume_id: data.resumeId,
      job_id: data.jobId,
      customization_level: data.customizationLevel,
      industry: data.industry,
    });
    return response.data;
  },
  
  // Get comparison data
  getComparison: async (
    resumeId: number
  ): Promise<ApiResponse<ResumeOptimizationResult>> => {
    const response = await api.get(`/comparison/${resumeId}`);
    return response.data;
  },
};

// Auth service for authentication operations
export const authService = {
  // Login user
  login: async (credentials: LoginRequest): Promise<ApiResponse<{token: string, user: User}>> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  // Register new user
  register: async (userData: RegisterRequest): Promise<ApiResponse<{token: string, user: User}>> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // Logout user
  logout: async (): Promise<ApiResponse<void>> => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  // Get current user
  getCurrentUser: async (): Promise<ApiResponse<{user: User}>> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Refresh token
  refreshToken: async (): Promise<ApiResponse<{token: string, user: User}>> => {
    const response = await api.post('/auth/refresh');
    return response.data;
  }
};