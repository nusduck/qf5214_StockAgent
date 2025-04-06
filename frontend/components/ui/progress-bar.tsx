import React from "react";
import { cn } from "@/lib/utils";

interface ProgressBarProps {
  progress: number;
  className?: string;
  showPercentage?: boolean;
  message?: string;
}

export function ProgressBar({
  progress,
  className,
  showPercentage = true,
  message
}: ProgressBarProps) {
  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between items-center">
        {message && (
          <p className="text-sm font-medium">{message}</p>
        )}
        {showPercentage && (
          <span className="text-sm text-muted-foreground">{Math.round(progress)}%</span>
        )}
      </div>
      
      <div className={cn("w-full bg-secondary h-2 rounded-full overflow-hidden", className)}>
        <div 
          className="bg-primary h-full rounded-full transition-all duration-300 ease-in-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
} 