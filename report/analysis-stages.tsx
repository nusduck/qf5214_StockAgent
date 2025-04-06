import React from "react";
import { CheckCircle2, Circle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

export type AnalysisStage = {
  name: string;
  description?: string;
};

interface AnalysisStagesProps {
  stages: AnalysisStage[];
  currentStage: number;
  className?: string;
}

export function AnalysisStages({
  stages,
  currentStage,
  className
}: AnalysisStagesProps) {
  return (
    <div className={cn("space-y-4", className)}>
      <h3 className="text-lg font-medium">分析进度</h3>
      <ul className="space-y-4">
        {stages.map((stage, index) => {
          // 计算阶段状态: 完成、进行中、等待
          const isCompleted = index < currentStage;
          const isCurrent = index === currentStage;
          const isPending = index > currentStage;
          
          return (
            <li 
              key={index} 
              className={cn(
                "flex items-start gap-3 p-3 rounded-md",
                isCurrent && "bg-primary/10",
                isCompleted && "text-muted-foreground"
              )}
            >
              {isCompleted ? (
                <CheckCircle2 className="h-5 w-5 text-primary shrink-0 mt-0.5" />
              ) : isCurrent ? (
                <Clock className="h-5 w-5 text-primary animate-pulse shrink-0 mt-0.5" />
              ) : (
                <Circle className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
              )}
              <div>
                <p className={cn(
                  "text-sm font-medium",
                  isCurrent && "text-primary"
                )}>
                  {stage.name}
                </p>
                {stage.description && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {stage.description}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
} 