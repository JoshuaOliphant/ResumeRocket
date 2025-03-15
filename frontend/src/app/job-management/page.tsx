"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, FileText, Plus, Trash2, RefreshCw } from "lucide-react";
import { useJobs, useDeleteJob } from "@/hooks/use-resume-api";
import { JobDescription } from "@/lib/api-types";
import { formatDate } from "@/lib/utils";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Skeleton } from "@/components/ui/skeleton";

export default function JobManagementPage() {
  const router = useRouter();
  const [jobToDelete, setJobToDelete] = useState<number | null>(null);
  
  const {
    data: jobs,
    isLoading: jobsLoading,
    isError: jobsError,
    error: jobsErrorData,
    refetch,
  } = useJobs();
  
  const deleteJobMutation = useDeleteJob();
  
  const handleDeleteJob = async (jobId: number) => {
    try {
      await deleteJobMutation.mutateAsync(jobId);
      setJobToDelete(null);
    } catch (error) {
      console.error("Failed to delete job", error);
    }
  };
  
  const renderJobContent = (content: string) => {
    // Truncate job content for display
    const maxLength = 100;
    return content.length > maxLength
      ? `${content.substring(0, maxLength)}...`
      : content;
  };
  
  const handleAddJob = () => {
    router.push("/job-input");
  };
  
  const handleUseForCustomization = (jobId: number) => {
    router.push(`/resume-customization?jobId=${jobId}`);
  };
  
  if (jobsLoading) {
    return (
      <div className="container mx-auto py-10">
        <h1 className="text-3xl font-bold mb-6">My Saved Jobs</h1>
        <div className="flex justify-between items-center mb-6">
          <Skeleton className="h-10 w-40" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-7 w-40 mb-2" />
            <Skeleton className="h-5 w-60" />
          </CardHeader>
          <CardContent>
            {Array(3).fill(0).map((_, i) => (
              <div key={i} className="mb-6">
                <Skeleton className="h-12 w-full mb-4" />
                <Skeleton className="h-48 w-full" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    );
  }
  
  if (jobsError) {
    return (
      <div className="container mx-auto py-10">
        <h1 className="text-3xl font-bold mb-6">My Saved Jobs</h1>
        <Card className="border-red-300 bg-red-50 dark:bg-red-950/10">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <CardTitle>Error Loading Jobs</CardTitle>
            </div>
            <CardDescription>
              {jobsErrorData?.message || "Failed to load your saved jobs."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => refetch()} 
              variant="outline"
              className="gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">My Saved Jobs</h1>
        <Button onClick={handleAddJob} className="gap-2">
          <Plus className="h-4 w-4" />
          Add New Job
        </Button>
      </div>
      
      {(!jobs || jobs.length === 0) ? (
        <Card>
          <CardHeader>
            <CardTitle>No Jobs Found</CardTitle>
            <CardDescription>
              You haven't saved any job descriptions yet. Add a job to get started.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center py-10">
            <Button onClick={handleAddJob} variant="outline" className="gap-2">
              <FileText className="h-5 w-5" />
              Add Your First Job Description
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Your Saved Job Descriptions</CardTitle>
            <CardDescription>
              Manage your saved job descriptions and use them to customize your resume.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Job Title</TableHead>
                  <TableHead>Company</TableHead>
                  <TableHead>Description Preview</TableHead>
                  <TableHead>Date Added</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {jobs.map((job: JobDescription) => (
                  <TableRow key={job.id}>
                    <TableCell className="font-medium">{job.title}</TableCell>
                    <TableCell>
                      {job.company ? (
                        job.company
                      ) : (
                        <span className="text-muted-foreground italic">Not specified</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="max-w-md">
                        {renderJobContent(job.content)}
                      </div>
                      {job.source_url && (
                        <Badge variant="outline" className="mt-2">
                          From URL
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{formatDate(job.created_at)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleUseForCustomization(job.id)}
                        >
                          Use
                        </Button>
                        <AlertDialog
                          open={jobToDelete === job.id}
                          onOpenChange={(open) => {
                            if (!open) setJobToDelete(null);
                          }}
                        >
                          <AlertDialogTrigger asChild>
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-red-500"
                              onClick={() => setJobToDelete(job.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Delete Job Description</AlertDialogTitle>
                              <AlertDialogDescription>
                                Are you sure you want to delete this job description? This action cannot be undone.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction
                                className="bg-red-500 hover:bg-red-600"
                                onClick={() => handleDeleteJob(job.id)}
                              >
                                {deleteJobMutation.isPending ? (
                                  <>
                                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                                    Deleting...
                                  </>
                                ) : (
                                  "Delete"
                                )}
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}