"use client"

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { FileTextIcon, ArrowRightIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { RecentOptimization } from "@/lib/api-types";

interface OptimizationCardProps {
  jobTitle: string;
  company: string;
  matchScore: number;
  date: string;
  logoUrl?: string;
}

function OptimizationCard({
  jobTitle,
  company,
  matchScore,
  date,
  logoUrl,
}: OptimizationCardProps) {
  const scoreColor =
    matchScore >= 80
      ? "text-green-600 dark:text-green-400"
      : matchScore >= 60
        ? "text-yellow-600 dark:text-yellow-400"
        : "text-red-600 dark:text-red-400";

  return (
    <Card
      className="overflow-hidden transition-all duration-200 hover:shadow-md"
    >
      <CardContent className="p-0">
        <div className="flex items-start p-4">
          <div
            className="h-12 w-12 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center overflow-hidden mr-4"
          >
            {logoUrl ? (
              <img
                src={logoUrl}
                alt={company}
                className="h-full w-full object-cover"
              />
            ) : (
              <FileTextIcon className="h-6 w-6 text-gray-400" />
            )}
          </div>
          <div className="flex-1">
            <h3
              className="font-medium text-gray-900 dark:text-white"
            >
              {jobTitle}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {company}
            </p>
            <div className="mt-2 flex items-center">
              <span className={`text-sm font-medium ${scoreColor}`}>
                {matchScore}% Match
              </span>
              <span
                className="mx-2 text-gray-300 dark:text-gray-600"
              >
                •
              </span>
              <span
                className="text-xs text-gray-500 dark:text-gray-400"
              >
                {date}
              </span>
            </div>
          </div>
          <div className="ml-4">
            <Badge
              variant={matchScore >= 80 ? "default" : "secondary"}
            >
              {matchScore >= 80
                ? "Excellent"
                : matchScore >= 60
                  ? "Good"
                  : "Needs Work"}
            </Badge>
          </div>
        </div>
        <div className="px-4 pb-4">
          <Progress value={matchScore} className="h-1.5" />
        </div>
      </CardContent>
    </Card>
  );
}

// Loading skeleton component for optimization cards
function OptimizationCardSkeleton() {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start">
          <Skeleton className="h-12 w-12 rounded-full mr-4" />
          <div className="flex-1">
            <Skeleton className="h-5 w-36 mb-2" />
            <Skeleton className="h-4 w-24 mb-3" />
            <div className="flex items-center">
              <Skeleton className="h-4 w-20 mr-2" />
              <Skeleton className="h-3 w-16" />
            </div>
          </div>
          <Skeleton className="h-6 w-20 ml-4" />
        </div>
        <Skeleton className="h-1.5 w-full mt-4" />
      </CardContent>
    </Card>
  );
}

// Empty state when there are no optimizations
function EmptyOptimizations() {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      <FileTextIcon className="h-12 w-12 text-gray-300 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">
        No optimizations yet
      </h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 max-w-xs">
        Customize your resume for a job to see your optimization results here.
      </p>
      <Button>Create your first optimization</Button>
    </div>
  );
}

interface RecentOptimizationsWithDataProps {
  isLoading?: boolean;
  optimizations?: RecentOptimization[];
  error?: string | null;
}

export function RecentOptimizationsWithData({ 
  isLoading = false, 
  optimizations = [], 
  error = null 
}: RecentOptimizationsWithDataProps) {
  return (
    <Card className="h-full">
      <CardHeader
        className="flex flex-row items-center justify-between pb-2"
      >
        <div>
          <CardTitle>Recent Optimizations</CardTitle>
          <CardDescription>
            Your latest resume customizations
          </CardDescription>
        </div>
        <Button variant="ghost" size="sm" className="gap-1">
          View all <ArrowRightIcon className="h-4 w-4" />
        </Button>
      </CardHeader>
      
      <CardContent>
        {isLoading ? (
          // Loading state
          <div className="space-y-4">
            <OptimizationCardSkeleton />
            <OptimizationCardSkeleton />
            <OptimizationCardSkeleton />
          </div>
        ) : error ? (
          // Error state
          <div className="text-center py-6 text-red-500">
            <p>Failed to load optimizations</p>
            <p className="text-sm text-gray-500 mt-2">{error}</p>
          </div>
        ) : optimizations.length === 0 ? (
          // Empty state
          <EmptyOptimizations />
        ) : (
          // Data loaded successfully
          <div className="space-y-4">
            {optimizations.map((optimization) => (
              <OptimizationCard
                key={optimization.id}
                jobTitle={optimization.job_title || "Untitled Position"}
                company={optimization.company || "Unknown Company"}
                matchScore={optimization.match_score}
                date={optimization.date}
                logoUrl={optimization.logo_url}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}