"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { 
  HomeIcon, 
  FileTextIcon, 
  BriefcaseIcon, 
  SettingsIcon, 
  LogOutIcon,
  MenuIcon,
  XIcon,
  UserIcon,
  PlusIcon,
  FileUpIcon
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { 
  Sheet, 
  SheetContent, 
  SheetHeader, 
  SheetTitle, 
  SheetTrigger,
  SheetClose
} from "@/components/ui/sheet";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger 
} from "@/components/ui/tooltip";

export default function MobileNav() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();
  const [open, setOpen] = useState(false);
  
  // Get user initials for the avatar fallback
  const userInitials = user?.name 
    ? user.name.split(" ").map(part => part[0]).join("").toUpperCase() 
    : "U";

  // Navigation items for authenticated users
  const authNavItems = [
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

  // Public navigation items
  const publicNavItems = [
    {
      href: "/features",
      label: "Features",
      active: pathname === "/features",
    },
    {
      href: "/pricing",
      label: "Pricing",
      active: pathname === "/pricing",
    },
    {
      href: "/about",
      label: "About",
      active: pathname === "/about",
    },
  ];

  return (
    <>
      {/* Mobile Floating Action Buttons */}
      {isAuthenticated && (
        <div className="fixed bottom-4 right-4 flex flex-col gap-2 md:hidden">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Link href="/resume-upload">
                  <Button size="icon" className="h-12 w-12 rounded-full shadow-lg">
                    <FileUpIcon className="h-5 w-5" />
                    <span className="sr-only">Upload Resume</span>
                  </Button>
                </Link>
              </TooltipTrigger>
              <TooltipContent side="left">
                <p>Upload Resume</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      )}

      {/* Mobile Navigation */}
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-background border-t md:hidden">
        <div className="grid grid-cols-4 h-16">
          {isAuthenticated ? (
            // Authenticated mobile tabs
            <>
              {authNavItems.slice(0, 3).map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex flex-col items-center justify-center h-full ${
                    item.active 
                      ? "text-primary" 
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <item.icon className="h-5 w-5" />
                  <span className="text-xs mt-1">{item.label.split(' ')[0]}</span>
                </Link>
              ))}

              {/* Menu Sheet Trigger */}
              <Sheet open={open} onOpenChange={setOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon" className="flex flex-col items-center justify-center h-full rounded-none w-full">
                    <MenuIcon className="h-5 w-5" />
                    <span className="text-xs mt-1">More</span>
                  </Button>
                </SheetTrigger>
                <SheetContent side="bottom" className="h-[85vh] rounded-t-xl">
                  <SheetHeader className="border-b pb-4">
                    <SheetTitle className="text-left flex items-center">
                      <span>Menu</span>
                      <SheetClose asChild>
                        <Button variant="ghost" size="icon" className="ml-auto">
                          <XIcon className="h-5 w-5" />
                        </Button>
                      </SheetClose>
                    </SheetTitle>
                  </SheetHeader>
                  
                  <div className="py-4">
                    <div className="flex items-center p-2 mb-4">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={user?.avatar_url || ""} />
                        <AvatarFallback>{userInitials}</AvatarFallback>
                      </Avatar>
                      <div className="ml-3">
                        <p className="text-sm font-medium">{user?.name || "User"}</p>
                        <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                          {user?.email}
                        </p>
                      </div>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="ml-auto" 
                        onClick={() => logout()}
                      >
                        <LogOutIcon className="h-5 w-5" />
                      </Button>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4">
                      {/* Quick Actions */}
                      <Link href="/resume-upload" onClick={() => setOpen(false)}>
                        <div className="flex flex-col items-center justify-center p-4 rounded-lg border hover:bg-accent">
                          <FileUpIcon className="h-6 w-6 mb-2" />
                          <span className="text-xs text-center">Upload Resume</span>
                        </div>
                      </Link>
                      <Link href="/job-input" onClick={() => setOpen(false)}>
                        <div className="flex flex-col items-center justify-center p-4 rounded-lg border hover:bg-accent">
                          <PlusIcon className="h-6 w-6 mb-2" />
                          <span className="text-xs text-center">Add Job</span>
                        </div>
                      </Link>
                      <Link href="/profile" onClick={() => setOpen(false)}>
                        <div className="flex flex-col items-center justify-center p-4 rounded-lg border hover:bg-accent">
                          <UserIcon className="h-6 w-6 mb-2" />
                          <span className="text-xs text-center">Profile</span>
                        </div>
                      </Link>
                    </div>
                    
                    {/* All menu items */}
                    <div className="mt-6">
                      <h3 className="text-sm font-medium px-2 mb-2">All Pages</h3>
                      <div className="space-y-1">
                        {authNavItems.map((item) => (
                          <SheetClose asChild key={item.href}>
                            <Link
                              href={item.href}
                              className={`flex items-center gap-2 px-2 py-2 rounded-md ${
                                item.active ? "bg-accent" : "hover:bg-accent/50"
                              }`}
                            >
                              <item.icon className="h-5 w-5" />
                              <span>{item.label}</span>
                            </Link>
                          </SheetClose>
                        ))}
                        <SheetClose asChild>
                          <Link
                            href="/settings"
                            className="flex items-center gap-2 px-2 py-2 rounded-md hover:bg-accent/50"
                          >
                            <SettingsIcon className="h-5 w-5" />
                            <span>Settings</span>
                          </Link>
                        </SheetClose>
                      </div>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
            </>
          ) : (
            // Public mobile tabs
            <>
              <Link
                href="/"
                className={`flex flex-col items-center justify-center h-full ${
                  pathname === "/" 
                    ? "text-primary" 
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <HomeIcon className="h-5 w-5" />
                <span className="text-xs mt-1">Home</span>
              </Link>
              
              {publicNavItems.slice(0, 2).map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex flex-col items-center justify-center h-full ${
                    item.active 
                      ? "text-primary" 
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <span className="text-xs mt-1">{item.label}</span>
                </Link>
              ))}
              
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon" className="flex flex-col items-center justify-center h-full rounded-none w-full">
                    <MenuIcon className="h-5 w-5" />
                    <span className="text-xs mt-1">Menu</span>
                  </Button>
                </SheetTrigger>
                <SheetContent side="bottom" className="h-[40vh] rounded-t-xl">
                  <SheetHeader className="border-b pb-4">
                    <SheetTitle className="text-left flex items-center">
                      <span>Menu</span>
                      <SheetClose asChild>
                        <Button variant="ghost" size="icon" className="ml-auto">
                          <XIcon className="h-5 w-5" />
                        </Button>
                      </SheetClose>
                    </SheetTitle>
                  </SheetHeader>
                  
                  <div className="py-4">
                    <div className="flex flex-col gap-4">
                      <SheetClose asChild>
                        <Link href="/login">
                          <Button variant="outline" className="w-full">Log in</Button>
                        </Link>
                      </SheetClose>
                      <SheetClose asChild>
                        <Link href="/register">
                          <Button className="w-full">Sign up</Button>
                        </Link>
                      </SheetClose>
                    </div>
                    
                    <div className="mt-6">
                      <div className="space-y-1">
                        {publicNavItems.map((item) => (
                          <SheetClose asChild key={item.href}>
                            <Link
                              href={item.href}
                              className={`flex items-center px-2 py-2 rounded-md ${
                                item.active ? "bg-accent" : "hover:bg-accent/50"
                              }`}
                            >
                              <span>{item.label}</span>
                            </Link>
                          </SheetClose>
                        ))}
                      </div>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
            </>
          )}
        </div>
      </div>
    </>
  );
}