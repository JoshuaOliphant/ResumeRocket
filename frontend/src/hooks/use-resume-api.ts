import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { 
  resumeService, 
  jobService, 
  customizationService 
} from "@/lib/api-services";
import { ApiResponse } from "@/lib/api-types";

// Query keys for cache management
export const QueryKeys = {
  resumes: ['resumes'] as const,
  resume: (id: number) => ['resume', id] as const,
  jobs: ['jobs'] as const,
  job: (id: number) => ['job', id] as const,
  customization: (id: number) => ['customization', id] as const,
};

// Helper to extract loading, error, and data states consistently
export const extractQueryState = <T>(query: any) => {
  return {
    data: query.data?.data as T,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error?.response?.data || query.error,
  };
};

// ---- Resume Queries ---- //

export const useResumes = () => {
  const query = useQuery({
    queryKey: QueryKeys.resumes,
    queryFn: resumeService.getResumes,
  });
  
  return extractQueryState(query);
};

export const useResume = (resumeId: number) => {
  const query = useQuery({
    queryKey: QueryKeys.resume(resumeId),
    queryFn: () => resumeService.getResume(resumeId),
    enabled: !!resumeId,
  });
  
  return extractQueryState(query);
};

export const useUploadResume = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (file: File) => resumeService.uploadResume(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.resumes });
    },
  });
};

export const useUploadResumeText = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (text: string) => resumeService.uploadResumeText(text),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.resumes });
    },
  });
};

export const useDeleteResume = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (resumeId: number) => resumeService.deleteResume(resumeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.resumes });
    },
  });
};

// ---- Job Queries ---- //

export const useJobs = () => {
  const query = useQuery({
    queryKey: QueryKeys.jobs,
    queryFn: jobService.getJobs,
  });
  
  return extractQueryState(query);
};

export const useJob = (jobId: number) => {
  const query = useQuery({
    queryKey: QueryKeys.job(jobId),
    queryFn: () => jobService.getJob(jobId),
    enabled: !!jobId,
  });
  
  return extractQueryState(query);
};

export const useSubmitJobUrl = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { url: string }) => jobService.submitJobUrl(data.url),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.jobs });
    },
  });
};

export const useSubmitJobText = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { text: string; title: string; company?: string }) => 
      jobService.submitJobText(data.text, data.title, data.company),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.jobs });
    },
  });
};

export const useDeleteJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (jobId: number) => jobService.deleteJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.jobs });
    },
  });
};

// ---- Customization Queries ---- //

export const useCustomizeResume = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { 
      resumeId: number; 
      jobId: number; 
      customizationLevel: string;
      industry?: string;
    }) => customizationService.customizeResume(data),
    onSuccess: (response: ApiResponse<any>) => {
      if (response.data?.customized_resume?.id) {
        queryClient.invalidateQueries({ 
          queryKey: QueryKeys.customization(response.data.customized_resume.id) 
        });
      }
    },
  });
};

export const useResumeComparison = (resumeId: number | string | undefined) => {
  const query = useQuery({
    queryKey: ['resumeComparison', resumeId],
    queryFn: async () => {
      if (!resumeId) throw new Error('Resume ID is required');
      const id = typeof resumeId === 'string' ? parseInt(resumeId) : resumeId;
      return customizationService.getComparison(id);
    },
    enabled: !!resumeId,
  });
  
  return extractQueryState(query);
};