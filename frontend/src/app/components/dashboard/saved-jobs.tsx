"use client"

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BriefcaseIcon, ClockIcon, MapPinIcon, ArrowRightIcon } from "lucide-react";
import Link from "next/link";

interface JobCardProps {
  title: string;
  company: string;
  location: string;
  salary?: string;
  postedDate: string;
  logoUrl?: string;
  featured?: boolean;
}

function JobCard({
  title,
  company,
  location,
  salary,
  postedDate,
  logoUrl,
  featured = false,
}: JobCardProps) {
  return (
    <div
      className={`p-4 border-b border-gray-200 dark:border-gray-700 last:border-0 ${
        featured
          ? "bg-blue-50/50 dark:bg-blue-900/10"
          : ""
      }`}
    >
      <div className="flex items-start gap-3">
        <div
          className="h-12 w-12 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center overflow-hidden flex-shrink-0"
        >
          {logoUrl ? (
            <img
              src={logoUrl}
              alt={company}
              className="h-full w-full object-cover"
            />
          ) : (
            <BriefcaseIcon className="h-6 w-6 text-gray-400" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div>
              <h3
                className="font-medium text-gray-900 dark:text-white truncate"
              >
                {title}
              </h3>
              <p
                className="text-sm text-gray-500 dark:text-gray-400"
              >
                {company}
              </p>
            </div>
            {featured && (
              <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 border-blue-200 dark:border-blue-800">
                Featured
              </Badge>
            )}
          </div>
          <div
            className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500 dark:text-gray-400 mt-2"
          >
            <span className="flex items-center">
              <MapPinIcon className="h-3 w-3 mr-1" />
              {location}
            </span>
            {salary && (
              <>
                <span
                  className="inline-block"
                >
                  •
                </span>
                <span>{salary}</span>
              </>
            )}
            <span
              className="inline-block"
            >
              •
            </span>
            <span className="flex items-center">
              <ClockIcon className="h-3 w-3 mr-1" />
              {postedDate}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SavedJobs() {
  const savedJobs = [
    {
      title: "Senior React Developer",
      company: "TechCorp Inc.",
      location: "San Francisco, CA",
      salary: "$120K - $150K",
      postedDate: "2 days ago",
      logoUrl:
        "https://images.unsplash.com/photo-1549924231-f129b911e442?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
      featured: true,
    },
    {
      title: "Product Manager",
      company: "Innovate Labs",
      location: "Remote",
      salary: "$100K - $130K",
      postedDate: "3 days ago",
      logoUrl:
        "https://images.unsplash.com/photo-1568822617270-2c1579f8dfe2?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
    },
    {
      title: "UX/UI Designer",
      company: "Creative Solutions",
      location: "New York, NY",
      salary: "$90K - $110K",
      postedDate: "1 week ago",
      logoUrl:
        "https://images.unsplash.com/photo-1572044162444-ad60f128bdea?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
    },
  ];

  return (
    <Card className="h-full">
      <CardHeader
        className="flex flex-row items-center justify-between pb-2"
      >
        <div>
          <CardTitle>Saved Jobs</CardTitle>
          <CardDescription>
            Jobs you're interested in applying to
          </CardDescription>
        </div>
        <Button variant="ghost" size="sm" className="gap-1" asChild>
          <Link href="#">
            View all <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent className="p-0">
        {savedJobs.map((job, index) => (
          <JobCard key={index} {...job} />
        ))}
      </CardContent>
    </Card>
  );
}