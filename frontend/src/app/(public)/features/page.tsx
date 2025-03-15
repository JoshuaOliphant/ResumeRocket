"use client";

import React from "react";
import Link from "next/link";
import { 
  FileTextIcon, 
  BarChartIcon, 
  CheckCircleIcon, 
  ZapIcon, 
  ArrowRightIcon,
  TargetIcon,
  RefreshCwIcon,
  SparklesIcon,
  SearchIcon,
  ListFilterIcon,
  CopyIcon,
  FileDownIcon,
  ClockIcon,
  UserPlusIcon
} from "lucide-react";
import { Button } from "@/components/ui/button";

// Feature sections
const features = [
  {
    title: "AI Resume Optimization",
    description: "Our AI analyzes your resume and customizes it to match specific job descriptions, increasing your chances of getting past ATS screening.",
    icon: ZapIcon,
    points: [
      "Automatic keyword optimization for ATS",
      "Tailored content based on job requirements",
      "Skill highlighting based on relevance",
      "Improved formatting and structure"
    ]
  },
  {
    title: "ATS Simulation & Analysis",
    description: "See exactly how your resume will be processed by Applicant Tracking Systems (ATS) with detailed scoring and insights.",
    icon: BarChartIcon,
    points: [
      "ATS score prediction with detailed breakdown",
      "Keyword match analysis",
      "Missing skills identification",
      "Formatting issue detection"
    ]
  },
  {
    title: "Resume Comparison",
    description: "See a side-by-side comparison of your original resume and the optimized version, with highlights of what changed and why.",
    icon: RefreshCwIcon,
    points: [
      "Visual diff highlighting changes",
      "Explanation for each modification",
      "Before/after metrics",
      "Version history tracking"
    ]
  },
  {
    title: "Job Management",
    description: "Save and organize job descriptions to streamline your application process and track your progress.",
    icon: ListFilterIcon,
    points: [
      "Job description extraction from URLs",
      "Manual job description entry",
      "Job categorization and tagging",
      "Search and filter functionality"
    ]
  },
  {
    title: "Resume Management",
    description: "Upload, store, and manage multiple versions of your resume for different job types and industries.",
    icon: FileTextIcon,
    points: [
      "Multiple resume storage",
      "Resume version control",
      "Industry-specific optimization",
      "Template library"
    ]
  },
  {
    title: "Export Options",
    description: "Export your optimized resume in multiple formats, ready to submit to job applications.",
    icon: FileDownIcon,
    points: [
      "PDF export with formatting preserved",
      "DOCX export for further editing",
      "Plain text for copy-paste",
      "ATS-friendly formatting"
    ]
  }
];

export default function FeaturesPage() {
  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      {/* Hero section */}
      <div className="text-center mb-16 md:mb-24">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
          Powerful Features to Land Your Dream Job
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
          ResumeRocket combines AI technology with proven job search strategies to optimize your resume for each application.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register" passHref legacyBehavior>
            <Button size="lg" className="px-8">
              Get Started Free
              <ArrowRightIcon className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="/login" passHref legacyBehavior>
            <Button size="lg" variant="outline" className="px-8">
              Log In
            </Button>
          </Link>
        </div>
      </div>

      {/* Features grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
        {features.map((feature, index) => (
          <div key={index} className="bg-card rounded-xl border shadow-sm p-6 flex flex-col">
            <div className="mb-4">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-4">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground mb-4">{feature.description}</p>
            </div>
            <div className="mt-auto">
              <ul className="space-y-2">
                {feature.points.map((point, i) => (
                  <li key={i} className="flex items-start">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                    <span className="text-sm">{point}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>

      {/* How it works section */}
      <div className="bg-muted rounded-xl p-8 md:p-12 mb-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight mb-4">How It Works</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Our simple three-step process makes it easy to optimize your resume for each job application.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center text-center">
            <div className="relative">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground text-2xl font-bold mb-4">
                1
              </div>
              <div className="hidden md:block absolute h-1 bg-border w-[calc(100%+2rem)] top-8 left-full -z-10"></div>
            </div>
            <h3 className="text-xl font-bold mb-2">Upload Your Resume</h3>
            <p className="text-muted-foreground">
              Upload your existing resume in PDF, DOCX, or enter it directly as text.
            </p>
          </div>
          <div className="flex flex-col items-center text-center">
            <div className="relative">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground text-2xl font-bold mb-4">
                2
              </div>
              <div className="hidden md:block absolute h-1 bg-border w-[calc(100%+2rem)] top-8 left-full -z-10"></div>
            </div>
            <h3 className="text-xl font-bold mb-2">Add Job Description</h3>
            <p className="text-muted-foreground">
              Paste the job URL or description and our AI will analyze the requirements.
            </p>
          </div>
          <div className="flex flex-col items-center text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground text-2xl font-bold mb-4">
              3
            </div>
            <h3 className="text-xl font-bold mb-2">Get Optimized Resume</h3>
            <p className="text-muted-foreground">
              Receive your tailored resume with improvements highlighted and ATS score analysis.
            </p>
          </div>
        </div>
      </div>

      {/* FAQ section */}
      <div className="mb-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold tracking-tight mb-4">Frequently Asked Questions</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need to know about ResumeRocket.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <div className="border rounded-lg p-6">
            <h3 className="text-lg font-bold mb-2">How does the AI optimization work?</h3>
            <p className="text-muted-foreground">
              Our AI analyzes both your resume and the job description to identify key skills, requirements, and qualifications. It then enhances your resume by highlighting relevant experiences and achievements, adjusting keywords, and improving formatting for better ATS compatibility.
            </p>
          </div>
          <div className="border rounded-lg p-6">
            <h3 className="text-lg font-bold mb-2">Will the AI write false information?</h3>
            <p className="text-muted-foreground">
              No. Our AI only works with the information you provide in your original resume. It restructures and enhances your existing content but does not fabricate experiences or skills you don't have.
            </p>
          </div>
          <div className="border rounded-lg p-6">
            <h3 className="text-lg font-bold mb-2">Is my data secure and private?</h3>
            <p className="text-muted-foreground">
              Yes. We take security seriously. Your resume data and job descriptions are encrypted and never shared with third parties. We only use your information to provide and improve our service.
            </p>
          </div>
          <div className="border rounded-lg p-6">
            <h3 className="text-lg font-bold mb-2">What file formats are supported?</h3>
            <p className="text-muted-foreground">
              We support PDF, DOCX, and plain text formats for resume uploads. You can also enter your resume content directly into our platform.
            </p>
          </div>
        </div>
      </div>

      {/* CTA section */}
      <div className="bg-primary text-primary-foreground rounded-xl p-8 md:p-12 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to Land Your Dream Job?</h2>
        <p className="text-xl text-primary-foreground/80 max-w-2xl mx-auto mb-8">
          Join thousands of job seekers who are optimizing their applications with ResumeRocket. Get started for free today.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register" passHref legacyBehavior>
            <Button size="lg" variant="secondary" className="px-8">
              Sign Up Free
            </Button>
          </Link>
          <Link href="/login" passHref legacyBehavior>
            <Button size="lg" variant="outline" className="px-8 bg-transparent text-primary-foreground hover:bg-primary-foreground/10 border-primary-foreground/20">
              Log In
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}