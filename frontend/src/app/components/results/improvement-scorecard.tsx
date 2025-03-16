"use client"

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer } from "@/components/ui/chart";
import { CheckCircleIcon, AlertCircleIcon, BarChartIcon } from "lucide-react";

export function ImprovementScorecard() {
  // Mock data for improvement metrics
  const improvementMetrics = [
    { name: "Clarity", score: 85 },
    { name: "Relevance", score: 90 },
    { name: "Specificity", score: 75 },
    { name: "Keywords", score: 95 },
  ];

  const pieData = [
    { name: "Excellent", value: 3 },
    { name: "Good", value: 1 },
    { name: "Needs Improvement", value: 0 },
  ];

  const COLORS = [
    "hsl(var(--chart-1))",
    "hsl(var(--chart-2))",
    "hsl(var(--chart-3))",
  ];

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-medium">
          Content Improvement
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div
            className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 flex flex-col items-center justify-center"
          >
            <div
              className="text-green-600 dark:text-green-400 mb-1"
            >
              <CheckCircleIcon className="h-8 w-8" />
            </div>
            <span
              className="text-2xl font-bold text-green-700 dark:text-green-400"
            >
              86%
            </span>
            <span
              className="text-xs text-green-600 dark:text-green-500"
            >
              ATS Score
            </span>
          </div>
          <div
            className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 flex flex-col items-center justify-center"
          >
            <div className="text-blue-600 dark:text-blue-400 mb-1">
              <BarChartIcon className="h-8 w-8" />
            </div>
            <span
              className="text-2xl font-bold text-blue-700 dark:text-blue-400"
            >
              +35%
            </span>
            <span
              className="text-xs text-blue-600 dark:text-blue-500"
            >
              Improvement
            </span>
          </div>
        </div>

        <div>
          <h4
            className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3"
          >
            Content Quality
          </h4>
          <div className="flex justify-center">
            {/* Simplified pie chart placeholder */}
            <div className="h-[150px] w-[150px] flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 relative">
              <div className="absolute inset-4 rounded-full bg-white dark:bg-gray-900"></div>
              <span className="text-lg font-bold">75%</span>
            </div>
          </div>
          <div className="flex justify-center space-x-4 text-xs mt-4">
            {pieData.map((entry, index) => (
              <div
                key={index}
                className="flex items-center"
              >
                <span
                  className="inline-block w-3 h-3 rounded-full mr-1"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                ></span>
                <span>
                  {entry.name}: {entry.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h4
            className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3"
          >
            Improvement Metrics
          </h4>
          <div className="space-y-3">
            {improvementMetrics.map((metric, index) => (
              <div
                key={metric.name}
                className="flex items-center"
              >
                <div
                  className="w-24 text-sm text-gray-600 dark:text-gray-400"
                >
                  {metric.name}
                </div>
                <div
                  className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
                >
                  <div
                    className="h-full bg-blue-500 dark:bg-blue-600 rounded-full"
                    style={{ width: `${metric.score}%` }}
                  ></div>
                </div>
                <div
                  className="w-8 text-right text-sm font-medium ml-2"
                >
                  {metric.score}%
                </div>
              </div>
            ))}
          </div>
        </div>

        <div
          className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 flex items-start"
        >
          <AlertCircleIcon
            className="h-5 w-5 text-amber-500 dark:text-amber-400 mt-0.5 mr-3 flex-shrink-0"
          />

          <div>
            <h4
              className="text-sm font-medium text-amber-800 dark:text-amber-300"
            >
              Recommendation
            </h4>
            <p
              className="text-xs text-amber-700 dark:text-amber-400 mt-1"
            >
              Add more quantifiable achievements to your work experience section
              to further improve your resume's impact.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}