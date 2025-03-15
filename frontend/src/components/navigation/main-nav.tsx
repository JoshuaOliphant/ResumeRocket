"use client";

import React from "react";
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
  UserIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";

interface MainNavProps {
  showMobileMenu?: boolean;
  setShowMobileMenu?: (show: boolean) => void;
}

export default function MainNav({
  showMobileMenu,
  setShowMobileMenu,
}: MainNavProps) {
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

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

  // Navigation items for public pages
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

  // Get user initials for the avatar fallback
  const userInitials = user?.name 
    ? user.name.split(" ").map(part => part[0]).join("").toUpperCase() 
    : "U";

  // Handle mobile menu state
  const handleMobileMenuToggle = (open: boolean) => {
    setIsMobileMenuOpen(open);
    if (setShowMobileMenu) {
      setShowMobileMenu(open);
    }
  };

  return (
    <>
      {/* Desktop navigation */}
      <div className="hidden md:flex items-center gap-6">
        {isAuthenticated ? (
          // Authenticated navigation links
          <>
            {authNavItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 text-sm font-medium transition-colors hover:text-primary ${
                  item.active ? "text-primary" : "text-muted-foreground"
                }`}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}

            {/* User dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user?.avatar_url || ""} />
                    <AvatarFallback>{userInitials}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user?.name}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/profile">
                    <UserIcon className="mr-2 h-4 w-4" />
                    <span>Profile</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings">
                    <SettingsIcon className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  className="text-red-500 focus:text-red-500" 
                  onClick={() => logout()}
                >
                  <LogOutIcon className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </>
        ) : (
          // Public navigation links
          <>
            {publicNavItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  item.active ? "text-primary" : "text-muted-foreground"
                }`}
              >
                {item.label}
              </Link>
            ))}
            
            {/* Auth buttons */}
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
          </>
        )}
      </div>

      {/* Mobile menu trigger */}
      <div className="md:hidden">
        <Sheet open={isMobileMenuOpen} onOpenChange={handleMobileMenuToggle}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MenuIcon className="h-5 w-5" />
              <span className="sr-only">Toggle Menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="pr-0 sm:max-w-xs">
            {isAuthenticated ? (
              // Authenticated mobile menu
              <>
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 px-2 py-4"
                  onClick={() => handleMobileMenuToggle(false)}
                >
                  <span className="font-bold text-xl">ResumeRocket</span>
                </Link>
                
                <div className="mt-2 px-2">
                  <div className="flex items-center gap-2 py-2">
                    <Avatar>
                      <AvatarImage src={user?.avatar_url || ""} />
                      <AvatarFallback>{userInitials}</AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">{user?.name || "User"}</span>
                      <span className="text-xs text-muted-foreground truncate">{user?.email}</span>
                    </div>
                  </div>
                </div>
                
                <nav className="mt-4 flex flex-col gap-2 px-2">
                  {authNavItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => handleMobileMenuToggle(false)}
                      className={`flex items-center gap-2 p-2 rounded-md ${
                        item.active ? "bg-accent" : "hover:bg-accent/50"
                      }`}
                    >
                      <item.icon className="h-5 w-5" />
                      <span>{item.label}</span>
                    </Link>
                  ))}
                  <button
                    onClick={() => {
                      handleMobileMenuToggle(false);
                      logout();
                    }}
                    className="flex items-center gap-2 p-2 text-red-500 rounded-md hover:bg-accent/50 mt-2"
                  >
                    <LogOutIcon className="h-5 w-5" />
                    <span>Logout</span>
                  </button>
                </nav>
              </>
            ) : (
              // Public mobile menu
              <>
                <Link
                  href="/"
                  className="flex items-center gap-2 px-2 py-4"
                  onClick={() => handleMobileMenuToggle(false)}
                >
                  <span className="font-bold text-xl">ResumeRocket</span>
                </Link>
                
                <nav className="mt-4 flex flex-col gap-2 px-2">
                  {publicNavItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => handleMobileMenuToggle(false)}
                      className={`flex items-center gap-2 p-2 rounded-md ${
                        item.active ? "bg-accent" : "hover:bg-accent/50"
                      }`}
                    >
                      <span>{item.label}</span>
                    </Link>
                  ))}
                  
                  <div className="flex flex-col gap-2 mt-4">
                    <Link href="/login" passHref legacyBehavior>
                      <Button variant="outline" className="w-full justify-center">
                        Log in
                      </Button>
                    </Link>
                    <Link href="/register" passHref legacyBehavior>
                      <Button className="w-full justify-center">
                        Sign up
                      </Button>
                    </Link>
                  </div>
                </nav>
              </>
            )}
          </SheetContent>
        </Sheet>
      </div>
    </>
  );
}