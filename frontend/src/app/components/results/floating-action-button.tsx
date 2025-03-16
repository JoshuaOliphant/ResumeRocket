"use client"

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { DownloadIcon, FileTextIcon, FileIcon, XIcon } from "lucide-react";

export function FloatingActionButton() {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleDownload = (format: string) => {
    // In a real app, this would trigger the download in the specified format
    console.log(`Downloading in ${format} format`);
    setIsExpanded(false);
  };

  return (
    <div className="fixed bottom-8 right-8 z-50">
      {isExpanded && (
        <div
          className="absolute bottom-16 right-0 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 mb-4 w-48 border border-gray-200 dark:border-gray-700"
        >
          <div className="space-y-2">
            <Button
              variant="ghost"
              className="w-full justify-start text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={() => handleDownload("pdf")}
            >
              <FileTextIcon className="mr-2 h-4 w-4 text-red-500" />
              Download as PDF
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={() => handleDownload("docx")}
            >
              <FileTextIcon
                className="mr-2 h-4 w-4 text-blue-500"
              />
              Download as DOCX
            </Button>
            <Button
              variant="ghost"
              className="w-full justify-start text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={() => handleDownload("txt")}
            >
              <FileIcon className="mr-2 h-4 w-4 text-gray-500" />
              Download as TXT
            </Button>
          </div>
        </div>
      )}

      <Button
        size="lg"
        className={`rounded-full shadow-lg ${isExpanded ? "bg-gray-700 hover:bg-gray-800 dark:bg-gray-600 dark:hover:bg-gray-700" : "bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800"}`}
        onClick={toggleExpand}
      >
        {isExpanded ? (
          <XIcon className="h-5 w-5" />
        ) : (
          <>
            <DownloadIcon className="mr-2 h-5 w-5" />
            Download
          </>
        )}
      </Button>
    </div>
  );
}