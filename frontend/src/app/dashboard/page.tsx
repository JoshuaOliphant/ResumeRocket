"use client"

import React from "react";
import { RecentOptimizations } from "(components)/recent-optimizations";
import { StatisticsSection } from "(components)/statistics-section";
import { SavedJobs } from "(components)/saved-jobs";
import { OptimizationHistory } from "(components)/optimization-history";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1
          className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white"
        >
          Dashboard
        </h1>
        <div className="flex items-center space-x-2">
          <span
            className="text-sm text-gray-500 dark:text-gray-400"
          >
            Last updated: Today, 2:30 PM
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <RecentOptimizations />
        <StatisticsSection />
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <SavedJobs />
        </div>
        <div className="md:col-span-1">
          <OptimizationHistory />
        </div>
      </div>
    </div>
  );
}
