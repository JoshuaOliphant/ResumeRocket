"use client"

import React from "react";
import { Switch } from "@/components/ui/switch";
import { CheckIcon, XIcon } from "lucide-react";

interface SuggestionToggleProps {
  id: string;
  text: string;
  isAccepted: boolean;
  onToggle: () => void;
}

export function SuggestionToggle({
  id,
  text,
  isAccepted,
  onToggle,
}: SuggestionToggleProps) {
  return (
    <div
      className={`flex items-center justify-between p-3 rounded-md ${
        isAccepted
          ? "bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800/50"
          : "bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700"
      }`}
    >
      <div className="flex items-center">
        {isAccepted ? (
          <CheckIcon
            className="h-4 w-4 text-green-600 dark:text-green-400 mr-2 flex-shrink-0"
          />
        ) : (
          <XIcon
            className="h-4 w-4 text-gray-400 dark:text-gray-500 mr-2 flex-shrink-0"
          />
        )}

        <span
          className={`text-sm ${
            isAccepted
              ? "text-green-800 dark:text-green-300"
              : "text-gray-700 dark:text-gray-300"
          }`}
        >
          {text}
        </span>
      </div>
      <Switch
        checked={isAccepted}
        onCheckedChange={onToggle}
        className={isAccepted ? "data-[state=checked]:bg-green-600" : ""}
      />
    </div>
  );
}