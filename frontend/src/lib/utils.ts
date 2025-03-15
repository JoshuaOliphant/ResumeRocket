import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// API base URL - can be configured based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Authentication token handling
export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
};

export const setAuthToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
  }
};

export const removeAuthToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
  }
};

// API client
export const apiClient = {
  // Generic fetch function with authentication
  async fetch<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const token = getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers,
    };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });
      
      const contentType = response.headers.get('content-type');
      let data;
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }
      
      if (!response.ok) {
        return {
          error: data.message || 'An unknown error occurred',
          status: response.status,
        };
      }
      
      return {
        data: data as T,
        status: response.status,
      };
    } catch (error) {
      return {
        error: (error as Error).message || 'Network error',
        status: 0,
      };
    }
  },
  
  // GET request
  get<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.fetch<T>(endpoint, { ...options, method: 'GET' });
  },
  
  // POST request
  post<T>(endpoint: string, data: any, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.fetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  // PUT request
  put<T>(endpoint: string, data: any, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.fetch<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
  
  // DELETE request
  delete<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.fetch<T>(endpoint, { ...options, method: 'DELETE' });
  },
  
  // File upload
  async uploadFile<T>(
    endpoint: string, 
    file: File, 
    additionalData: Record<string, any> = {}, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const token = getAuthToken();
    const formData = new FormData();
    
    formData.append('file', file);
    
    // Add any additional data to the form
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, value);
    });
    
    const headers = {
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers,
    };
    
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        method: 'POST',
        headers,
        body: formData,
      });
      
      const contentType = response.headers.get('content-type');
      let data;
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }
      
      if (!response.ok) {
        return {
          error: data.message || 'An unknown error occurred',
          status: response.status,
        };
      }
      
      return {
        data: data as T,
        status: response.status,
      };
    } catch (error) {
      return {
        error: (error as Error).message || 'Network error',
        status: 0,
      };
    }
  }
};
