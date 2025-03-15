import { 
  useQuery, 
  useMutation, 
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions
} from '@tanstack/react-query';
import { 
  dashboardService, 
  resumeService, 
  jobService, 
  customizationService 
} from '@/lib/api-services';
import { ApiResponse } from '@/lib/utils';
import { extractQueryState } from '@/lib/react-query';
import { 
  DashboardData, 
  Resume, 
  JobDescription, 
  ResumeOptimizationResult, 
  CustomizeResumeRequest 
} from '@/lib/api-types';

// React Query Keys
export const QueryKeys = {
  dashboard: ['dashboard'],
  resumes: ['resumes'],
  resume: (id: number) => ['resume', id],
  jobs: ['jobs'],
  job: (id: number) => ['job', id],
  customization: (id: number) => ['customization', id],
};

// Dashboard hooks
export const useDashboardData = (options?: UseQueryOptions<ApiResponse<DashboardData>>) => {
  const result = useQuery({
    queryKey: QueryKeys.dashboard,
    queryFn: () => dashboardService.getDashboardData(),
    ...options,
  });

  return {
    ...extractQueryState(result),
    dashboardData: result.data?.data,
  };
};

// Resume hooks
export const useResumes = () => {
  const queryClient = useQueryClient();
  
  // Hook to get user's resumes would go here if it exists in the API
  
  // Upload resume mutation
  const uploadResumeMutation = useMutation({
    mutationFn: (file: File) => resumeService.uploadResume(file),
    onSuccess: () => {
      // Invalidate the resumes query to refetch
      queryClient.invalidateQueries({ queryKey: QueryKeys.resumes });
      // Also invalidate dashboard data as it may contain resume stats
      queryClient.invalidateQueries({ queryKey: QueryKeys.dashboard });
    },
  });
  
  // Delete resume mutation
  const deleteResumeMutation = useMutation({
    mutationFn: (resumeId: number) => resumeService.deleteResume(resumeId),
    onSuccess: () => {
      // Invalidate both resumes and dashboard queries
      queryClient.invalidateQueries({ queryKey: QueryKeys.resumes });
      queryClient.invalidateQueries({ queryKey: QueryKeys.dashboard });
    },
  });
  
  return {
    uploadResume: uploadResumeMutation,
    deleteResume: deleteResumeMutation,
  };
};

// Get single resume
export const useResume = (resumeId: number) => {
  const result = useQuery({
    queryKey: QueryKeys.resume(resumeId),
    queryFn: () => resumeService.getResume(resumeId),
    enabled: !!resumeId, // Only run query if resumeId is provided
  });
  
  return {
    ...extractQueryState(result),
    resume: result.data?.data?.resume,
  };
};

// Job hooks
export const useJobs = () => {
  const queryClient = useQueryClient();
  
  // Get all jobs
  const jobsQuery = useQuery({
    queryKey: QueryKeys.jobs,
    queryFn: () => jobService.getJobs(),
  });
  
  // Submit job text mutation
  const submitJobTextMutation = useMutation({
    mutationFn: ({ jobText, title, company }: { jobText: string; title?: string; company?: string }) => 
      jobService.submitJobText(jobText, title, company),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.jobs });
      queryClient.invalidateQueries({ queryKey: QueryKeys.dashboard });
    },
  });
  
  // Submit job URL mutation
  const submitJobUrlMutation = useMutation({
    mutationFn: (jobUrl: string) => jobService.submitJobUrl(jobUrl),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.jobs });
      queryClient.invalidateQueries({ queryKey: QueryKeys.dashboard });
    },
  });
  
  return {
    jobs: jobsQuery.data?.data?.jobs || [],
    isLoading: jobsQuery.isLoading,
    isError: jobsQuery.isError,
    error: jobsQuery.error,
    submitJobText: submitJobTextMutation,
    submitJobUrl: submitJobUrlMutation,
  };
};

// Customization hooks
export const useCustomizeResume = () => {
  const queryClient = useQueryClient();
  
  // Customize resume mutation
  const customizeResumeMutation = useMutation({
    mutationFn: (data: CustomizeResumeRequest) => customizationService.customizeResume(data),
    onSuccess: (data) => {
      // If the customization was successful, invalidate dashboard data
      if (data.data?.customized_resume) {
        queryClient.invalidateQueries({ queryKey: QueryKeys.dashboard });
      }
    },
  });
  
  // Save customization mutation
  const saveCustomizationMutation = useMutation({
    mutationFn: (customizationId: number) => customizationService.saveCustomization(customizationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.dashboard });
    },
  });
  
  return {
    customizeResume: customizeResumeMutation,
    saveCustomization: saveCustomizationMutation,
  };
};

// Get comparison data
export const useComparisonData = (resumeId: number) => {
  const result = useQuery({
    queryKey: ['comparison', resumeId],
    queryFn: () => customizationService.getComparison(resumeId),
    enabled: !!resumeId, // Only run if resumeId is provided
  });
  
  return {
    ...extractQueryState(result),
    comparisonData: result.data?.data,
  };
};