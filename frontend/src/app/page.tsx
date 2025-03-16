"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold">Resume Rocket</h1>
          <nav>
            <ul className="flex space-x-4">
              <li>
                <Link href="/resume-upload">Upload Resume</Link>
              </li>
              <li>
                <Link href="/dashboard">Dashboard</Link>
              </li>
            </ul>
          </nav>
        </div>
      </header>
      
      <main className="flex flex-1 flex-col items-center justify-center p-6">
        <div className="max-w-3xl text-center">
          <h2 className="text-4xl font-bold mb-4">Optimize Your Resume</h2>
          <p className="text-xl mb-8">
            Upload your resume and get AI-powered suggestions to improve your
            chances of landing your dream job.
          </p>
          <Button asChild size="lg">
            <Link href="/resume-upload">Get Started</Link>
          </Button>
        </div>
      </main>
      
      <footer className="border-t py-6">
        <div className="container mx-auto px-4 text-center">
          <p>© 2025 Resume Rocket. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}