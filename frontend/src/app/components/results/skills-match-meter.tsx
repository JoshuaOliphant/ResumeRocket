"use client"

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { ChartContainer } from "@/components/ui/chart";

export function SkillsMatchMeter() {
  // Mock data for skills match
  const skillsData = [
    { name: "React.js", original: 65, optimized: 95 },
    { name: "Node.js", original: 70, optimized: 90 },
    { name: "AWS", original: 30, optimized: 85 },
    { name: "CI/CD", original: 20, optimized: 80 },
    { name: "TypeScript", original: 50, optimized: 75 },
  ];

  const overallMatch = {
    original: 45,
    optimized: 85,
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle
          className="text-lg font-medium flex items-center justify-between"
        >
          Skills Match
          <Badge
            variant="outline"
            className="ml-2 bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800"
          >
            +40% Improvement
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500 dark:text-gray-400">
              Overall Match
            </span>
            <span className="font-medium">
              {overallMatch.optimized}%
            </span>
          </div>
          <Progress
            value={overallMatch.optimized}
            className="h-2"
          />

          <div
            className="flex items-center text-xs text-gray-500 dark:text-gray-400"
          >
            <div className="flex items-center">
              <span
                className="inline-block w-3 h-3 bg-gray-300 dark:bg-gray-600 rounded-full mr-1"
              ></span>
              Original: {overallMatch.original}%
            </div>
            <div className="flex items-center ml-4">
              <span
                className="inline-block w-3 h-3 bg-blue-500 dark:bg-blue-600 rounded-full mr-1"
              ></span>
              Optimized: {overallMatch.optimized}%
            </div>
          </div>
        </div>

        <div>
          <h4
            className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3"
          >
            Key Skills Improvement
          </h4>
          <div className="space-y-3">
            {skillsData.map((skill) => (
              <div key={skill.name} className="flex items-center text-sm">
                <div className="w-24 text-gray-600 dark:text-gray-400">
                  {skill.name}
                </div>
                <div className="flex-1 relative h-4 bg-gray-100 dark:bg-gray-800 rounded">
                  <div
                    className="absolute h-full bg-gray-300 dark:bg-gray-600 rounded"
                    style={{ width: `${skill.original}%` }}
                  ></div>
                  <div
                    className="absolute h-full bg-blue-500 dark:bg-blue-600 rounded"
                    style={{ width: `${skill.optimized}%` }}
                  ></div>
                </div>
                <div className="w-16 text-right ml-2">
                  <span className="text-gray-400">
                    {skill.original}%
                  </span>
                  <span className="text-blue-500 dark:text-blue-400 ml-1">
                    ▶ {skill.optimized}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-2">
          <h4
            className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3"
          >
            Job Requirements Match
          </h4>
          <div className="space-y-3">
            {skillsData.map((skill) => (
              <div
                key={skill.name}
                className="space-y-1"
              >
                <div
                  className="flex justify-between text-sm"
                >
                  <span
                    className="text-gray-700 dark:text-gray-300"
                  >
                    {skill.name}
                  </span>
                  <span className="font-medium">
                    {skill.optimized}%
                  </span>
                </div>
                <Progress
                  value={skill.optimized}
                  className="h-1.5"
                />
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}