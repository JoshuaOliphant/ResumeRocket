"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import { useSubmitJobUrl, useSubmitJobText } from "@/hooks/use-resume-api";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function JobInputPage() {
  const [activeTab, setActiveTab] = useState<string>("url");
  const [jobUrl, setJobUrl] = useState<string>("");
  const [jobText, setJobText] = useState<string>("");
  const [jobTitle, setJobTitle] = useState<string>("");
  const [company, setCompany] = useState<string>("");
  const [urlError, setUrlError] = useState<string>("");
  const [textError, setTextError] = useState<string>("");
  
  const { toast } = useToast();
  const router = useRouter();
  
  const submitJobUrlMutation = useSubmitJobUrl();
  const submitJobTextMutation = useSubmitJobText();
  
  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUrlError("");
    
    if (!jobUrl.trim()) {
      setUrlError("Please enter a job URL");
      return;
    }
    
    // Basic URL validation
    try {
      new URL(jobUrl);
    } catch (err) {
      setUrlError("Please enter a valid URL");
      return;
    }
    
    try {
      await submitJobUrlMutation.mutateAsync({ url: jobUrl });
      toast({
        title: "Success",
        description: "Job description extracted and saved successfully",
      });
      router.push("/job-management");
    } catch (error: any) {
      setUrlError(error.message || "Failed to process job URL");
    }
  };
  
  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTextError("");
    
    if (!jobText.trim()) {
      setTextError("Please enter a job description");
      return;
    }
    
    if (!jobTitle.trim()) {
      setTextError("Please enter a job title");
      return;
    }
    
    try {
      await submitJobTextMutation.mutateAsync({
        text: jobText,
        title: jobTitle,
        company: company.trim(),
      });
      toast({
        title: "Success",
        description: "Job description saved successfully",
      });
      router.push("/job-management");
    } catch (error: any) {
      setTextError(error.message || "Failed to save job description");
    }
  };
  
  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">Add Job Description</h1>
      
      <Tabs defaultValue="url" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="url">Job URL</TabsTrigger>
          <TabsTrigger value="text">Job Text</TabsTrigger>
        </TabsList>
        
        <TabsContent value="url">
          <Card>
            <CardHeader>
              <CardTitle>Add Job from URL</CardTitle>
              <CardDescription>
                Enter the URL of a job posting to automatically extract the job description.
              </CardDescription>
            </CardHeader>
            <form onSubmit={handleUrlSubmit}>
              <CardContent>
                <div className="grid w-full items-center gap-4">
                  <div className="flex flex-col space-y-1.5">
                    <Input
                      id="job-url"
                      placeholder="https://example.com/job-posting"
                      value={jobUrl}
                      onChange={(e) => setJobUrl(e.target.value)}
                    />
                    {urlError && <p className="text-sm text-red-500">{urlError}</p>}
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={() => router.back()}>
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={submitJobUrlMutation.isPending}
                >
                  {submitJobUrlMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing
                    </>
                  ) : (
                    "Extract Job Description"
                  )}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>
        
        <TabsContent value="text">
          <Card>
            <CardHeader>
              <CardTitle>Add Job Description Text</CardTitle>
              <CardDescription>
                Enter the job description details manually.
              </CardDescription>
            </CardHeader>
            <form onSubmit={handleTextSubmit}>
              <CardContent>
                <div className="grid w-full items-center gap-4">
                  <div className="flex flex-col space-y-1.5">
                    <label htmlFor="job-title" className="text-sm font-medium">
                      Job Title
                    </label>
                    <Input
                      id="job-title"
                      placeholder="Software Engineer"
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                      required
                    />
                  </div>
                  
                  <div className="flex flex-col space-y-1.5">
                    <label htmlFor="company" className="text-sm font-medium">
                      Company (Optional)
                    </label>
                    <Input
                      id="company"
                      placeholder="Acme Corp"
                      value={company}
                      onChange={(e) => setCompany(e.target.value)}
                    />
                  </div>
                  
                  <div className="flex flex-col space-y-1.5">
                    <label htmlFor="job-description" className="text-sm font-medium">
                      Job Description
                    </label>
                    <Textarea
                      id="job-description"
                      placeholder="Paste the full job description here..."
                      value={jobText}
                      onChange={(e) => setJobText(e.target.value)}
                      required
                      className="min-h-[300px]"
                    />
                    {textError && <p className="text-sm text-red-500">{textError}</p>}
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={() => router.back()}>
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={submitJobTextMutation.isPending}
                >
                  {submitJobTextMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving
                    </>
                  ) : (
                    "Save Job Description"
                  )}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}