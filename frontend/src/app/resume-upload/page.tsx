"use client";

import React, { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { FileUploadArea } from "../components/file-upload-area";
import { PreviousDocuments } from "../components/previous-documents";
import { CompatibleFormats } from "../components/compatible-formats";
import { Header } from "../components/header";
import { Footer } from "../components/footer";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { uploadFormDataWithAuth } from '@/lib/api';

export default function ResumeUploadPage() {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState<string>("");
  const [jobFile, setJobFile] = useState<File | null>(null);
  const [jobText, setJobText] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const router = useRouter();

  const handleResumeUpload = (file: File | null) => {
    setResumeFile(file);
    setResumeText("");
    setError("");
  };

  const handleResumeTextInput = (text: string) => {
    setResumeText(text);
    setResumeFile(null);
    setError("");
  };

  const handleJobUpload = (file: File | null) => {
    setJobFile(file);
    setJobText("");
    setError("");
  };

  const handleJobTextInput = (text: string) => {
    setJobText(text);
    setJobFile(null);
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const formData = new FormData();
      
      // Handle resume input
      if (resumeFile) {
        formData.append('resume_file', resumeFile);
      } else if (resumeText.trim()) {
        formData.append('resume', resumeText);
      } else {
        throw new Error('Please provide a resume file or text');
      }

      // Handle job description input
      if (jobFile) {
        formData.append('job_file', jobFile);
      } else if (jobText.trim()) {
        formData.append('job_description', jobText);
      } else {
        throw new Error('Please provide a job description file or text');
      }

      // Upload resume and job description
      const analyzeResponse = await uploadFormDataWithAuth('/api/analyze_resume', formData);
      
      if (!analyzeResponse.ok) {
        const errorData = await analyzeResponse.json();
        throw new Error(errorData.error || 'Error processing resume');
      }

      const { resume_id, job_id } = await analyzeResponse.json();

      // Customize resume with streaming
      const customizeResponse = await uploadFormDataWithAuth('/api/customize_resume_streaming', formData);
      
      if (!customizeResponse.ok) {
        const errorData = await customizeResponse.json();
        throw new Error(errorData.error || 'Error customizing resume');
      }

      // Redirect to results page
      router.push(`/results/${resume_id}/${job_id}`);
    } catch (error) {
      if (error instanceof Error) {
        if (error.message === 'Authentication required' || error.message === 'Authentication expired') {
          router.push('/login');
          return;
        }
        setError(error.message);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormComplete = () => {
    return (resumeFile || resumeText.trim().length > 0) && (jobFile || jobText.trim().length > 0);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold mb-2">Customize Your Resume</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Upload your resume and job description to get personalized recommendations
            </p>
          </div>

          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
                <h2 className="text-xl font-semibold mb-4">Upload Your Resume</h2>
                <Tabs defaultValue="upload">
                  <TabsList className="mb-4">
                    <TabsTrigger value="upload">Upload File</TabsTrigger>
                    <TabsTrigger value="paste">Paste Text</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="upload">
                    <FileUploadArea
                      onFileUpload={handleResumeUpload}
                      acceptedFileTypes=".pdf,.doc,.docx"
                      fileType="resume"
                      currentFile={resumeFile}
                    />
                  </TabsContent>
                  
                  <TabsContent value="paste">
                    <FileUploadArea
                      onFileUpload={handleResumeUpload}
                      onTextInput={handleResumeTextInput}
                      acceptedFileTypes=".pdf,.doc,.docx"
                      fileType="resume"
                      allowTextInput={true}
                      currentFile={resumeFile}
                      textValue={resumeText}
                    />
                  </TabsContent>
                </Tabs>
                <CompatibleFormats fileType="resume" />
              </div>
              
              <div className="bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
                <h3 className="text-lg font-semibold mb-4">Previous Resumes</h3>
                <PreviousDocuments 
                  documentType="resume" 
                  onSelect={handleResumeUpload} 
                />
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
                <h2 className="text-xl font-semibold mb-4">Job Description</h2>
                <Tabs defaultValue="paste">
                  <TabsList className="mb-4">
                    <TabsTrigger value="paste">Paste Text</TabsTrigger>
                    <TabsTrigger value="upload">Upload File</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="paste">
                    <FileUploadArea
                      onFileUpload={handleJobUpload}
                      onTextInput={handleJobTextInput}
                      acceptedFileTypes=".pdf,.doc,.docx,.txt"
                      fileType="job"
                      allowTextInput={true}
                      currentFile={jobFile}
                      textValue={jobText}
                    />
                  </TabsContent>
                  
                  <TabsContent value="upload">
                    <FileUploadArea
                      onFileUpload={handleJobUpload}
                      acceptedFileTypes=".pdf,.doc,.docx,.txt"
                      fileType="job"
                      currentFile={jobFile}
                    />
                  </TabsContent>
                </Tabs>
                <CompatibleFormats fileType="job" />
              </div>
              
              <div className="bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
                <h3 className="text-lg font-semibold mb-4">Previous Job Descriptions</h3>
                <PreviousDocuments 
                  documentType="job" 
                  onSelect={handleJobUpload} 
                />
              </div>
            </div>
          </div>
          
          <div className="mt-8 text-center">
            <Button 
              size="lg" 
              onClick={handleSubmit} 
              disabled={!isFormComplete() || isSubmitting}
              className="min-w-[200px]"
            >
              {isSubmitting ? "Processing..." : "Optimize Resume"}
            </Button>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}