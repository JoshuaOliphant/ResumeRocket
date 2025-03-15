import { QueryClient } from '@tanstack/react-query';

// Error handler to customize error messages
const queryErrorHandler = (error: unknown): void => {
  // Log to monitoring service or analytics
  console.error('React Query Error:', error);
};

// Configure the query client with defaults
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1, // Only retry failed queries once
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false, // Don't refetch when window gains focus
      onError: queryErrorHandler, // Custom error handler
    },
    mutations: {
      retry: 0, // Don't retry failed mutations
      onError: queryErrorHandler, // Custom error handler
    },
  },
});

// Custom hook for handling loading and error states
export const extractQueryState = <T>(result: {
  data?: T;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
}) => {
  return {
    data: result.data,
    isLoading: result.isLoading,
    isError: result.isError,
    error: result.error,
  };
};