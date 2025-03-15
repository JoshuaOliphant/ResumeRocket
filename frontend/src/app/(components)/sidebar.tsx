"use client"

import React, { useState } from "react";
import {
  HomeIcon,
  FileTextIcon,
  BriefcaseIcon,
  SettingsIcon,
  UserIcon,
  MenuIcon,
  XIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface SidebarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
}

export function Sidebar({ currentPage, setCurrentPage }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: HomeIcon },
    { id: "resumes", label: "My Resumes", icon: FileTextIcon },
    { id: "jobs", label: "Job Listings", icon: BriefcaseIcon },
    { id: "profile", label: "Profile", icon: UserIcon },
    { id: "settings", label: "Settings", icon: SettingsIcon },
  ];

  return (
    <>
      <div
        className={`fixed inset-0 bg-black/50 z-20 transition-opacity duration-200 md:hidden ${
          collapsed ? "opacity-0 pointer-events-none" : "opacity-100"
        }`}
        onClick={() => setCollapsed(true)}
      />

      <aside
        className={`fixed md:relative z-30 flex h-screen flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ${
          collapsed ? "-translate-x-full md:translate-x-0 md:w-20" : "w-64"
        }`}
      >
        <div
          className="flex h-14 items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center">
            {!collapsed && (
              <span
                className="text-xl font-bold text-gray-900 dark:text-white"
              >
                ResumeRocket
              </span>
            )}

            {collapsed && (
              <span
                className="text-xl font-bold text-gray-900 dark:text-white"
              >
                RR
              </span>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setCollapsed(true)}
          >
            <XIcon className="h-5 w-5" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-2">
            {navItems.map((item, index) => (
              <Button
                key={item.id}
                variant={currentPage === item.id ? "secondary" : "ghost"}
                className={`w-full justify-start ${collapsed ? "justify-center" : ""}`}
                onClick={() => setCurrentPage(item.id)}
                id={`fzwyp5_${index}`}
              >
                <item.icon
                  className={`h-5 w-5 ${collapsed ? "" : "mr-3"}`}
                  id={`j6ob9i_${index}`}
                />
                {!collapsed && <span id={`bjxe3u_${index}`}>{item.label}</span>}
              </Button>
            ))}
          </nav>
        </div>

        <div
          className="border-t border-gray-200 dark:border-gray-700 p-4"
        >
          <div className="flex items-center">
            <Avatar>
              <AvatarImage
                src="https://github.com/yusufhilmi.png"
              />
              <AvatarFallback>YH</AvatarFallback>
            </Avatar>
            {!collapsed && (
              <div className="ml-3">
                <p
                  className="text-sm font-medium text-gray-900 dark:text-white"
                >
                  Yusuf Hilmi
                </p>
                <p
                  className="text-xs text-gray-500 dark:text-gray-400"
                >
                  Premium Plan
                </p>
              </div>
            )}
          </div>
        </div>
      </aside>

      <Button
        variant="outline"
        size="icon"
        className="fixed bottom-4 left-4 z-40 md:hidden"
        onClick={() => setCollapsed(false)}
      >
        <MenuIcon className="h-5 w-5" />
      </Button>
    </>
  );
}
