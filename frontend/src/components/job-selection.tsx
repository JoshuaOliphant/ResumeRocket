"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { AlertCircle, RefreshCw, Plus, ChevronRight } from "lucide-react";
import { useJobs } from "@/hooks/use-resume-api";
import { JobDescription } from "@/lib/api-types";
import { formatDate } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

interface JobSelectionProps {
  onJobSelected: (jobId: number) => void;
  selectedJobId?: number;
}

export function JobSelection({ onJobSelected, selectedJobId }: JobSelectionProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialJobId = searchParams.get("jobId") || selectedJobId?.toString();
  const [localSelectedJobId, setLocalSelectedJobId] = useState<string | undefined>(
    initialJobId ? initialJobId.toString() : undefined
  );
  
  const {
    data: jobs,
    isLoading,
    isError,
    error,
    refetch,
  } = useJobs();
  
  useEffect(() => {
    // If we have a selectedJobId prop, update the local state
    if (selectedJobId && selectedJobId.toString() !== localSelectedJobId) {
      setLocalSelectedJobId(selectedJobId.toString());
    }
    // If we have an initial job ID from query params and jobs are loaded, select it
    else if (initialJobId && jobs?.length > 0 && !localSelectedJobId) {
      setLocalSelectedJobId(initialJobId);
      onJobSelected(parseInt(initialJobId));
    }
  }, [initialJobId, jobs, localSelectedJobId, onJobSelected, selectedJobId]);
  
  const handleJobChange = (value: string) => {
    setLocalSelectedJobId(value);
    onJobSelected(parseInt(value));
  };
  
  const handleAddNewJob = () => {
    router.push("/job-input");
  };
  
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>
            <Skeleton className="h-6 w-40" />
          </CardTitle>
          <CardDescription>
            <Skeleton className="h-4 w-60" />
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>
    );
  }
  
  if (isError) {
    return (
      <Card className="border-red-300 bg-red-50 dark:bg-red-950/10">
        <CardHeader>
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <CardTitle>Error Loading Jobs</CardTitle>
          </div>
          <CardDescription>
            {error?.message || "Failed to load your saved jobs."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => refetch()} variant="outline" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }
  
  if (!jobs || jobs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Job Descriptions Found</CardTitle>
          <CardDescription>
            You need to add a job description before you can customize your resume.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center">
          <Button onClick={handleAddNewJob} className="gap-2">
            <Plus className="h-4 w-4" />
            Add New Job Description
          </Button>
        </CardContent>
      </Card>
    );
  }
  
  // Extract the selected job data for preview
  const selectedJob = localSelectedJobId
    ? jobs.find((job: JobDescription) => job.id.toString() === localSelectedJobId)
    : undefined;
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Select Job Description</CardTitle>
        <CardDescription>
          Choose a job description to customize your resume for.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Select value={localSelectedJobId} onValueChange={handleJobChange}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a job description" />
          </SelectTrigger>
          <SelectContent>
            {jobs.map((job: JobDescription) => (
              <SelectItem key={job.id} value={job.id.toString()}>
                {job.title} {job.company ? `at ${job.company}` : ""}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        {selectedJob && (
          <div className="mt-4 p-4 border rounded-md bg-muted/50">
            <h3 className="font-semibold text-sm mb-1">{selectedJob.title}</h3>
            {selectedJob.company && (
              <p className="text-sm text-muted-foreground mb-2">
                {selectedJob.company}
              </p>
            )}
            <p className="text-xs text-muted-foreground mb-2">
              Added on {formatDate(selectedJob.created_at)}
            </p>
            <p className="text-sm line-clamp-3">
              {selectedJob.content.substring(0, 150)}
              {selectedJob.content.length > 150 ? "..." : ""}
            </p>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={handleAddNewJob} className="gap-1">
          <Plus className="h-4 w-4" />
          Add New Job
        </Button>
        
        {selectedJob && (
          <Button 
            variant="link" 
            className="text-primary gap-1"
            onClick={() => router.push(`/job-management`)}
          >
            Manage Jobs
            <ChevronRight className="h-4 w-4" />
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}