"use client"

import React from "react";
import { SuggestionToggle } from "./suggestion-toggle";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

interface ComparisonPanelProps {
  acceptedSuggestions: string[];
  onAcceptSuggestion: (id: string) => void;
}

export function ComparisonPanel({
  acceptedSuggestions,
  onAcceptSuggestion,
}: ComparisonPanelProps) {
  // Mock data for comparison sections
  const comparisonSections = [
    {
      id: "summary",
      title: "Professional Summary",
      original:
        "Software engineer with experience in web development using React and Node.js.",
      optimized:
        "Dedicated software engineer with 5+ years of experience in full-stack development, specializing in React, Node.js, and cloud infrastructure. Proven track record of delivering scalable solutions that drive business growth and enhance user experience.",
      changes: [
        {
          id: "summary-1",
          text: "Added years of experience and specialization",
          highlight:
            "full-stack development, specializing in React, Node.js, and cloud infrastructure",
        },
      ],
    },
    {
      id: "experience",
      title: "Work Experience",
      original:
        "Developed web applications at TechCorp Inc. Worked on backend services and frontend components.",
      optimized:
        "Led development of microservices architecture that improved system reliability by 35%. Implemented CI/CD pipelines reducing deployment time by 40%. Mentored junior developers and conducted code reviews to ensure quality standards.",
      changes: [
        {
          id: "experience-1",
          text: "Added quantifiable achievements",
          highlight: "improved system reliability by 35%",
        },
        {
          id: "experience-2",
          text: "Added leadership experience",
          highlight: "Mentored junior developers and conducted code reviews",
        },
      ],
    },
    {
      id: "skills",
      title: "Skills",
      original: "JavaScript, React, Node.js, HTML, CSS",
      optimized:
        "React.js & Redux, Node.js & Express, AWS (Lambda, EC2, S3), Docker & Kubernetes, CI/CD (Jenkins, GitHub Actions), TypeScript",
      changes: [
        {
          id: "skills-1",
          text: "Added cloud technologies",
          highlight: "AWS (Lambda, EC2, S3)",
        },
        {
          id: "skills-2",
          text: "Added containerization skills",
          highlight: "Docker & Kubernetes",
        },
        {
          id: "skills-3",
          text: "Added CI/CD experience",
          highlight: "CI/CD (Jenkins, GitHub Actions)",
        },
      ],
    },
  ];

  const highlightText = (text: string, highlight: string) => {
    if (!highlight) return text;

    const parts = text.split(new RegExp(`(${highlight})`, "gi"));
    return (
      <>
        {parts.map((part, i) =>
          part.toLowerCase() === highlight.toLowerCase() ? (
            <span
              key={i}
              className="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 px-1 rounded"
            >
              {part}
            </span>
          ) : (
            part
          ),
        )}
      </>
    );
  };

  return (
    <div className="space-y-6">
      {comparisonSections.map((section) => (
        <Card
          key={section.id}
          className="overflow-hidden"
        >
          <div
            className="bg-gray-50 dark:bg-gray-800/50 px-6 py-4 border-b border-gray-200 dark:border-gray-700"
          >
            <h3
              className="text-lg font-medium text-gray-900 dark:text-white"
            >
              {section.title}
            </h3>
          </div>
          <CardContent className="p-0">
            <div
              className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-200 dark:divide-gray-700"
            >
              <div className="p-6">
                <h4
                  className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3"
                >
                  Original
                </h4>
                <p
                  className="text-gray-700 dark:text-gray-300"
                >
                  {section.original}
                </p>
              </div>
              <div
                className="p-6 bg-gray-50/50 dark:bg-gray-800/20"
              >
                <h4
                  className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3"
                >
                  Optimized
                </h4>
                <p
                  className="text-gray-700 dark:text-gray-300"
                >
                  {acceptedSuggestions.some((id) => id.startsWith(section.id))
                    ? (() => {
                        let result = section.optimized;
                        const acceptedChanges = section.changes.filter(change => 
                          acceptedSuggestions.includes(change.id)
                        );
                        return acceptedChanges.length > 0
                          ? highlightText(result, acceptedChanges.map(c => c.highlight).join("|"))
                          : result;
                      })()
                    : section.original}
                </p>
              </div>
            </div>

            <Separator />

            <div
              className="p-4 bg-gray-50 dark:bg-gray-800/50"
            >
              <h4
                className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3"
              >
                Suggested Changes
              </h4>
              <div className="space-y-3">
                {section.changes.map((change) => (
                  <SuggestionToggle
                    key={change.id}
                    id={change.id}
                    text={change.text}
                    isAccepted={acceptedSuggestions.includes(change.id)}
                    onToggle={() => onAcceptSuggestion(change.id)}
                  />
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}