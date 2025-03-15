"use client"

import React from "react";
import { Sidebar } from "(components)/sidebar";

interface LayoutProps {
  children: React.ReactNode;
  currentPage: string;
  setCurrentPage: (page: string) => void;
}

export default function Layout({
  children,
  currentPage,
  setCurrentPage,
}: LayoutProps) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
      />
      <main className="flex-1 overflow-y-auto p-4 md:p-6">
        {children}
      </main>
    </div>
  );
}
