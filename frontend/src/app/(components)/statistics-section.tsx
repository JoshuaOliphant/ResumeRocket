"use client"

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChartContainer } from "@/components/ui/chart";
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Line, LineChart, Bar, BarChart, CartesianGrid, XAxis } from "recharts";
import { ArrowUpIcon, TrendingUpIcon } from "lucide-react";

export function StatisticsSection() {
  const matchScoreData = [
    { date: "Jan", score: 65 },
    { date: "Feb", score: 68 },
    { date: "Mar", score: 72 },
    { date: "Apr", score: 75 },
    { date: "May", score: 78 },
    { date: "Jun", score: 82 },
    { date: "Jul", score: 85 },
    { date: "Aug", score: 88 },
  ];

  const optimizationsData = [
    { month: "Jan", count: 2 },
    { month: "Feb", count: 3 },
    { month: "Mar", count: 5 },
    { month: "Apr", count: 4 },
    { month: "May", count: 7 },
    { month: "Jun", count: 9 },
    { month: "Jul", count: 8 },
    { month: "Aug", count: 12 },
  ];

  const keywordData = [
    { month: "Jan", relevance: 45 },
    { month: "Feb", relevance: 52 },
    { month: "Mar", relevance: 58 },
    { month: "Apr", relevance: 63 },
    { month: "May", relevance: 70 },
    { month: "Jun", relevance: 75 },
    { month: "Jul", relevance: 82 },
    { month: "Aug", relevance: 88 },
  ];

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Resume Performance</CardTitle>
            <CardDescription>
              Track your improvement over time
            </CardDescription>
          </div>
          <div
            className="flex items-center space-x-1 rounded-md bg-green-100 dark:bg-green-900/30 px-2 py-1 text-xs font-medium text-green-600 dark:text-green-400"
          >
            <ArrowUpIcon className="h-3 w-3" />
            <span>23%</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="match-score">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="match-score">
              Match Score
            </TabsTrigger>
            <TabsTrigger value="optimizations">
              Optimizations
            </TabsTrigger>
            <TabsTrigger value="keywords">
              Keywords
            </TabsTrigger>
          </TabsList>

          <TabsContent value="match-score" className="space-y-4">
            <div className="pt-4">
              <ChartContainer
                config={{}}
                className="aspect-[none] h-[250px]"
              >
                <LineChart data={matchScoreData}>
                  <ChartTooltip
                    content={<ChartTooltipContent />}
                  />
                  <CartesianGrid
                    vertical={false}
                    strokeDasharray="3 3"
                  />
                  <XAxis
                    dataKey="date"
                    axisLine={false}
                    tickLine={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="hsl(var(--chart-1))"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ChartContainer>
            </div>
            <div
              className="flex items-center justify-between text-sm"
            >
              <div className="text-muted-foreground">
                Starting: 65%
              </div>
              <div className="font-medium">
                Current: 88%
              </div>
            </div>
          </TabsContent>

          <TabsContent value="optimizations">
            <div className="pt-4">
              <ChartContainer
                config={{}}
                className="aspect-[none] h-[250px]"
              >
                <BarChart data={optimizationsData}>
                  <ChartTooltip
                    content={<ChartTooltipContent />}
                  />
                  <CartesianGrid
                    vertical={false}
                    strokeDasharray="3 3"
                  />
                  <XAxis
                    dataKey="month"
                    axisLine={false}
                    tickLine={false}
                  />
                  <Bar
                    dataKey="count"
                    fill="hsl(var(--chart-2))"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ChartContainer>
            </div>
            <div
              className="flex items-center justify-between text-sm"
            >
              <div className="text-muted-foreground">
                Total: 50 optimizations
              </div>
              <div className="font-medium">
                Monthly avg: 6.3
              </div>
            </div>
          </TabsContent>

          <TabsContent value="keywords">
            <div className="pt-4">
              <ChartContainer
                config={{}}
                className="aspect-[none] h-[250px]"
              >
                <LineChart data={keywordData}>
                  <ChartTooltip
                    content={<ChartTooltipContent />}
                  />
                  <CartesianGrid
                    vertical={false}
                    strokeDasharray="3 3"
                  />
                  <XAxis
                    dataKey="month"
                    axisLine={false}
                    tickLine={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="relevance"
                    stroke="hsl(var(--chart-3))"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ChartContainer>
            </div>
            <div
              className="flex items-center justify-between text-sm"
            >
              <div className="text-muted-foreground">
                Keyword relevance
              </div>
              <div className="font-medium">
                Improved by 43%
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
