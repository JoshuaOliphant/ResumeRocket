"use client"

import { useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Loader2, FileDown, Share2, ArrowLeft, CheckCircle, XCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from '@/components/ui/skeleton'
import { customizationService } from '@/lib/api-services'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export default function ResumeComparisonPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const resumeId = searchParams.get('id')
  const [activeTab, setActiveTab] = useState('comparison')
  
  // Fetch comparison data
  const comparisonQuery = useQuery({
    queryKey: ['resumeComparison', resumeId],
    queryFn: async () => {
      if (!resumeId) throw new Error('Resume ID is required')
      const response = await customizationService.getComparison(parseInt(resumeId))
      return response.data
    },
    enabled: !!resumeId
  })

  // Extract data from query
  const resume = comparisonQuery.data?.customized_resume
  const job = comparisonQuery.data?.job_description
  const comparison = comparisonQuery.data?.comparison
  const improvementData = {
    originalScore: comparisonQuery.data?.original_ats_score || 0,
    customizedScore: comparisonQuery.data?.customized_ats_score || 0,
    improvement: comparisonQuery.data?.improvement || 0
  }

  // Parse comparison data if available
  const parsedComparison = comparison ? (
    typeof comparison === 'string' ? JSON.parse(comparison) : comparison
  ) : null

  // Format resume content for display
  const formatContent = (content: string) => {
    // Simple formatting to preserve paragraph breaks
    return content.split('\n').map((line, i) => (
      <p key={i} className={line.trim() === '' ? 'my-4' : 'my-2'}>
        {line || '\u00A0'}
      </p>
    ))
  }

  // Handle export options
  const handleExport = (format: string) => {
    alert(`Exporting as ${format} - Implementation required`)
    // Actual implementation would call an API endpoint to generate the file
  }

  if (!resumeId) {
    return (
      <div className="container mx-auto py-10">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>No resume ID provided. Please return to the customization page.</AlertDescription>
        </Alert>
        <Button className="mt-4" onClick={() => router.push('/resume-customization')}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Return to Customization
        </Button>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Resume Optimization Results</h1>
        <Button variant="outline" onClick={() => router.push('/dashboard')}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
        </Button>
      </div>

      {comparisonQuery.isPending ? (
        <div className="space-y-6">
          <Skeleton className="h-[200px] w-full rounded-lg" />
          <Skeleton className="h-[400px] w-full rounded-lg" />
        </div>
      ) : comparisonQuery.isError ? (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {comparisonQuery.error instanceof Error 
              ? comparisonQuery.error.message 
              : 'Failed to load resume comparison data'}
          </AlertDescription>
        </Alert>
      ) : (
        <>
          {/* Improvement Summary Card */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Optimization Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <h3 className="text-sm font-medium">Original ATS Score</h3>
                  <div className="flex items-center gap-2">
                    <Progress value={improvementData.originalScore} className="h-2" />
                    <span className="text-lg font-bold">{improvementData.originalScore}%</span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h3 className="text-sm font-medium">Optimized ATS Score</h3>
                  <div className="flex items-center gap-2">
                    <Progress value={improvementData.customizedScore} className="h-2" />
                    <span className="text-lg font-bold">{improvementData.customizedScore}%</span>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h3 className="text-sm font-medium">Improvement</h3>
                  <div className="flex items-center">
                    <Badge variant={improvementData.improvement > 0 ? "success" : "default"}>
                      {improvementData.improvement > 0 ? '+' : ''}{improvementData.improvement}%
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Job details */}
              {job && (
                <div className="mt-6">
                  <h3 className="text-sm font-medium mb-2">Optimized For:</h3>
                  <div className="bg-muted p-3 rounded-md">
                    <p className="font-medium">{job.title || 'Untitled Position'}</p>
                    {job.company && <p className="text-sm text-muted-foreground">{job.company}</p>}
                  </div>
                </div>
              )}

              {/* Export options */}
              <div className="mt-6 flex justify-end">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button>
                      <FileDown className="mr-2 h-4 w-4" />
                      Export Resume
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => handleExport('pdf')}>
                      Export as PDF
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleExport('docx')}>
                      Export as Word (DOCX)
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleExport('txt')}>
                      Export as Text
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardContent>
          </Card>

          {/* Main Content Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList>
              <TabsTrigger value="comparison">Side-by-Side Comparison</TabsTrigger>
              <TabsTrigger value="optimized">Optimized Resume</TabsTrigger>
              <TabsTrigger value="changes">Change Details</TabsTrigger>
            </TabsList>

            {/* Comparison View Tab */}
            <TabsContent value="comparison" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Original Resume</CardTitle>
                  </CardHeader>
                  <CardContent className="prose max-w-none">
                    <div className="bg-muted/50 p-4 rounded-md text-sm">
                      {resume?.original_content ? (
                        formatContent(resume.original_content)
                      ) : (
                        <p className="text-muted-foreground">Original content not available</p>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Optimized Resume</CardTitle>
                  </CardHeader>
                  <CardContent className="prose max-w-none">
                    <div className="bg-muted/50 p-4 rounded-md text-sm">
                      {resume?.customized_content ? (
                        formatContent(resume.customized_content)
                      ) : (
                        <p className="text-muted-foreground">Customized content not available</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Optimized Resume Tab */}
            <TabsContent value="optimized">
              <Card>
                <CardHeader>
                  <CardTitle>Optimized Resume</CardTitle>
                </CardHeader>
                <CardContent className="prose max-w-none">
                  <div className="bg-muted/50 p-4 rounded-md">
                    {resume?.customized_content ? (
                      formatContent(resume.customized_content)
                    ) : (
                      <p className="text-muted-foreground">Customized content not available</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Changes Detail Tab */}
            <TabsContent value="changes">
              <Card>
                <CardHeader>
                  <CardTitle>Detailed Changes</CardTitle>
                </CardHeader>
                <CardContent>
                  {parsedComparison ? (
                    <div className="space-y-6">
                      {/* Keyword Matches */}
                      <div>
                        <h3 className="text-lg font-semibold mb-3">Keyword Matches</h3>
                        <div className="bg-muted/50 p-4 rounded-md">
                          {parsedComparison.matching_keywords?.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                              {parsedComparison.matching_keywords.map((keyword: string, index: number) => (
                                <Badge key={index} variant="outline" className="bg-green-50 text-green-700 border-green-200">
                                  {keyword}
                                </Badge>
                              ))}
                            </div>
                          ) : (
                            <p className="text-muted-foreground">No matching keywords found</p>
                          )}
                        </div>
                      </div>

                      {/* Missing Keywords */}
                      <div>
                        <h3 className="text-lg font-semibold mb-3">Missing Keywords</h3>
                        <div className="bg-muted/50 p-4 rounded-md">
                          {parsedComparison.missing_keywords?.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                              {parsedComparison.missing_keywords.map((keyword: string, index: number) => (
                                <Badge key={index} variant="outline" className="bg-red-50 text-red-700 border-red-200">
                                  {keyword}
                                </Badge>
                              ))}
                            </div>
                          ) : (
                            <p className="text-green-600 flex items-center">
                              <CheckCircle className="h-4 w-4 mr-2" />
                              No missing keywords - great job!
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Section Changes */}
                      <div>
                        <h3 className="text-lg font-semibold mb-3">Section Improvements</h3>
                        <div className="space-y-4">
                          {parsedComparison.section_changes ? (
                            Object.entries(parsedComparison.section_changes).map(([section, changes]: [string, any], index: number) => (
                              <div key={index} className="bg-muted/50 p-4 rounded-md">
                                <h4 className="font-medium mb-2">{section}</h4>
                                <p className="text-sm">{changes.description || 'Section was optimized'}</p>
                                {changes.before && changes.after && (
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3 text-xs">
                                    <div>
                                      <p className="text-muted-foreground mb-1">Before:</p>
                                      <div className="bg-background p-2 rounded">{changes.before}</div>
                                    </div>
                                    <div>
                                      <p className="text-muted-foreground mb-1">After:</p>
                                      <div className="bg-background p-2 rounded">{changes.after}</div>
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))
                          ) : (
                            <p className="text-muted-foreground">No detailed section changes available</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <Alert>
                      <AlertTitle>No detailed comparison data available</AlertTitle>
                      <AlertDescription>
                        We couldn't find detailed information about the changes made to your resume.
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  )
}