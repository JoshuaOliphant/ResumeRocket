"use client";

import React from "react";
import { Header } from "../components/header";
import { Footer } from "../components/footer";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { PlusIcon, SearchIcon, FileTextIcon, TrashIcon, DownloadIcon } from "lucide-react";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ResumeManagementPage() {
  // Mock data for resumes
  const resumes = [
    {
      id: 1,
      name: "Software Engineer Resume",
      lastUpdated: "2 days ago",
      size: "245 KB",
      optimizations: 5,
      tags: ["Tech", "Engineering"],
    },
    {
      id: 2,
      name: "Full Stack Developer Resume",
      lastUpdated: "1 week ago",
      size: "312 KB",
      optimizations: 3,
      tags: ["Tech", "Full Stack"],
    },
    {
      id: 3,
      name: "Product Manager Resume",
      lastUpdated: "2 weeks ago",
      size: "198 KB",
      optimizations: 2,
      tags: ["Product", "Management"],
    },
    {
      id: 4,
      name: "UX/UI Designer Resume",
      lastUpdated: "1 month ago",
      size: "275 KB",
      optimizations: 1,
      tags: ["Design", "UX/UI"],
    },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold">Resume Management</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Manage your resumes and optimization history
            </p>
          </div>
          
          <div className="flex gap-3">
            <Button asChild>
              <Link href="/resume-upload">
                <PlusIcon className="h-5 w-5 mr-2" />
                Upload New Resume
              </Link>
            </Button>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800 mb-8">
          <div className="p-4 flex items-center">
            <div className="relative flex-1 max-w-md">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search resumes..."
                className="w-full py-2 pl-10 pr-4 border border-gray-300 dark:border-gray-700 rounded-md bg-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600"
              />
            </div>
            <div className="ml-4 flex items-center space-x-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Filter by:
              </span>
              <select className="py-2 px-3 border border-gray-300 dark:border-gray-700 rounded-md bg-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600">
                <option value="all">All Tags</option>
                <option value="tech">Tech</option>
                <option value="design">Design</option>
                <option value="management">Management</option>
              </select>
            </div>
          </div>
        </div>
        
        <Tabs defaultValue="grid">
          <div className="flex justify-between items-center mb-4">
            <TabsList>
              <TabsTrigger value="grid">Grid View</TabsTrigger>
              <TabsTrigger value="list">List View</TabsTrigger>
            </TabsList>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {resumes.length} Resumes
            </div>
          </div>
          
          <TabsContent value="grid">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {resumes.map((resume) => (
                <Card key={resume.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-lg">{resume.name}</CardTitle>
                        <CardDescription>{resume.lastUpdated} • {resume.size}</CardDescription>
                      </div>
                      <FileTextIcon className="h-5 w-5 text-gray-400" />
                    </div>
                  </CardHeader>
                  <CardContent className="pb-2">
                    <div className="flex flex-wrap gap-2 mb-4">
                      {resume.tags.map((tag, index) => (
                        <Badge key={index} variant="secondary">{tag}</Badge>
                      ))}
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Optimizations</span>
                      <span className="font-medium">{resume.optimizations}</span>
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    <Button variant="outline" size="sm">
                      <DownloadIcon className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                    <Button variant="ghost" size="sm" className="text-red-500 dark:text-red-400">
                      <TrashIcon className="h-4 w-4 mr-2" />
                      Delete
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="list">
            <div className="bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800 overflow-hidden">
              <div className="grid grid-cols-12 gap-4 py-3 px-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 text-sm font-medium text-gray-500 dark:text-gray-400">
                <div className="col-span-5">Name</div>
                <div className="col-span-2">Last Updated</div>
                <div className="col-span-2">Size</div>
                <div className="col-span-2">Tags</div>
                <div className="col-span-1">Actions</div>
              </div>
              
              {resumes.map((resume) => (
                <div key={resume.id} className="grid grid-cols-12 gap-4 py-4 px-4 border-b border-gray-200 dark:border-gray-700 last:border-0 items-center">
                  <div className="col-span-5 flex items-center">
                    <FileTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{resume.name}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{resume.optimizations} optimizations</div>
                    </div>
                  </div>
                  <div className="col-span-2 text-gray-600 dark:text-gray-400">{resume.lastUpdated}</div>
                  <div className="col-span-2 text-gray-600 dark:text-gray-400">{resume.size}</div>
                  <div className="col-span-2">
                    <div className="flex flex-wrap gap-1">
                      {resume.tags.map((tag, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">{tag}</Badge>
                      ))}
                    </div>
                  </div>
                  <div className="col-span-1 flex space-x-2">
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <DownloadIcon className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-red-500 dark:text-red-400">
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </main>
      
      <Footer />
    </div>
  );
}