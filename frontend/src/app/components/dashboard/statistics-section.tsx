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
import { ArrowUpIcon } from "lucide-react";

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

  // Helper function to render a simplified chart placeholder
  const renderChartPlaceholder = (data: any[], color: string, type: 'line' | 'bar') => {
    const maxValue = Math.max(...data.map(item => Object.values(item)[1] as number));
    
    return (
      <div className="h-[250px] flex items-end justify-between px-2 pt-4">
        {data.map((item, index) => {
          const value = Object.values(item)[1] as number;
          const height = `${(value / maxValue) * 80}%`;
          
          return type === 'line' ? (
            <div key={index} className="flex flex-col items-center relative">
              <div className="absolute bottom-0 w-full h-[1px] bg-gray-200"></div>
              <div className={`w-2 h-2 rounded-full ${color} z-10`}></div>
              {index > 0 && (
                <div 
                  className={`absolute bottom-1 left-0 h-[1px] w-full -translate-x-1/2 transform ${color}`} 
                  style={{ transform: 'rotate(-30deg) translateY(8px)' }}
                ></div>
              )}
              <div className="text-xs mt-2 text-gray-500">{Object.values(item)[0]}</div>
            </div>
          ) : (
            <div key={index} className="flex flex-col items-center">
              <div 
                className={`w-8 ${color} rounded-t`} 
                style={{ height }}
              ></div>
              <div className="text-xs mt-2 text-gray-500">{Object.values(item)[0]}</div>
            </div>
          );
        })}
      </div>
    );
  };

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
              {renderChartPlaceholder(matchScoreData, 'bg-blue-500', 'line')}
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

          <TabsContent value="optimizations" className="space-y-4">
            <div className="pt-4">
              {renderChartPlaceholder(optimizationsData, 'bg-purple-500', 'bar')}
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

          <TabsContent value="keywords" className="space-y-4">
            <div className="pt-4">
              {renderChartPlaceholder(keywordData, 'bg-amber-500', 'line')}
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