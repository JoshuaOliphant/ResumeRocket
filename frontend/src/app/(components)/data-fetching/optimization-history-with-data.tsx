"use client"

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ChartContainer } from "@/components/ui/chart";
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { CartesianGrid, XAxis, YAxis, Tooltip, AreaChart, Area } from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface OptimizationHistoryWithDataProps {
  isLoading?: boolean;
  historyData?: Array<{ date: string; count: number }>;
  error?: string | null;
}

export function OptimizationHistoryWithData({
  isLoading = false,
  historyData = [],
  error = null,
}: OptimizationHistoryWithDataProps) {
  // Default data to show if none is provided
  const defaultData = [
    { date: "Jan 1", count: 3 },
    { date: "Jan 15", count: 5 },
    { date: "Feb 1", count: 2 },
    { date: "Feb 15", count: 6 },
    { date: "Mar 1", count: 8 },
    { date: "Mar 15", count: 3 },
    { date: "Apr 1", count: 5 },
    { date: "Apr 15", count: 7 },
    { date: "May 1", count: 9 },
    { date: "May 15", count: 4 },
    { date: "Jun 1", count: 6 },
    { date: "Jun 15", count: 8 },
  ];

  const displayData = historyData.length > 0 ? historyData : defaultData;
  
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40 mb-2" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[220px] w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Optimization History</CardTitle>
          <CardDescription>
            Your resume customizations over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error || "Failed to load optimization history"}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Optimization History</CardTitle>
        <CardDescription>
          Your resume customizations over time
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={{}} className="h-[220px]">
          <AreaChart
            data={displayData}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="hsl(var(--primary))"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="hsl(var(--primary))"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>
            <ChartTooltip content={<ChartTooltipContent />} />
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tickFormatter={(value) => value.substring(0, 3)}
            />
            <YAxis hide />
            <Area
              type="monotone"
              dataKey="count"
              stroke="hsl(var(--primary))"
              fillOpacity={1}
              fill="url(#colorCount)"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}