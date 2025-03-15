'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import ProtectedRoute from '@/components/auth/protected-route';
import { dashboardService } from '@/lib/api-services';
import { DashboardData } from '@/lib/api-types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await dashboardService.getDashboardData();
        
        if (response.error) {
          setError(response.error);
        } else if (response.data) {
          setDashboardData(response.data);
        }
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Welcome, {user?.username || 'User'}</h1>
          <Button onClick={() => logout()}>Logout</Button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
          </div>
        ) : error ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-red-500">
                <p>{error}</p>
                <Button onClick={() => window.location.reload()} className="mt-4">
                  Retry
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : dashboardData ? (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Dashboard content would go here */}
            <div className="md:col-span-12">
              <Card>
                <CardHeader>
                  <CardTitle>Your Dashboard</CardTitle>
                  <CardDescription>
                    Here's a summary of your resume optimization activity
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p>Total Resumes: {dashboardData.stats.total_resumes}</p>
                  <p>Total Jobs: {dashboardData.stats.total_jobs}</p>
                  <p>Total Customizations: {dashboardData.stats.total_customizations}</p>
                  <p>Average Improvement: {dashboardData.stats.average_improvement}%</p>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Welcome to ResumeRocket</CardTitle>
              <CardDescription>
                Start by uploading your resume and a job description to get personalized optimization.
              </CardDescription>
            </CardHeader>
          </Card>
        )}
      </div>
    </ProtectedRoute>
  );
}