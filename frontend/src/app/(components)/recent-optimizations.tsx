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
import { Progress } from "@/components/ui/progress";
import { FileTextIcon, ExternalLinkIcon, ArrowRightIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface OptimizationCardProps {
  jobTitle: string;
  company: string;
  matchScore: number;
  date: string;
  logoUrl?: string;
}

function OptimizationCard({
  jobTitle,
  company,
  matchScore,
  date,
  logoUrl,
}: OptimizationCardProps) {
  const scoreColor =
    matchScore >= 80
      ? "text-green-600 dark:text-green-400"
      : matchScore >= 60
        ? "text-yellow-600 dark:text-yellow-400"
        : "text-red-600 dark:text-red-400";

  return (
    <Card
      className="overflow-hidden transition-all duration-200 hover:shadow-md"
    >
      <CardContent className="p-0">
        <div className="flex items-start p-4">
          <div
            className="h-12 w-12 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center overflow-hidden mr-4"
          >
            {logoUrl ? (
              <img
                src={logoUrl}
                alt={company}
                className="h-full w-full object-cover"
              />
            ) : (
              <FileTextIcon className="h-6 w-6 text-gray-400" />
            )}
          </div>
          <div className="flex-1">
            <h3
              className="font-medium text-gray-900 dark:text-white"
            >
              {jobTitle}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {company}
            </p>
            <div className="mt-2 flex items-center">
              <span className={`text-sm font-medium ${scoreColor}`}>
                {matchScore}% Match
              </span>
              <span
                className="mx-2 text-gray-300 dark:text-gray-600"
              >
                •
              </span>
              <span
                className="text-xs text-gray-500 dark:text-gray-400"
              >
                {date}
              </span>
            </div>
          </div>
          <div className="ml-4">
            <Badge
              variant={matchScore >= 80 ? "default" : "secondary"}
            >
              {matchScore >= 80
                ? "Excellent"
                : matchScore >= 60
                  ? "Good"
                  : "Needs Work"}
            </Badge>
          </div>
        </div>
        <div className="px-4 pb-4">
          <Progress value={matchScore} className="h-1.5" />
        </div>
      </CardContent>
    </Card>
  );
}

export function RecentOptimizations() {
  const recentOptimizations = [
    {
      jobTitle: "Senior Frontend Developer",
      company: "TechCorp Inc.",
      matchScore: 92,
      date: "Today",
      logoUrl:
        "https://images.unsplash.com/photo-1549924231-f129b911e442?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
    },
    {
      jobTitle: "UX/UI Designer",
      company: "Creative Solutions",
      matchScore: 78,
      date: "Yesterday",
      logoUrl:
        "https://images.unsplash.com/photo-1572044162444-ad60f128bdea?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
    },
    {
      jobTitle: "Product Manager",
      company: "Innovate Labs",
      matchScore: 65,
      date: "3 days ago",
      logoUrl:
        "https://images.unsplash.com/photo-1568822617270-2c1579f8dfe2?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
    },
  ];

  return (
    <Card className="h-full">
      <CardHeader
        className="flex flex-row items-center justify-between pb-2"
      >
        <div>
          <CardTitle>Recent Optimizations</CardTitle>
          <CardDescription>
            Your latest resume customizations
          </CardDescription>
        </div>
        <Button variant="ghost" size="sm" className="gap-1">
          View all <ArrowRightIcon className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentOptimizations.map((optimization, index) => (
            <OptimizationCard
              key={index}
              {...optimization}
              id={`o1hmlt_${index}`}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
