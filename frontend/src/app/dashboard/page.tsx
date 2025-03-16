"use client";

import React from "react";
import { Header } from "../components/header";
import { Footer } from "../components/footer";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { PlusIcon, FileTextIcon, BriefcaseIcon, SettingsIcon, UserIcon } from "lucide-react";
import { RecentOptimizations } from "../components/dashboard/recent-optimizations";
import { StatisticsSection } from "../components/dashboard/statistics-section";
import { SavedJobs } from "../components/dashboard/saved-jobs";

export default function DashboardPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Welcome back! Track your resume optimization progress
            </p>
          </div>
          
          <div className="flex gap-3">
            <Button asChild>
              <Link href="/resume-upload">
                <PlusIcon className="h-5 w-5 mr-2" />
                New Optimization
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/resume-management">
                <FileTextIcon className="h-5 w-5 mr-2" />
                My Resumes
              </Link>
            </Button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <StatisticsSection />
          </div>
          <div>
            <div className="bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800 h-full">
              <div className="p-6">
                <div className="flex items-center justify-center h-32 w-32 mx-auto rounded-full bg-gray-100 dark:bg-gray-800 mb-4">
                  <UserIcon className="h-16 w-16 text-gray-400" />
                </div>
                <h2 className="text-xl font-bold text-center mb-1">John Doe</h2>
                <p className="text-gray-500 dark:text-gray-400 text-center mb-4">Software Engineer</p>
                
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Resume Optimizations</span>
                    <span className="font-medium">12</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Saved Jobs</span>
                    <span className="font-medium">8</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Applications Sent</span>
                    <span className="font-medium">5</span>
                  </div>
                </div>
                
                <Button variant="outline" className="w-full" asChild>
                  <Link href="#">
                    <SettingsIcon className="h-4 w-4 mr-2" />
                    Account Settings
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RecentOptimizations />
          <SavedJobs />
        </div>
      </main>
      
      <Footer />
    </div>
  );
}