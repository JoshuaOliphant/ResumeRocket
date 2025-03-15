"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import ProtectedRoute from "@/components/auth/protected-route";
import MobileNav from "@/components/navigation/mobile-nav";
import {
  HomeIcon,
  FileTextIcon,
  BriefcaseIcon,
  SettingsIcon,
  LogOutIcon,
  MenuIcon,
  AlertCircleIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Toaster } from "@/components/ui/toaster";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Define navigation items
  const navItems = [
    {
      href: "/dashboard",
      label: "Dashboard",
      icon: HomeIcon,
      active: pathname === "/dashboard",
    },
    {
      href: "/resume-upload",
      label: "My Resumes",
      icon: FileTextIcon,
      active: pathname.includes("/resume"),
    },
    {
      href: "/job-management",
      label: "Job Listings",
      icon: BriefcaseIcon,
      active: pathname.includes("/job"),
    },
    {
      href: "/settings",
      label: "Settings",
      icon: SettingsIcon,
      active: pathname === "/settings",
    },
  ];

  // Get user initials for the avatar fallback
  const userInitials = user?.name 
    ? user.name.split(" ").map(part => part[0]).join("").toUpperCase() 
    : "U";

  return (
    <ProtectedRoute>
      <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
        {/* Desktop sidebar */}
        <SidebarProvider defaultOpen={true}>
          <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] min-h-screen">
            <Sidebar variant="sticky" collapsible="icon">
              <SidebarHeader className="flex items-center p-4">
                <Link href="/dashboard" className="flex items-center gap-2">
                  <span className="font-bold text-xl">ResumeRocket</span>
                </Link>
                <SidebarTrigger className="ml-auto" />
              </SidebarHeader>

              <SidebarContent>
                <SidebarMenu>
                  {navItems.map((item) => (
                    <SidebarMenuItem key={item.href}>
                      <Link href={item.href} passHref legacyBehavior>
                        <SidebarMenuButton
                          isActive={item.active}
                          tooltip={item.label}
                        >
                          <item.icon className="mr-2 h-5 w-5" />
                          <span>{item.label}</span>
                        </SidebarMenuButton>
                      </Link>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarContent>

              <SidebarFooter>
                <div className="flex items-center gap-2 p-2">
                  <Avatar>
                    <AvatarImage src={user?.avatar_url || ""} />
                    <AvatarFallback>{userInitials}</AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{user?.name || "User"}</span>
                    <span className="text-xs text-muted-foreground">{user?.email}</span>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="ml-auto" 
                    onClick={() => logout()}
                  >
                    <LogOutIcon className="h-4 w-4" />
                  </Button>
                </div>
              </SidebarFooter>
            </Sidebar>

            {/* Mobile header */}
            <header className="sticky top-0 z-10 flex h-14 items-center gap-4 border-b bg-background px-4 md:hidden">
              <Link href="/dashboard" className="flex items-center gap-2">
                <span className="font-bold">ResumeRocket</span>
              </Link>
              <Avatar className="ml-auto h-8 w-8">
                <AvatarImage src={user?.avatar_url || ""} />
                <AvatarFallback>{userInitials}</AvatarFallback>
              </Avatar>
            </header>

            {/* Main content */}
            <main className="flex-1 overflow-hidden">
              <div className="container mx-auto py-6 px-4 sm:px-6 max-w-6xl">
                {children}
              </div>
            </main>
          </div>
        </SidebarProvider>
        <Toaster />
        <MobileNav />
      </div>
    </ProtectedRoute>
  );
}