"use client"

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Loader2, Upload, File, FileText } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { resumeService } from '@/lib/api-services'

export default function ResumeUploadPage() {
  const [fileUploadError, setFileUploadError] = useState<string | null>(null)
  const [textInputError, setTextInputError] = useState<string | null>(null)
  const [resumeText, setResumeText] = useState<string>("")
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  // File upload mutation
  const uploadResumeMutation = useMutation({
    mutationFn: (file: File) => resumeService.uploadResume(file),
    onSuccess: (response) => {
      if (response.data?.resume) {
        // Navigate to resume management page after successful upload
        router.push('/resume-management')
      } else {
        setFileUploadError('Failed to process resume. Please try again.')
      }
    },
    onError: (error: any) => {
      setFileUploadError(error?.message || 'Failed to upload resume. Please try again.')
    }
  })

  // Text input mutation
  const submitResumeTextMutation = useMutation({
    mutationFn: (text: string) => {
      // Create a file from the text
      const file = new File([text], "resume.txt", { type: "text/plain" })
      return resumeService.uploadResume(file)
    },
    onSuccess: (response) => {
      if (response.data?.resume) {
        // Navigate to resume management page after successful submit
        router.push('/resume-management')
      } else {
        setTextInputError('Failed to process resume text. Please try again.')
      }
    },
    onError: (error: any) => {
      setTextInputError(error?.message || 'Failed to submit resume text. Please try again.')
    }
  })

  // Handle file selection
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadedFileName(file.name)
      setFileUploadError(null)
    }
  }

  // Handle file upload
  const handleFileUpload = () => {
    const file = fileInputRef.current?.files?.[0]
    if (!file) {
      setFileUploadError('Please select a file to upload')
      return
    }

    // Check file type (PDF, DOCX, TXT)
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
    if (!validTypes.includes(file.type)) {
      setFileUploadError('Please upload a PDF, DOCX, or TXT file')
      return
    }

    // Upload file
    uploadResumeMutation.mutate(file)
  }

  // Handle text submission
  const handleTextSubmit = () => {
    if (!resumeText.trim()) {
      setTextInputError('Please enter your resume text')
      return
    }

    submitResumeTextMutation.mutate(resumeText)
  }

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">Upload Your Resume</h1>
      <p className="text-gray-500 mb-8">
        Upload your resume to get started. We'll analyze it and provide suggestions to improve its effectiveness.
      </p>

      <Tabs defaultValue="file" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-8">
          <TabsTrigger value="file">File Upload</TabsTrigger>
          <TabsTrigger value="text">Text Input</TabsTrigger>
        </TabsList>

        <TabsContent value="file">
          <Card>
            <CardHeader>
              <CardTitle>Upload Resume File</CardTitle>
              <CardDescription>
                Upload your resume as a PDF, DOCX, or TXT file. Max size: 5MB.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-6">
                <div className="grid w-full items-center gap-1.5">
                  <Label htmlFor="resume-file">Resume File</Label>
                  <div className="flex items-center gap-4">
                    <Input
                      id="resume-file"
                      type="file"
                      ref={fileInputRef}
                      accept=".pdf,.docx,.txt"
                      onChange={handleFileChange}
                    />
                  </div>
                  {uploadedFileName && (
                    <p className="text-sm text-gray-500 mt-2 flex items-center">
                      <File className="h-4 w-4 mr-1" /> {uploadedFileName}
                    </p>
                  )}
                </div>

                {fileUploadError && (
                  <Alert variant="destructive">
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>{fileUploadError}</AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button variant="outline" onClick={() => router.push('/dashboard')}>
                Cancel
              </Button>
              <Button 
                onClick={handleFileUpload}
                disabled={uploadResumeMutation.isPending}
              >
                {uploadResumeMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Resume
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="text">
          <Card>
            <CardHeader>
              <CardTitle>Enter Resume Text</CardTitle>
              <CardDescription>
                Copy and paste your resume text directly.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-6">
                <div className="grid w-full gap-1.5">
                  <Label htmlFor="resume-text">Resume Content</Label>
                  <Textarea
                    id="resume-text"
                    placeholder="Paste your resume text here..."
                    className="min-h-[300px]"
                    value={resumeText}
                    onChange={(e) => {
                      setResumeText(e.target.value)
                      setTextInputError(null)
                    }}
                  />
                </div>

                {textInputError && (
                  <Alert variant="destructive">
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>{textInputError}</AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button variant="outline" onClick={() => router.push('/dashboard')}>
                Cancel
              </Button>
              <Button 
                onClick={handleTextSubmit}
                disabled={submitResumeTextMutation.isPending}
              >
                {submitResumeTextMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Submit Resume
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}