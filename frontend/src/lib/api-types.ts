/**
 * General API response type
 */
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  error?: string;
}

/**
 * User model
 */
export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  is_admin: boolean;
}

/**
 * Login request parameters
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Registration request parameters
 */
export interface RegisterRequest {
  username?: string;
  name?: string;
  email: string;
  password: string;
  password_confirm?: string;
}

/**
 * Job description model
 */
export interface JobDescription {
  id: number;
  title: string;
  content: string;
  url?: string;
  company?: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

/**
 * Resume model
 */
export interface Resume {
  id: number;
  original_content: string;
  customized_content?: string;
  file_format: string;
  ats_score?: number;
  confidence?: number;
  improvement?: number;
  matching_keywords?: string[];
  missing_keywords?: string[];
  created_at: string;
  updated_at: string;
  user_id: number;
  job_description_id?: number;
  original_file?: Blob;
  customized_file?: Blob;
}

/**
 * Resume section analysis
 */
export interface SectionAnalysis {
  name: string;
  score: number;
  improvement: number;
  suggestions: string[];
}

/**
 * Resume optimization data
 */
export interface OptimizationData {
  summary: string;
  keywords_added: string[];
  keywords_removed: string[];
  formatting_improvements: string[];
  content_improvements: string[];
  sections: SectionAnalysis[];
}

/**
 * Resume comparison data
 */
export interface ComparisonData {
  added_keywords: string[];
  removed_keywords: string[];
  changed_sections: {
    name: string;
    changes: string[];
  }[];
  diff_html?: string;
}

/**
 * Resume optimization result
 */
export interface ResumeOptimizationResult {
  resume: Resume;
  job: JobDescription;
  optimization_data: OptimizationData;
  comparison_data: ComparisonData;
  improvement: number;
  original_ats_score: number;
  customized_ats_score: number;
}

/**
 * Dashboard statistics
 */
export interface DashboardStats {
  total_resumes: number;
  total_jobs: number;
  avg_improvement: number;
  last_customization: string | null;
}

/**
 * Dashboard data
 */
export interface DashboardData {
  dashboard_data: {
    resume: Resume;
    job: {
      title: string;
      url?: string;
    };
    improvement: number;
    date: string;
  }[];
  total_resumes: number;
  avg_improvement: number;
  search_query?: string;
}