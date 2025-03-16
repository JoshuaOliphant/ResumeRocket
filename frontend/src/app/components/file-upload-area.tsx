"use client"

import React, { useState, useRef, useCallback } from "react";
import { FileIcon, UploadIcon, XIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface FileUploadAreaProps {
  onFileUpload: (file: File | null) => void;
  onTextInput?: (text: string) => void;
  acceptedFileTypes: string;
  fileType: 'resume' | 'job';
  allowTextInput?: boolean;
  currentFile: File | null;
  textValue?: string;
}

export function FileUploadArea({
  onFileUpload,
  onTextInput,
  acceptedFileTypes,
  fileType,
  allowTextInput = false,
  currentFile,
  textValue = '',
}: FileUploadAreaProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      handleFile(droppedFile);
    }
  }, []);

  const handleFile = (selectedFile: File) => {
    // Check if file type is accepted
    const fileExtension = `.${selectedFile.name.split(".").pop()?.toLowerCase()}`;
    const isAccepted = acceptedFileTypes
      .split(",")
      .some((type) => type.trim() === fileExtension || type.trim() === "*");

    if (!isAccepted) {
      alert(
        `Please upload a file with one of these formats: ${acceptedFileTypes}`,
      );
      return;
    }

    onFileUpload(selectedFile);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleRemoveFile = () => {
    onFileUpload(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (onTextInput) {
      onTextInput(e.target.value);
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="space-y-4">
      {allowTextInput ? (
        <textarea
          className="w-full h-32 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder={`Paste your ${fileType} text here...`}
          value={textValue}
          onChange={handleTextChange}
        />
      ) : (
        <div
          className={`border-2 border-dashed rounded-lg p-6 text-center ${
            isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'
          }`}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {currentFile ? (
            <div className="space-y-2">
              <p className="text-sm text-gray-500">{currentFile.name}</p>
              <button
                onClick={handleRemoveFile}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                Remove
              </button>
            </div>
          ) : (
            <>
              <p className="text-gray-500">
                Drag and drop your {fileType} file here, or{' '}
                <label className="text-indigo-600 hover:text-indigo-500 cursor-pointer">
                  browse
                  <input
                    type="file"
                    className="hidden"
                    accept={acceptedFileTypes}
                    onChange={handleFileInputChange}
                  />
                </label>
              </p>
              <p className="text-sm text-gray-400 mt-1">
                Supported formats: {acceptedFileTypes.replace(/\./g, '').toUpperCase()}
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}