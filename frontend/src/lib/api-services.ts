import { apiClient } from "./utils";
import { 
  AuthResponse, 
  LoginRequest, 
  RegisterRequest, 
  ResumeOptimizationResult,
  CustomizeResumeRequest,
  DashboardData,
  Resume,
  JobDescription,
  CustomizedResume
} from "./api-types";

// Auth Services
export const authService = {
  login: (data: LoginRequest) => {
    return apiClient.post<AuthResponse>('/auth/login', data);
  },
  
  register: (data: RegisterRequest) => {
    return apiClient.post<AuthResponse>('/auth/register', data);
  },
  
  getCurrentUser: () => {
    return apiClient.get<{ user: AuthResponse['user'] }>('/auth/me');
  },
  
  logout: () => {
    return apiClient.post<{}>('/auth/logout', {});
  }
};

// Resume Services
export const resumeService = {
  // Upload and process a resume
  uploadResume: (file: File) => {
    return apiClient.uploadFile<{ resume: Resume }>('/api/process_resume', file);
  },
  
  // Get a specific resume
  getResume: (resumeId: number) => {
    return apiClient.get<{ resume: Resume }>(`/api/resume/${resumeId}`);
  },
  
  // Delete a resume
  deleteResume: (resumeId: number) => {
    return apiClient.delete<{}>(`/api/resume/${resumeId}/delete`);
  }
};

// Job Services
export const jobService = {
  // Upload job description as text
  submitJobText: (jobText: string, title?: string, company?: string) => {
    return apiClient.post<{ job: JobDescription }>('/api/job/text', { 
      job_text: jobText, 
      title, 
      company 
    });
  },
  
  // Submit job URL to extract job description
  submitJobUrl: (jobUrl: string) => {
    return apiClient.post<{ job: JobDescription }>('/api/job/url', { job_url: jobUrl });
  },
  
  // Get all jobs
  getJobs: () => {
    return apiClient.get<{ jobs: JobDescription[] }>('/api/jobs');
  }
};

// Customization Services
export const customizationService = {
  // Customize resume based on job description
  customizeResume: (data: CustomizeResumeRequest) => {
    return apiClient.post<ResumeOptimizationResult>('/api/customize-resume', data);
  },
  
  // Save a customized resume
  saveCustomization: (customizationId: number) => {
    return apiClient.post<{ success: boolean }>('/api/save_customized_resume', { 
      customization_id: customizationId 
    });
  },
  
  // Get comparison data for a customized resume
  getComparison: (resumeId: number) => {
    return apiClient.get<ResumeOptimizationResult>(`/api/compare/${resumeId}`);
  }
};

// Dashboard Services
export const dashboardService = {
  // Get dashboard data
  getDashboardData: () => {
    return apiClient.get<DashboardData>('/api/dashboard');
  }
};