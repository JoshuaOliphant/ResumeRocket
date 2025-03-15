"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileTextIcon } from "lucide-react";

// This layout is for all authentication-related pages (login, register, reset password)
// It provides a more focused, minimal UI compared to the public layout
export default function AuthPagesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left side - branding and messaging */}
      <div className="hidden lg:flex relative flex-col justify-between bg-muted/80 p-10">
        <div>
          <Link href="/" className="flex items-center gap-2">
            <FileTextIcon className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">ResumeRocket</span>
          </Link>
        </div>
        
        <div className="relative z-20 mt-auto">
          <blockquote className="space-y-2">
            <p className="text-lg">
              "ResumeRocket helped me transform my resume and land my dream job at a Fortune 500 company. The AI-powered recommendations were exactly what I needed."
            </p>
            <footer className="text-sm">
              Sofia Chen — Senior Product Manager
            </footer>
          </blockquote>
        </div>
        
        {/* Background decoration */}
        <div className="absolute inset-0 z-10">
          <div className="absolute left-1/2 top-1/2 -translate-y-1/2 -translate-x-1/2 lg:translate-x-0 xl:translate-x-0 h-[800px] w-[800px] rounded-full bg-primary/5"></div>
          <div className="absolute right-0 bottom-0 h-[400px] w-[400px] rounded-full bg-primary/10"></div>
          <div className="absolute left-0 top-0 h-[300px] w-[300px] rounded-full bg-primary/10"></div>
        </div>
      </div>
      
      {/* Right side - auth form */}
      <div className="flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
          <div className="flex flex-col space-y-2 text-center">
            <Link href="/" className="mx-auto flex items-center gap-2 lg:hidden mb-4">
              <FileTextIcon className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">ResumeRocket</span>
            </Link>
            
            <h1 className="text-2xl font-semibold tracking-tight">
              {pathname === "/login" 
                ? "Welcome back" 
                : pathname === "/register" 
                  ? "Create an account" 
                  : pathname.includes("reset-password") 
                    ? "Reset your password" 
                    : "Account Access"}
            </h1>
            <p className="text-sm text-muted-foreground">
              {pathname === "/login" 
                ? "Enter your credentials to access your account" 
                : pathname === "/register" 
                  ? "Enter your information to create an account" 
                  : pathname.includes("reset-password") 
                    ? "We'll send you a link to reset your password" 
                    : "Manage your account"}
            </p>
          </div>
          
          {children}
          
          <p className="px-8 text-center text-sm text-muted-foreground">
            By clicking continue, you agree to our{" "}
            <Link 
              href="/terms" 
              className="underline underline-offset-4 hover:text-primary"
            >
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link 
              href="/privacy" 
              className="underline underline-offset-4 hover:text-primary"
            >
              Privacy Policy
            </Link>
            .
          </p>
        </div>
      </div>
    </div>
  );
}