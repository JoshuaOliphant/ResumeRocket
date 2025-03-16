import { useRouter } from 'next/navigation';

interface FetchOptions extends RequestInit {
  requiresAuth?: boolean;
}

export async function fetchWithAuth(url: string, options: FetchOptions = {}) {
  const { requiresAuth = true, ...fetchOptions } = options;
  
  // Get the token from localStorage
  const token = localStorage.getItem('token');
  
  // If auth is required and no token exists, throw error
  if (requiresAuth && !token) {
    throw new Error('Authentication required');
  }
  
  // Prepare headers
  const headers = new Headers(fetchOptions.headers);
  if (requiresAuth && token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  // Make the request
  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });
  
  // Handle 401 Unauthorized responses
  if (response.status === 401) {
    // Clear the invalid token
    localStorage.removeItem('token');
    // Throw error to be handled by caller
    throw new Error('Authentication expired');
  }
  
  return response;
}

export async function uploadFormDataWithAuth(url: string, formData: FormData) {
  return fetchWithAuth(url, {
    method: 'POST',
    body: formData,
  });
}

export async function postJsonWithAuth(url: string, data: any) {
  return fetchWithAuth(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
}

export async function getWithAuth(url: string) {
  return fetchWithAuth(url, {
    method: 'GET',
  });
} 