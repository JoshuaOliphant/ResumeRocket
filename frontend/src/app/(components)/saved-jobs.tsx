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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BriefcaseIcon,
  BookmarkIcon,
  StarIcon,
  MapPinIcon,
  CalendarIcon,
} from "lucide-react";

interface JobCardProps {
  title: string;
  company: string;
  location: string;
  salary: string;
  posted: string;
  matchScore: number;
  logoUrl?: string;
  isFavorite?: boolean;
}

function JobCard({
  title,
  company,
  location,
  salary,
  posted,
  matchScore,
  logoUrl,
  isFavorite = false,
}: JobCardProps) {
  return (
    <Card
      className="group overflow-hidden transition-all duration-200 hover:shadow-md"
    >
      <CardContent className="p-0">
        <div className="flex items-start p-4">
          <div
            className="h-12 w-12 rounded-md bg-gray-100 dark:bg-gray-700 flex items-center justify-center overflow-hidden mr-4"
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
          <div className="flex-1">
            <div className="flex items-start justify-between">
              <div>
                <h3
                  className="font-medium text-gray-900 dark:text-white"
                >
                  {title}
                </h3>
                <p
                  className="text-sm text-gray-500 dark:text-gray-400"
                >
                  {company}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {isFavorite ? (
                  <StarIcon
                    className="h-4 w-4 fill-yellow-400 text-yellow-400"
                  />
                ) : (
                  <BookmarkIcon className="h-4 w-4" />
                )}
              </Button>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              <div
                className="flex items-center text-xs text-gray-500 dark:text-gray-400"
              >
                <MapPinIcon className="mr-1 h-3 w-3" />
                {location}
              </div>
              <div
                className="flex items-center text-xs text-gray-500 dark:text-gray-400"
              >
                <CalendarIcon className="mr-1 h-3 w-3" />
                {posted}
              </div>
              <Badge variant="outline" className="ml-auto">
                {salary}
              </Badge>
            </div>
          </div>
        </div>
        <div
          className="border-t border-gray-100 dark:border-gray-800 px-4 py-3 bg-gray-50 dark:bg-gray-800/50 flex justify-between items-center"
        >
          <Badge
            variant={matchScore >= 80 ? "default" : "secondary"}
          >
            {matchScore}% Match
          </Badge>
          <Button size="sm">
            Optimize Resume
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function SavedJobs() {
  const savedJobs = [
    {
      title: "Senior Frontend Developer",
      company: "TechCorp Inc.",
      location: "San Francisco, CA",
      salary: "$120K - $150K",
      posted: "2 days ago",
      matchScore: 92,
      logoUrl:
        "https://images.unsplash.com/photo-1549924231-f129b911e442?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
      isFavorite: true,
    },
    {
      title: "UX/UI Designer",
      company: "Creative Solutions",
      location: "Remote",
      salary: "$90K - $110K",
      posted: "1 week ago",
      matchScore: 78,
      logoUrl:
        "https://images.unsplash.com/photo-1572044162444-ad60f128bdea?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
    },
    {
      title: "Product Manager",
      company: "Innovate Labs",
      location: "New York, NY",
      salary: "$130K - $160K",
      posted: "3 days ago",
      matchScore: 65,
      logoUrl:
        "https://images.unsplash.com/photo-1568822617270-2c1579f8dfe2?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
      isFavorite: true,
    },
    {
      title: "Full Stack Developer",
      company: "Growth Startup",
      location: "Austin, TX",
      salary: "$100K - $130K",
      posted: "Just now",
      matchScore: 88,
      logoUrl:
        "https://images.unsplash.com/photo-1559136555-9303baea8ebd?ixlib=rb-1.2.1&auto=format&fit=crop&w=50&h=50&q=80",
    },
  ];

  const appliedJobs = savedJobs.slice(0, 2);
  const favoriteJobs = savedJobs.filter((job) => job.isFavorite);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Saved Jobs</CardTitle>
        <CardDescription>
          Jobs you've saved for later
        </CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs defaultValue="all" className="px-4 pt-2">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="all">
              All
            </TabsTrigger>
            <TabsTrigger value="favorites">
              Favorites
            </TabsTrigger>
            <TabsTrigger value="applied">
              Applied
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="pt-4 pb-2 px-2">
            <div className="space-y-4">
              {savedJobs.map((job, index) => (
                <JobCard key={index} {...job} id={`jfopdl_${index}`} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="favorites" className="pt-4 pb-2 px-2">
            <div className="space-y-4">
              {favoriteJobs.map((job, index) => (
                <JobCard key={index} {...job} id={`jxhphv_${index}`} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="applied" className="pt-4 pb-2 px-2">
            <div className="space-y-4">
              {appliedJobs.map((job, index) => (
                <JobCard key={index} {...job} id={`ixerhh_${index}`} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
