"use client"

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ZapIcon } from "lucide-react";

export function Header() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
  }, []);

  const handleSignOut = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    router.push("/auth/login");
  };

  return (
    <header
      className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950"
    >
      <div
        className="container mx-auto px-4 py-4 flex items-center justify-between"
      >
        <div className="flex items-center gap-2">
          <ZapIcon
            className="h-6 w-6 text-blue-600 dark:text-blue-500"
          />
          <Link href="/" className="font-bold text-xl text-gray-900 dark:text-white">
            ResumeRocket
          </Link>
        </div>
        <nav className="hidden md:flex items-center space-x-6">
          <Link
            href="/resume-upload"
            className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
          >
            Upload Resume
          </Link>
          {isAuthenticated && (
            <>
              <Link
                href="/dashboard"
                className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
              >
                Dashboard
              </Link>
              <Link
                href="/resume-management"
                className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
              >
                Manage Resumes
              </Link>
            </>
          )}
        </nav>
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Button
              variant="outline"
              className="hidden md:inline-flex"
              onClick={handleSignOut}
            >
              Sign Out
            </Button>
          ) : (
            <Button
              variant="outline"
              className="hidden md:inline-flex"
              onClick={() => router.push("/auth/login")}
            >
              Sign In
            </Button>
          )}
          <Button asChild>
            <Link href="/resume-upload">Get Started</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}