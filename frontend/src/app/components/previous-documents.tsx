"use client"

import React from "react";
import { FileIcon, ClockIcon } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface PreviousDocumentsProps {
  documentType: "resume" | "job";
  onSelect: (file: File) => void;
}

export function PreviousDocuments({
  documentType,
  onSelect,
}: PreviousDocumentsProps) {
  // Mock data for previous documents
  const previousDocuments = [
    {
      id: 1,
      name:
        documentType === "resume"
          ? "Software_Engineer_Resume.pdf"
          : "Frontend_Developer_JD.pdf",
      date: "2023-11-15T14:30:00",
      size: 245, // KB
    },
    {
      id: 2,
      name:
        documentType === "resume"
          ? "Product_Manager_Resume.docx"
          : "UX_Designer_JD.pdf",
      date: "2023-10-22T09:15:00",
      size: 183, // KB
    },
    {
      id: 3,
      name:
        documentType === "resume"
          ? "Data_Analyst_Resume.pdf"
          : "Data_Scientist_JD.pdf",
      date: "2023-09-05T16:45:00",
      size: 210, // KB
    },
    {
      id: 4,
      name:
        documentType === "resume"
          ? "Marketing_Resume.pdf"
          : "Marketing_Manager_JD.pdf",
      date: "2023-08-17T11:20:00",
      size: 198, // KB
    },
  ];

  const handleSelectDocument = (document: (typeof previousDocuments)[0]) => {
    // In a real application, you would fetch the actual file
    // For this demo, we'll create a mock file
    const mockFile = new File([""], document.name, {
      type: document.name.endsWith(".pdf")
        ? "application/pdf"
        : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });

    onSelect(mockFile);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(date);
  };

  return (
    <div className="space-y-4">
      {previousDocuments.length === 0 ? (
        <div className="text-center py-8">
          <ClockIcon
            className="h-10 w-10 text-gray-400 mx-auto mb-3"
          />
          <p className="text-gray-500 dark:text-gray-400">
            No previous{" "}
            {documentType === "resume" ? "resumes" : "job descriptions"} found
          </p>
        </div>
      ) : (
        <ScrollArea
          className="h-[250px] rounded-md border border-gray-200 dark:border-gray-800"
        >
          <div className="p-4 space-y-3">
            {previousDocuments.map((doc, index) => (
              <div
                key={doc.id}
                className="flex items-center p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                onClick={() => handleSelectDocument(doc)}
              >
                <FileIcon
                  className="h-6 w-6 text-blue-500 mr-3 flex-shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <p
                    className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate"
                  >
                    {doc.name}
                  </p>
                  <div
                    className="flex items-center text-xs text-gray-500 dark:text-gray-400"
                  >
                    <span>{formatDate(doc.date)}</span>
                    <span className="mx-2">
                      •
                    </span>
                    <span>{doc.size} KB</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      )}
    </div>
  );
}