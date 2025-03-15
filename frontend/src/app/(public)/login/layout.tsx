"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { Card } from "@/components/ui/card";

// This is a special layout for auth pages that displays a simpler, more focused UI
export default function AuthPagesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  
  // Determine which auth page this is for the title
  const pageTitle = pathname === "/login" 
    ? "Log In" 
    : pathname === "/register" 
      ? "Create an Account" 
      : pathname === "/reset-password" 
        ? "Reset Password" 
        : "Account";

  return (
    <div className="container flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] py-8">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">{pageTitle}</h1>
          <p className="text-sm text-muted-foreground">
            {pathname === "/login" 
              ? "Enter your credentials to access your account" 
              : pathname === "/register" 
                ? "Enter your information to create an account" 
                : pathname === "/reset-password" 
                  ? "Enter your email to reset your password" 
                  : "Manage your account"}
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}