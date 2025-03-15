"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { 
  PlusIcon, 
  MoreVerticalIcon, 
  SearchIcon, 
  ChevronRightIcon, 
  TrashIcon,
  PencilIcon,
  FileTextIcon,
  ExternalLinkIcon
} from "lucide-react";

// Sample data
const sampleJobs = [
  {
    id: 1,
    title: "Senior Frontend Developer",
    company: "Tech Solutions Inc.",
    date: "2023-11-15T00:00:00Z",
    source: "LinkedIn",
  },
  {
    id: 2,
    title: "Full Stack Engineer",
    company: "Innovate Corp",
    date: "2023-11-10T00:00:00Z",
    source: "Indeed",
  },
  {
    id: 3,
    title: "React Developer",
    company: "Web Systems LLC",
    date: "2023-11-05T00:00:00Z",
    source: "Manual Entry",
  },
];

export default function JobManagementPage() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);

  // Filter jobs based on search query
  const filteredJobs = sampleJobs.filter((job) => {
    const query = searchQuery.toLowerCase();
    return (
      job.title.toLowerCase().includes(query) ||
      job.company.toLowerCase().includes(query)
    );
  });

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).format(date);
  };

  // Handle job deletion
  const handleDeleteJob = () => {
    // In a real app, you would make an API call to delete the job
    console.log(`Deleting job with ID: ${selectedJobId}`);
    setDeleteDialogOpen(false);
    setSelectedJobId(null);
  };

  // Open delete dialog
  const openDeleteDialog = (jobId: number) => {
    setSelectedJobId(jobId);
    setDeleteDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Job Listings</h1>
          <p className="text-muted-foreground">
            Manage your saved job listings and optimize your resume for each one.
          </p>
        </div>
        <Link href="/job-input">
          <Button>
            <PlusIcon className="mr-2 h-4 w-4" />
            Add Job
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader className="px-6 pt-6 pb-4">
          <div className="flex items-center justify-between">
            <CardTitle>All Jobs</CardTitle>
            <div className="relative w-full max-w-sm">
              <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search jobs..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </CardHeader>
        <CardContent className="px-6">
          {filteredJobs.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Company</TableHead>
                  <TableHead>Date Added</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead className="w-[80px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredJobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell className="font-medium">{job.title}</TableCell>
                    <TableCell>{job.company}</TableCell>
                    <TableCell>{formatDate(job.date)}</TableCell>
                    <TableCell>{job.source}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreVerticalIcon className="h-4 w-4" />
                            <span className="sr-only">Open menu</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem>
                            <Link
                              href={`/resume-customization?jobId=${job.id}`}
                              className="flex items-center w-full"
                            >
                              <FileTextIcon className="mr-2 h-4 w-4" />
                              <span>Use for Resume</span>
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <PencilIcon className="mr-2 h-4 w-4" />
                            <span>Edit Job</span>
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <ExternalLinkIcon className="mr-2 h-4 w-4" />
                            <span>View Details</span>
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-red-500 focus:text-red-500"
                            onClick={() => openDeleteDialog(job.id)}
                          >
                            <TrashIcon className="mr-2 h-4 w-4" />
                            <span>Delete</span>
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-muted p-3 mb-4">
                <FileTextIcon className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium">No jobs found</h3>
              <p className="text-sm text-muted-foreground mt-1 mb-4">
                {searchQuery
                  ? "No jobs match your search criteria."
                  : "You haven't added any jobs yet."}
              </p>
              {!searchQuery && (
                <Link href="/job-input">
                  <Button>
                    <PlusIcon className="mr-2 h-4 w-4" />
                    Add Your First Job
                  </Button>
                </Link>
              )}
            </div>
          )}
        </CardContent>
        {filteredJobs.length > 0 && (
          <CardFooter className="flex items-center justify-between px-6 py-4 border-t">
            <div className="text-sm text-muted-foreground">
              Showing {filteredJobs.length} of {sampleJobs.length} jobs
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled>
                Previous
              </Button>
              <Button variant="outline" size="sm" disabled>
                Next
              </Button>
            </div>
          </CardFooter>
        )}
      </Card>

      {/* Delete confirmation dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Job</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this job? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteJob}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}