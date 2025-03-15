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
import { Loader2, AlertCircle } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useResumes, useCustomizeResume } from "@/hooks/use-resume-api";
import { JobSelection } from "@/components/job-selection";

export default function ResumeCustomizationPage() {
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [selectedJobId, setSelectedJobId] = useState<number | undefined>(undefined);
  const [customizationLevel, setCustomizationLevel] = useState<string>("balanced");
  const [industry, setIndustry] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  
  // Get resumeId and jobId from URL if available
  useEffect(() => {
    const resumeId = searchParams.get("resumeId");
    const jobId = searchParams.get("jobId");
    
    if (resumeId) setSelectedResumeId(resumeId);
    if (jobId) setSelectedJobId(parseInt(jobId));
  }, [searchParams]);
  
  // API hooks
  const {
    data: resumes,
    isLoading: resumesLoading,
    isError: resumesError,
    error: resumesErrorData,
  } = useResumes();
  
  const customizeResumeMutation = useCustomizeResume();
  
  const handleJobSelected = (jobId: number) => {
    setSelectedJobId(jobId);
  };
  
  const handleCustomize = async () => {
    if (!selectedResumeId || !selectedJobId || !customizationLevel) {
      toast({
        title: "Missing Information",
        description: "Please select a resume, job, and customization level.",
        variant: "destructive",
      });
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const result = await customizeResumeMutation.mutateAsync({
        resumeId: parseInt(selectedResumeId),
        jobId: selectedJobId,
        customizationLevel,
        industry: industry || undefined,
      });
      
      if (result.data?.customized_resume?.id) {
        router.push(`/resume-comparison/${result.data.customized_resume.id}`);
      } else {
        throw new Error("No customized resume was returned");
      }
    } catch (error: any) {
      toast({
        title: "Customization Failed",
        description: error.message || "Failed to customize your resume. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (resumesLoading) {
    return (
      <div className="container mx-auto py-10">
        <h1 className="text-3xl font-bold mb-6">Resume Customization</h1>
        <div className="flex items-center justify-center p-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading...</span>
        </div>
      </div>
    );
  }
  
  if (resumesError) {
    return (
      <div className="container mx-auto py-10">
        <h1 className="text-3xl font-bold mb-6">Resume Customization</h1>
        <Card className="border-red-300 bg-red-50 dark:bg-red-950/10">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <CardTitle>Error Loading Data</CardTitle>
            </div>
            <CardDescription>
              {resumesErrorData?.message || "Failed to load resumes. Please try again."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => router.refresh()} 
              variant="outline"
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  const noResumes = !resumes || resumes.length === 0;
  
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">Resume Customization</h1>
      
      <div className="grid gap-6 md:grid-cols-2">
        {/* Resume Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Select Resume</CardTitle>
            <CardDescription>
              Choose a resume to customize for your target job.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {noResumes ? (
              <div className="text-center py-4">
                <p className="text-muted-foreground mb-4">No resumes found</p>
                <Button
                  onClick={() => router.push("/resume-upload")}
                  variant="outline"
                >
                  Upload Resume
                </Button>
              </div>
            ) : (
              <Select
                value={selectedResumeId}
                onValueChange={setSelectedResumeId}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a resume" />
                </SelectTrigger>
                <SelectContent>
                  {resumes.map((resume) => (
                    <SelectItem key={resume.id} value={resume.id.toString()}>
                      {resume.title || `Resume ${resume.id}`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </CardContent>
        </Card>
        
        {/* Job Selection Component */}
        <JobSelection 
          onJobSelected={handleJobSelected} 
          selectedJobId={selectedJobId}
        />
      </div>
      
      {/* Customization Options */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Customization Options</CardTitle>
          <CardDescription>
            Configure how you want your resume to be customized.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Customization Level</label>
              <Select
                value={customizationLevel}
                onValueChange={setCustomizationLevel}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="conservative">
                    Conservative (Minimal Changes)
                  </SelectItem>
                  <SelectItem value="balanced">
                    Balanced (Recommended)
                  </SelectItem>
                  <SelectItem value="aggressive">
                    Aggressive (Major Rewrite)
                  </SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                Controls how much your resume will be modified
              </p>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Industry (Optional)</label>
              <Select
                value={industry}
                onValueChange={setIndustry}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select industry (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technology">Technology</SelectItem>
                  <SelectItem value="healthcare">Healthcare</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="education">Education</SelectItem>
                  <SelectItem value="marketing">Marketing</SelectItem>
                  <SelectItem value="manufacturing">Manufacturing</SelectItem>
                  <SelectItem value="retail">Retail</SelectItem>
                  <SelectItem value="legal">Legal</SelectItem>
                  <SelectItem value="government">Government</SelectItem>
                  <SelectItem value="nonprofit">Non-Profit</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                Provides additional context for customization
              </p>
            </div>
          </div>
        </CardContent>
        <CardFooter className="justify-between">
          <Button variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
          <Button
            onClick={handleCustomize}
            disabled={noResumes || !selectedResumeId || !selectedJobId || isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Customizing...
              </>
            ) : (
              "Customize Resume"
            )}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}