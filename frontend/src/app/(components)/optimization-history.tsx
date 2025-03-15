"use client"

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  FileTextIcon,
  ClockIcon,
  DownloadIcon,
  EyeIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from "lucide-react";

interface OptimizationHistoryItemProps {
  version: string;
  jobTitle: string;
  company: string;
  date: string;
  changePercentage: number;
}

function OptimizationHistoryItem({
  version,
  jobTitle,
  company,
  date,
  changePercentage,
}: OptimizationHistoryItemProps) {
  const isPositive = changePercentage > 0;

  return (
    <div
      className="flex items-start py-3 border-b border-gray-100 dark:border-gray-800 last:border-0"
    >
      <div
        className="h-8 w-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center mr-3"
      >
        <FileTextIcon
          className="h-4 w-4 text-gray-500 dark:text-gray-400"
        />
      </div>
      <div className="flex-1">
        <div className="flex items-start justify-between">
          <div>
            <h4
              className="font-medium text-sm text-gray-900 dark:text-white"
            >
              {jobTitle}
            </h4>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {company}
            </p>
          </div>
          <Badge variant="outline" className="text-xs">
            {version}
          </Badge>
        </div>
        <div className="mt-1 flex items-center text-xs">
          <ClockIcon className="h-3 w-3 mr-1 text-gray-400" />
          <span className="text-gray-500 dark:text-gray-400">
            {date}
          </span>

          <div
            className={`ml-auto flex items-center ${isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}
          >
            {isPositive ? (
              <ArrowUpIcon className="h-3 w-3 mr-1" />
            ) : (
              <ArrowDownIcon className="h-3 w-3 mr-1" />
            )}

            <span>{Math.abs(changePercentage)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function OptimizationHistory() {
  const historyItems = [
    {
      version: "v3.0",
      jobTitle: "Senior Frontend Developer",
      company: "TechCorp Inc.",
      date: "Today, 2:30 PM",
      changePercentage: 12,
    },
    {
      version: "v2.5",
      jobTitle: "Frontend Team Lead",
      company: "Digital Innovations",
      date: "Yesterday, 10:15 AM",
      changePercentage: 8,
    },
    {
      version: "v2.0",
      jobTitle: "React Developer",
      company: "WebSolutions Ltd.",
      date: "Aug 15, 2023",
      changePercentage: 15,
    },
    {
      version: "v1.5",
      jobTitle: "Frontend Developer",
      company: "Creative Tech",
      date: "Jul 28, 2023",
      changePercentage: -3,
    },
    {
      version: "v1.0",
      jobTitle: "Web Developer",
      company: "StartUp Inc.",
      date: "Jul 10, 2023",
      changePercentage: 0,
    },
    {
      version: "v0.5",
      jobTitle: "Junior Developer",
      company: "First Company",
      date: "Jun 5, 2023",
      changePercentage: 5,
    },
  ];

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Optimization History</CardTitle>
        <CardDescription>Previous resume versions</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px]">
          <div className="px-4">
            {historyItems.map((item, index) => (
              <OptimizationHistoryItem
                key={index}
                {...item}
                id={`gs0niy_${index}`}
              />
            ))}
          </div>
        </ScrollArea>
        <div
          className="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-between"
        >
          <Button variant="outline" size="sm" className="gap-1">
            <DownloadIcon className="h-4 w-4" />
            Export
          </Button>
          <Button variant="secondary" size="sm" className="gap-1">
            <EyeIcon className="h-4 w-4" />
            Compare Versions
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
