"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Toaster } from "@/components/ui/toaster";
import { FileTextIcon, BarChartIcon, ArrowRightIcon } from "lucide-react";
import MobileNav from "@/components/navigation/mobile-nav";

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Public header */}
      <header className="sticky top-0 z-10 border-b bg-background">
        <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link href="/" className="flex items-center gap-2">
            <span className="font-bold text-xl">ResumeRocket</span>
          </Link>
          
          <nav className="hidden md:flex items-center gap-6">
            <Link 
              href="/features" 
              className={`text-sm font-medium transition-colors hover:text-primary ${
                pathname === "/features" ? "text-primary" : "text-muted-foreground"
              }`}
            >
              Features
            </Link>
            <Link 
              href="/pricing" 
              className={`text-sm font-medium transition-colors hover:text-primary ${
                pathname === "/pricing" ? "text-primary" : "text-muted-foreground"
              }`}
            >
              Pricing
            </Link>
            <Link 
              href="/about" 
              className={`text-sm font-medium transition-colors hover:text-primary ${
                pathname === "/about" ? "text-primary" : "text-muted-foreground"
              }`}
            >
              About
            </Link>
          </nav>
          
          <div className="flex items-center gap-4">
            {pathname !== "/login" && (
              <Link href="/login" passHref legacyBehavior>
                <Button variant="ghost" size="sm">
                  Log in
                </Button>
              </Link>
            )}
            {pathname !== "/register" && (
              <Link href="/register" passHref legacyBehavior>
                <Button size="sm">
                  Sign up
                </Button>
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Mobile navigation drawer to be added here if needed */}

      {/* Main content */}
      <main className="flex-1">
        {pathname === "/" ? (
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        ) : (
          <div className="container mx-auto px-4 py-8 sm:px-6 lg:px-8 max-w-md">
            {children}
          </div>
        )}
      </main>

      {/* Footer only for landing page */}
      {pathname === "/" && (
        <footer className="border-t bg-background">
          <div className="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <h3 className="text-base font-medium">Product</h3>
                <ul className="mt-4 space-y-2">
                  <li>
                    <Link href="/features" className="text-sm text-muted-foreground hover:text-foreground">
                      Features
                    </Link>
                  </li>
                  <li>
                    <Link href="/pricing" className="text-sm text-muted-foreground hover:text-foreground">
                      Pricing
                    </Link>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-base font-medium">Resources</h3>
                <ul className="mt-4 space-y-2">
                  <li>
                    <Link href="/blog" className="text-sm text-muted-foreground hover:text-foreground">
                      Blog
                    </Link>
                  </li>
                  <li>
                    <Link href="/guides" className="text-sm text-muted-foreground hover:text-foreground">
                      Resume Guides
                    </Link>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-base font-medium">Company</h3>
                <ul className="mt-4 space-y-2">
                  <li>
                    <Link href="/about" className="text-sm text-muted-foreground hover:text-foreground">
                      About us
                    </Link>
                  </li>
                  <li>
                    <Link href="/contact" className="text-sm text-muted-foreground hover:text-foreground">
                      Contact
                    </Link>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-base font-medium">Legal</h3>
                <ul className="mt-4 space-y-2">
                  <li>
                    <Link href="/privacy" className="text-sm text-muted-foreground hover:text-foreground">
                      Privacy Policy
                    </Link>
                  </li>
                  <li>
                    <Link href="/terms" className="text-sm text-muted-foreground hover:text-foreground">
                      Terms of Service
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
            <div className="mt-8 border-t pt-8 flex flex-col sm:flex-row justify-between items-center">
              <p className="text-sm text-muted-foreground">
                &copy; {new Date().getFullYear()} ResumeRocket. All rights reserved.
              </p>
              <div className="mt-4 sm:mt-0 flex space-x-6">
                <Link href="https://twitter.com" className="text-muted-foreground hover:text-foreground">
                  <span className="sr-only">Twitter</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
                    <path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"></path>
                  </svg>
                </Link>
                <Link href="https://github.com" className="text-muted-foreground hover:text-foreground">
                  <span className="sr-only">GitHub</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
                    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path>
                    <path d="M9 18c-4.51 2-5-2-7-2"></path>
                  </svg>
                </Link>
                <Link href="https://linkedin.com" className="text-muted-foreground hover:text-foreground">
                  <span className="sr-only">LinkedIn</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
                    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                    <rect width="4" height="12" x="2" y="9"></rect>
                    <circle cx="4" cy="4" r="2"></circle>
                  </svg>
                </Link>
              </div>
            </div>
          </div>
        </footer>
      )}
      <Toaster />
      <MobileNav />
    </div>
  );
}