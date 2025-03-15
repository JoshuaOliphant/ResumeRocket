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
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BriefcaseIcon,
  BookmarkIcon,
  StarIcon,
  MapPinIcon,
  CalendarIcon,
  AlertCircle,
} from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { SavedJob } from "@/lib/api-types";

interface JobCardProps {
  title: string;
  company: string;
  location?: string;
  salary?: string;
  posted: string;
  matchScore?: number;
  logoUrl?: string;
  isFavorite?: boolean;
  status?: string;
}

function JobCard({
  title,
  company,
  location = "Remote",
  salary = "Not specified",
  posted,
  matchScore = 0,
  logoUrl,
  isFavorite = false,
  status,
}: JobCardProps) {
  return (
    <Card
      className="group overflow-hidden transition-all duration-200 hover:shadow-md"
    >
      <CardContent className="p-0">
        <div className="flex items-start p-4">
          <div
            className="h-12 w-12 rounded-md bg-gray-100 dark:bg-gray-700 flex items-center justify-center overflow-hidden mr-4"
          >
            {logoUrl ? (
              <img
                src={logoUrl}
                alt={company}
                className="h-full w-full object-cover"
              />
            ) : (
              <BriefcaseIcon className="h-6 w-6 text-gray-400" />
            )}
          </div>
          <div className="flex-1">
            <div className="flex items-start justify-between">
              <div>
                <h3
                  className="font-medium text-gray-900 dark:text-white"
                >
                  {title}
                </h3>
                <p
                  className="text-sm text-gray-500 dark:text-gray-400"
                >
                  {company}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {isFavorite ? (
                  <StarIcon
                    className="h-4 w-4 fill-yellow-400 text-yellow-400"
                  />
                ) : (
                  <BookmarkIcon className="h-4 w-4" />
                )}
              </Button>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              <div
                className="flex items-center text-xs text-gray-500 dark:text-gray-400"
              >
                <MapPinIcon className="mr-1 h-3 w-3" />
                {location}
              </div>
              <div
                className="flex items-center text-xs text-gray-500 dark:text-gray-400"
              >
                <CalendarIcon className="mr-1 h-3 w-3" />
                {posted}
              </div>
              {status && (
                <Badge variant="outline" className="ml-auto">
                  {status}
                </Badge>
              )}
              {!status && salary && (
                <Badge variant="outline" className="ml-auto">
                  {salary}
                </Badge>
              )}
            </div>
          </div>
        </div>
        <div
          className="border-t border-gray-100 dark:border-gray-800 px-4 py-3 bg-gray-50 dark:bg-gray-800/50 flex justify-between items-center"
        >
          {matchScore > 0 ? (
            <Badge
              variant={matchScore >= 80 ? "default" : "secondary"}
            >
              {matchScore}% Match
            </Badge>
          ) : (
            <span className="text-sm text-gray-500">Not analyzed</span>
          )}
          <Button size="sm">
            Optimize Resume
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Loading skeleton for job card
function JobCardSkeleton() {
  return (
    <Card>
      <CardContent className="p-0">
        <div className="flex items-start p-4">
          <Skeleton className="h-12 w-12 rounded-md mr-4" />
          <div className="flex-1">
            <div className="flex items-start justify-between">
              <div>
                <Skeleton className="h-5 w-36 mb-2" />
                <Skeleton className="h-4 w-24" />
              </div>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              <Skeleton className="h-4 w-24 mr-2" />
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-5 w-16 ml-auto" />
            </div>
          </div>
        </div>
        <div className="border-t border-gray-100 dark:border-gray-800 px-4 py-3 bg-gray-50 dark:bg-gray-800/50 flex justify-between items-center">
          <Skeleton className="h-5 w-20" />
          <Skeleton className="h-8 w-32" />
        </div>
      </CardContent>
    </Card>
  );
}

// Empty state component
function EmptySavedJobs() {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      <BriefcaseIcon className="h-12 w-12 text-gray-300 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">
        No saved jobs
      </h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 max-w-xs">
        Save job descriptions to see them here.
      </p>
      <Button>Find jobs</Button>
    </div>
  );
}

interface SavedJobsWithDataProps {
  isLoading?: boolean;
  savedJobs?: SavedJob[];
  error?: string | null;
}

export function SavedJobsWithData({
  isLoading = false,
  savedJobs = [],
  error = null,
}: SavedJobsWithDataProps) {
  // Process jobs into different categories
  const allJobs = savedJobs.map(job => ({
    id: job.id,
    title: job.title || "Untitled Position",
    company: job.company || "Unknown Company",
    posted: job.date,
    status: job.status,
    isFavorite: false // API doesn't provide this information yet
  }));

  // For favorites and applied, we'll use a subset or filter based on status
  // when the API supports these fields
  const favoriteJobs = allJobs.slice(0, Math.min(2, allJobs.length));
  const appliedJobs = allJobs.filter(job => job.status === "Applied");

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32 mb-2" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent className="p-0">
          <div className="px-4 pt-2">
            <Skeleton className="h-10 w-full mb-4" />
          </div>
          <div className="px-4 py-2 space-y-4">
            <JobCardSkeleton />
            <JobCardSkeleton />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Saved Jobs</CardTitle>
          <CardDescription>Jobs you've saved for later</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error || "Failed to load saved jobs"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Saved Jobs</CardTitle>
        <CardDescription>
          Jobs you've saved for later
        </CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs defaultValue="all" className="px-4 pt-2">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="all">
              All
            </TabsTrigger>
            <TabsTrigger value="favorites">
              Favorites
            </TabsTrigger>
            <TabsTrigger value="applied">
              Applied
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="pt-4 pb-2 px-2">
            {allJobs.length === 0 ? (
              <EmptySavedJobs />
            ) : (
              <div className="space-y-4">
                {allJobs.map((job, index) => (
                  <JobCard 
                    key={job.id || index}
                    title={job.title}
                    company={job.company}
                    posted={job.posted}
                    status={job.status}
                    isFavorite={job.isFavorite}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="favorites" className="pt-4 pb-2 px-2">
            {favoriteJobs.length === 0 ? (
              <EmptySavedJobs />
            ) : (
              <div className="space-y-4">
                {favoriteJobs.map((job, index) => (
                  <JobCard 
                    key={job.id || index}
                    title={job.title}
                    company={job.company}
                    posted={job.posted}
                    status={job.status}
                    isFavorite={true}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="applied" className="pt-4 pb-2 px-2">
            {appliedJobs.length === 0 ? (
              <EmptySavedJobs />
            ) : (
              <div className="space-y-4">
                {appliedJobs.map((job, index) => (
                  <JobCard 
                    key={job.id || index}
                    title={job.title}
                    company={job.company}
                    posted={job.posted}
                    status={job.status}
                    isFavorite={job.isFavorite}
                  />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}