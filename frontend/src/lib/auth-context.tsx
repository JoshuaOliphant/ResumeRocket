import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from './api-services';
import { User, LoginRequest, RegisterRequest } from './api-types';
import { getAuthToken, setAuthToken, removeAuthToken } from './utils';

// Define AuthContext type
interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<boolean>;
  register: (userData: RegisterRequest) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Create token refresh interval (30 minutes)
const TOKEN_REFRESH_INTERVAL = 30 * 60 * 1000;

// Auth Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  
  // Check for existing token and load user on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = getAuthToken();
        if (token) {
          await loadUserData();
        } else {
          setLoading(false);
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);
  
  // Set up token refresh interval
  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    
    if (user) {
      intervalId = setInterval(() => {
        refreshToken().catch(console.error);
      }, TOKEN_REFRESH_INTERVAL);
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [user]);
  
  // Load user data from the API
  const loadUserData = async (): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authService.getCurrentUser();
      
      if (response.error) {
        setError(response.error);
        removeAuthToken();
        setUser(null);
        setLoading(false);
        return false;
      }
      
      if (response.data?.user) {
        setUser(response.data.user);
        setLoading(false);
        return true;
      }
      
      setLoading(false);
      return false;
    } catch (err) {
      setError('Failed to load user data');
      setLoading(false);
      return false;
    }
  };
  
  // Login function
  const login = async (credentials: LoginRequest): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authService.login(credentials);
      
      if (response.error) {
        setError(response.error);
        setLoading(false);
        return false;
      }
      
      const { token, user } = response.data!;
      setAuthToken(token);
      setUser(user);
      setLoading(false);
      return true;
    } catch (err) {
      setError('Login failed');
      setLoading(false);
      return false;
    }
  };
  
  // Register function
  const register = async (userData: RegisterRequest): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authService.register(userData);
      
      if (response.error) {
        setError(response.error);
        setLoading(false);
        return false;
      }
      
      const { token, user } = response.data!;
      setAuthToken(token);
      setUser(user);
      setLoading(false);
      return true;
    } catch (err) {
      setError('Registration failed');
      setLoading(false);
      return false;
    }
  };
  
  // Logout function
  const logout = async (): Promise<void> => {
    setLoading(true);
    
    try {
      await authService.logout();
    } catch (err) {
      console.error('Logout API error:', err);
    } finally {
      // Always remove token and user state even if API call fails
      removeAuthToken();
      setUser(null);
      setLoading(false);
      router.push('/login');
    }
  };
  
  // Refresh token function
  const refreshToken = async (): Promise<boolean> => {
    try {
      const token = getAuthToken();
      if (!token) return false;
      
      const response = await authService.refreshToken();
      
      if (response.error || !response.data?.token) {
        removeAuthToken();
        setUser(null);
        return false;
      }
      
      setAuthToken(data.data.token);
      setUser(data.data.user);
      return true;
    } catch (err) {
      console.error('Token refresh error:', err);
      return false;
    }
  };
  
  // Computed property
  const isAuthenticated = !!user;
  
  const value = {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};