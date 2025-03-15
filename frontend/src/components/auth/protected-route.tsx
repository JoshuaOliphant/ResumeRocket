import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  adminOnly = false 
}) => {
  const { isAuthenticated, user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Wait for auth check to complete
    if (!loading) {
      // Redirect if not authenticated
      if (!isAuthenticated) {
        router.push('/login');
        return;
      }
      
      // Redirect if admin route but user is not admin
      if (adminOnly && user && !user.is_admin) {
        router.push('/dashboard');
        return;
      }
    }
  }, [isAuthenticated, loading, router, adminOnly, user]);

  // Show nothing while checking authentication
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  // If not authenticated or admin check fails, don't render children
  if (!isAuthenticated || (adminOnly && user && !user.is_admin)) {
    return null;
  }

  // Otherwise, render children
  return <>{children}</>;
};

export default ProtectedRoute;