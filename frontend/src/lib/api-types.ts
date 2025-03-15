// API types for ResumeRocket

// User related types
export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  created_at: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

// Resume related types
export interface Resume {
  id: number;
  user_id: number;
  filename: string;
  content: string;
  created_at: string;
  ats_score?: number;
}

export interface JobDescription {
  id: number;
  user_id: number;
  title?: string;
  company?: string;
  content: string;
  source_url?: string;
  created_at: string;
}

export interface CustomizedResume {
  id: number;
  user_id: number;
  resume_id: number;
  job_id: number;
  original_content: string;
  customized_content: string;
  original_ats_score?: number;
  improved_ats_score?: number;
  customization_level: string;
  created_at: string;
  comparison_data?: string; // JSON string containing comparison information
  optimization_plan?: string; // JSON string containing optimization plan
  industry?: string;
}

export interface ResumeOptimizationResult {
  customized_resume: CustomizedResume;
  original_resume: Resume;
  job_description: JobDescription;
}

// Request types
export interface CustomizeResumeRequest {
  resume_id: number;
  job_id: number;
  customization_level: string;
  industry?: string;
}

// Dashboard types
export interface DashboardStats {
  total_resumes: number;
  total_jobs: number;
  total_customizations: number;
  average_improvement: number;
}

export interface RecentOptimization {
  id: number;
  job_title?: string;
  company?: string;
  match_score: number;
  date: string;
  logo_url?: string;
}

export interface SavedJob {
  id: number;
  title?: string;
  company?: string;
  date: string;
  status?: string;
}

export interface DashboardData {
  stats: DashboardStats;
  recent_optimizations: RecentOptimization[];
  saved_jobs: SavedJob[];
  optimization_history: {
    date: string;
    count: number;
  }[];
}