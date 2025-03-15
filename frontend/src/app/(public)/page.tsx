"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { 
  FileTextIcon, 
  ArrowRightIcon, 
  BarChartIcon, 
  CheckCircleIcon,
  ZapIcon,
  TargetIcon,
  LineChartIcon,
  UserIcon,
  BuildingIcon,
  MoveUpIcon
} from "lucide-react";

// Testimonial data
const testimonials = [
  {
    content: "ResumeRocket helped me land interviews at 3 top tech companies after months of rejections.",
    author: "Michael K.",
    role: "Software Engineer"
  },
  {
    content: "The AI recommendations were surprisingly insightful. My resume is now much more targeted and effective.",
    author: "Sarah J.",
    role: "Marketing Manager"
  },
  {
    content: "I was skeptical at first, but the ATS optimization feature alone is worth it. My application success rate doubled!",
    author: "David W.",
    role: "Product Manager"
  }
];

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent z-0"></div>
        <div className="container px-4 md:px-6 relative z-10">
          <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
            <div className="flex flex-col justify-center space-y-4">
              <div className="space-y-2">
                <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary text-primary-foreground hover:bg-primary/80 mb-4">
                  <ZapIcon className="mr-1 h-3 w-3" /> AI-Powered Resume Optimization
                </div>
                <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
                  Land Your Dream Job With AI
                </h1>
                <p className="max-w-[600px] text-muted-foreground md:text-xl">
                  Tailored resumes that get past ATS systems and impress hiring managers, powered by AI that understands what recruiters want.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/register" passHref legacyBehavior>
                  <Button size="lg" className="px-8">
                    Get Started Free
                    <ArrowRightIcon className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/features" passHref legacyBehavior>
                  <Button size="lg" variant="outline" className="px-8">
                    See Features
                  </Button>
                </Link>
              </div>
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="h-8 w-8 rounded-full border-2 border-background bg-muted overflow-hidden">
                      <UserIcon className="h-full w-full p-1 text-muted-foreground" />
                    </div>
                  ))}
                </div>
                <div className="text-muted-foreground">
                  Trusted by <span className="font-medium text-foreground">2,000+</span> job seekers
                </div>
              </div>
            </div>
            <div className="flex justify-center lg:justify-end">
              <div className="relative w-full max-w-md lg:max-w-full h-[400px] lg:h-[500px] bg-gradient-to-tl from-primary/10 via-background to-background border rounded-lg overflow-hidden shadow-xl">
                <div className="absolute top-6 left-6 right-6 bottom-12 bg-card border rounded-md shadow-sm p-6">
                  <div className="space-y-2 mb-4">
                    <div className="h-4 w-1/3 bg-muted rounded"></div>
                    <div className="h-8 w-2/3 bg-primary/80 rounded text-primary-foreground flex items-center justify-center text-sm font-medium">
                      Software Engineer
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-center gap-x-3">
                      <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                        <CheckCircleIcon className="h-4 w-4 text-primary" />
                      </div>
                      <div className="space-y-1 flex-1">
                        <div className="h-2 w-full bg-muted rounded"></div>
                        <div className="h-2 w-3/4 bg-muted rounded"></div>
                      </div>
                    </div>
                    <div className="flex items-center gap-x-3">
                      <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                        <CheckCircleIcon className="h-4 w-4 text-primary" />
                      </div>
                      <div className="space-y-1 flex-1">
                        <div className="h-2 w-full bg-muted rounded"></div>
                        <div className="h-2 w-2/3 bg-muted rounded"></div>
                      </div>
                    </div>
                    <div className="flex items-center gap-x-3">
                      <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                        <MoveUpIcon className="h-4 w-4 text-primary" />
                      </div>
                      <div className="space-y-1 flex-1">
                        <div className="h-2 w-full bg-muted rounded"></div>
                        <div className="h-2 w-4/5 bg-muted rounded"></div>
                      </div>
                    </div>
                  </div>
                  <div className="absolute bottom-6 right-6 flex items-center space-x-2">
                    <div className="h-6 w-6 bg-muted rounded-full"></div>
                    <div className="h-6 w-24 bg-muted rounded-md"></div>
                  </div>
                </div>
                <div className="absolute -bottom-2 right-8 h-12 w-28 bg-accent rounded-t-lg flex items-center justify-center font-semibold text-sm">
                  97% Match
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/50">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2 max-w-3xl">
              <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80 mb-2">
                POWERED BY AI
              </div>
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                Optimize Your Resume for Each Job
              </h2>
              <p className="text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed max-w-[800px] mx-auto">
                ResumeRocket's AI analyzes job descriptions and optimizes your resume to highlight the most relevant skills and experience.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
              <div className="relative group flex flex-col items-center p-6 bg-background rounded-xl border shadow-sm transition-all hover:shadow-md">
                <div className="p-3 bg-primary/10 rounded-full mb-4">
                  <FileTextIcon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold mb-2">AI Resume Tailoring</h3>
                <p className="text-muted-foreground text-center">
                  Our AI creates customized resumes for each job application, emphasizing your most relevant skills and experience.
                </p>
              </div>
              <div className="relative group flex flex-col items-center p-6 bg-background rounded-xl border shadow-sm transition-all hover:shadow-md">
                <div className="p-3 bg-primary/10 rounded-full mb-4">
                  <BarChartIcon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold mb-2">ATS Optimization</h3>
                <p className="text-muted-foreground text-center">
                  Beat applicant tracking systems with keyword optimization and formatting that ensures your resume gets seen by recruiters.
                </p>
              </div>
              <div className="relative group flex flex-col items-center p-6 bg-background rounded-xl border shadow-sm transition-all hover:shadow-md">
                <div className="p-3 bg-primary/10 rounded-full mb-4">
                  <TargetIcon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold mb-2">Job Match Analysis</h3>
                <p className="text-muted-foreground text-center">
                  See exactly how well your resume matches each job description with detailed scoring and recommendations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center mb-8">
            <div className="space-y-2 max-w-3xl">
              <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80 mb-2">
                SIMPLE PROCESS
              </div>
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                Three Steps to Job Success
              </h2>
              <p className="text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed max-w-[800px] mx-auto">
                Our streamlined process makes it easy to optimize your resume for each job application.
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mx-auto max-w-5xl">
            <div className="flex flex-col items-center space-y-4 relative">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground text-2xl font-bold">
                1
              </div>
              <div className="hidden md:block absolute h-1 bg-border w-full top-8 left-1/2 -z-10"></div>
              <h3 className="text-xl font-bold">Upload Your Resume</h3>
              <p className="text-muted-foreground text-center">
                Upload your existing resume in PDF, DOCX, or enter it directly as text.
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4 relative">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground text-2xl font-bold">
                2
              </div>
              <div className="hidden md:block absolute h-1 bg-border w-full top-8 left-1/2 -z-10"></div>
              <h3 className="text-xl font-bold">Add Job Description</h3>
              <p className="text-muted-foreground text-center">
                Paste the job URL or description and our AI will analyze the requirements.
              </p>
            </div>
            <div className="flex flex-col items-center space-y-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-bold">Get Optimized Resume</h3>
              <p className="text-muted-foreground text-center">
                Receive your tailored resume with improvements highlighted and ATS score analysis.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-muted/30">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2 max-w-3xl">
              <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80 mb-2">
                TESTIMONIALS
              </div>
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                Our Users Land Jobs Faster
              </h2>
              <p className="text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed max-w-[800px] mx-auto">
                See how ResumeRocket has helped job seekers like you succeed.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
              {testimonials.map((testimonial, i) => (
                <div key={i} className="flex flex-col p-6 bg-background rounded-xl border shadow-sm">
                  <div className="flex mb-4">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg key={star} className="h-5 w-5 fill-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27z" />
                      </svg>
                    ))}
                  </div>
                  <p className="flex-1 text-lg italic mb-4">"{testimonial.content}"</p>
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center">
                      <UserIcon className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{testimonial.author}</p>
                      <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="container px-4 md:px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
            <div className="flex flex-col space-y-4">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                Ready to Land Your Dream Job?
              </h2>
              <p className="text-primary-foreground/90 md:text-xl max-w-[600px]">
                Join thousands of job seekers who are optimizing their applications with ResumeRocket. Get started for free today.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 mt-4">
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
              <div className="flex items-center gap-2 mt-4 text-primary-foreground/70 text-sm">
                <CheckCircleIcon className="h-4 w-4" />
                <span>No credit card required</span>
              </div>
            </div>
            <div className="p-6 bg-primary-foreground/10 rounded-lg border border-primary-foreground/20">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex flex-col space-y-2 p-4 rounded-lg bg-primary-foreground/5 border border-primary-foreground/20">
                  <div className="flex items-center space-x-2">
                    <FileTextIcon className="h-5 w-5" />
                    <span className="font-medium">10+ Resume Templates</span>
                  </div>
                </div>
                <div className="flex flex-col space-y-2 p-4 rounded-lg bg-primary-foreground/5 border border-primary-foreground/20">
                  <div className="flex items-center space-x-2">
                    <BuildingIcon className="h-5 w-5" />
                    <span className="font-medium">Industry-Specific AI</span>
                  </div>
                </div>
                <div className="flex flex-col space-y-2 p-4 rounded-lg bg-primary-foreground/5 border border-primary-foreground/20">
                  <div className="flex items-center space-x-2">
                    <TargetIcon className="h-5 w-5" />
                    <span className="font-medium">ATS Optimization</span>
                  </div>
                </div>
                <div className="flex flex-col space-y-2 p-4 rounded-lg bg-primary-foreground/5 border border-primary-foreground/20">
                  <div className="flex items-center space-x-2">
                    <LineChartIcon className="h-5 w-5" />
                    <span className="font-medium">Performance Analytics</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}