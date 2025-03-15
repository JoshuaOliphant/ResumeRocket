"use client"

import React from "react";
import { RecentOptimizationsWithData } from "../(components)/data-fetching/recent-optimizations-with-data";
import { StatisticsSectionWithData } from "../(components)/data-fetching/statistics-section-with-data";
import { SavedJobsWithData } from "../(components)/data-fetching/saved-jobs-with-data";
import { OptimizationHistoryWithData } from "../(components)/data-fetching/optimization-history-with-data";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { useDashboardData } from "@/hooks/use-api";
import { useErrorHandler } from "@/hooks/use-error-handler";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

export default function DashboardWithData() {
  const { dashboardData, isLoading, isError, error } = useDashboardData();
  const { handleError } = useErrorHandler();
  
  // Format current date/time for "last updated"
  const formattedDate = new Date().toLocaleString('en-US', { 
    hour: 'numeric', 
    minute: 'numeric', 
    hour12: true 
  });
  
  // If there's an error, handle it
  React.useEffect(() => {
    if (isError && error) {
      handleError(error, "Failed to load dashboard data");
    }
  }, [isError, error, handleError]);

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1
            className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white"
          >
            Dashboard
          </h1>
          <div className="flex items-center space-x-2">
            {isLoading ? (
              <Button variant="outline" size="sm" disabled>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Loading...
              </Button>
            ) : (
              <div className="flex items-center gap-4">
                <span
                  className="text-sm text-gray-500 dark:text-gray-400"
                >
                  Last updated: Today, {formattedDate}
                </span>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => window.location.reload()}
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh
                </Button>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <RecentOptimizationsWithData 
            isLoading={isLoading}
            optimizations={dashboardData?.recent_optimizations}
            error={isError ? error?.error : null}
          />
          <StatisticsSectionWithData 
            isLoading={isLoading}
            stats={dashboardData?.stats}
            error={isError ? error?.error : null}
          />
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="md:col-span-2">
            <SavedJobsWithData 
              isLoading={isLoading}
              savedJobs={dashboardData?.saved_jobs}
              error={isError ? error?.error : null}
            />
          </div>
          <div className="md:col-span-1">
            <OptimizationHistoryWithData 
              isLoading={isLoading}
              historyData={dashboardData?.optimization_history}
              error={isError ? error?.error : null}
            />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}