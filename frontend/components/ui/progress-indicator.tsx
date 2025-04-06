import React from "react";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface ProgressIndicatorProps {
  progress: number;
  message?: string;
  className?: string;
  showPercentage?: boolean;
  stages?: string[];
}

export function ProgressIndicator({
  progress,
  message,
  className,
  showPercentage = true,
  stages
}: ProgressIndicatorProps) {
  // 计算当前阶段
  const currentStage = stages ? Math.floor((progress / 100) * stages.length) : null;
  
  return (
    <div className={cn("w-full space-y-2", className)}>
      <div className="flex justify-between items-center">
        {message && (
          <p className="text-sm font-medium">{message}</p>
        )}
        {showPercentage && (
          <span className="text-sm text-muted-foreground">{Math.round(progress)}%</span>
        )}
      </div>
      
      <Progress value={progress} className="w-full" />
      
      {stages && stages.length > 0 && (
        <div className="mt-4 space-y-1">
          <p className="text-sm font-medium">当前阶段:</p>
          <ul className="space-y-1">
            {stages.map((stage, index) => (
              <li 
                key={index} 
                className={cn(
                  "text-sm px-3 py-1 rounded-md",
                  index === currentStage 
                    ? "bg-primary/10 text-primary font-medium" 
                    : index < currentStage 
                      ? "text-muted-foreground line-through" 
                      : "text-muted-foreground"
                )}
              >
                {stage}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
} 