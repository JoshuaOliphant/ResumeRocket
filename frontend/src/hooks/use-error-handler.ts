import { useState, useCallback } from 'react';
import { useToast } from './use-toast';

export interface ErrorState {
  message: string | null;
  code?: number;
  details?: string;
}

export const useErrorHandler = () => {
  const [error, setError] = useState<ErrorState | null>(null);
  const { toast } = useToast();

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleError = useCallback((err: unknown, customMessage?: string) => {
    let errorMessage = customMessage || 'An unexpected error occurred';
    let errorCode: number | undefined;
    let errorDetails: string | undefined;

    // Handle different error types
    if (typeof err === 'string') {
      errorMessage = err;
    } else if (err instanceof Error) {
      errorMessage = err.message;
      // If it's an axios error with a response
      if ('response' in err) {
        const axiosError = err as any;
        errorCode = axiosError.response?.status;
        errorDetails = axiosError.response?.data?.message || axiosError.response?.data?.error;
        // Use the API's error message if available
        if (errorDetails) {
          errorMessage = errorDetails;
        }
      }
    } else if (err && typeof err === 'object' && 'message' in err) {
      errorMessage = (err as any).message;
    }

    // Show toast notification for errors
    toast({
      title: 'Error',
      description: errorMessage,
      variant: 'destructive',
    });

    // Set the error state
    setError({
      message: errorMessage,
      code: errorCode,
      details: errorDetails,
    });

    // Also log to console in development
    if (process.env.NODE_ENV !== 'production') {
      console.error('Error occurred:', err);
    }

    return errorMessage;
  }, [toast]);

  return {
    error,
    handleError,
    clearError,
  };
};