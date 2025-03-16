"use client";

import React, { useState } from "react";
import { Header } from "../components/header";
import { Footer } from "../components/footer";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ComparisonPanel } from "../components/results/comparison-panel";
import { FloatingActionButton } from "../components/results/floating-action-button";
import { ImprovementScorecard } from "../components/results/improvement-scorecard";
import { SkillsMatchMeter } from "../components/results/skills-match-meter";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ResultsPage() {
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<string[]>([
    "summary-1",
    "experience-1",
    "skills-1",
    "skills-3",
  ]);

  const handleAcceptSuggestion = (id: string) => {
    setAcceptedSuggestions((prev) =>
      prev.includes(id)
        ? prev.filter((item) => item !== id)
        : [...prev, id]
    );
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Resume Optimization Results</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Your resume has been analyzed and optimized for the job description. 
              Review the changes below and choose which suggestions to apply.
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Tabs defaultValue="changes" className="mb-6">
                <TabsList className="mb-4">
                  <TabsTrigger value="changes">Content Changes</TabsTrigger>
                  <TabsTrigger value="full">Full Resume</TabsTrigger>
                </TabsList>
                
                <TabsContent value="changes">
                  <ComparisonPanel 
                    acceptedSuggestions={acceptedSuggestions}
                    onAcceptSuggestion={handleAcceptSuggestion}
                  />
                </TabsContent>
                
                <TabsContent value="full">
                  <div className="bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
                    <div className="text-center py-12">
                      <p className="text-xl mb-6">Full resume comparison will go here</p>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
            
            <div className="space-y-6">
              <ImprovementScorecard />
              <SkillsMatchMeter />
            </div>
          </div>
          
          <div className="mt-8 flex justify-center">
            <Button asChild size="lg" className="mr-4">
              <Link href="/dashboard">Save & Return to Dashboard</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/resume-upload">Optimize Another Resume</Link>
            </Button>
          </div>
        </div>
      </main>
      
      <FloatingActionButton />
      <Footer />
    </div>
  );
}