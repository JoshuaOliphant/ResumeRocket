"use client"

import React from "react";
import { HelpCircleIcon } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface CompatibleFormatsProps {
  fileType: "resume" | "job";
}

export function CompatibleFormats({ fileType }: CompatibleFormatsProps) {
  const formats =
    fileType === "resume"
      ? [
          { name: "PDF", extension: ".pdf", size: "5MB" },
          { name: "Word", extension: ".docx, .doc", size: "10MB" },
        ]
      : [
          { name: "PDF", extension: ".pdf", size: "5MB" },
          { name: "Word", extension: ".docx, .doc", size: "10MB" },
          { name: "Text", extension: ".txt", size: "2MB" },
        ];

  return (
    <div
      className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700"
    >
      <div className="flex items-center mb-2">
        <p
          className="text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Compatible Formats
        </p>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                className="ml-1 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
              >
                <HelpCircleIcon className="h-4 w-4" />
              </button>
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-xs max-w-xs">
                {fileType === "resume"
                  ? "We support these file formats for resume uploads. For best results, use PDF format."
                  : "We support these file formats for job descriptions. You can also paste text directly."}
              </p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
      <div className="flex flex-wrap gap-2">
        {formats.map((format, index) => (
          <div
            key={index}
            className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
          >
            {format.name}
            <span
              className="text-gray-500 dark:text-gray-400 ml-1"
            >
              ({format.extension})
            </span>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        Maximum file size: 10MB
      </p>
    </div>
  );
}