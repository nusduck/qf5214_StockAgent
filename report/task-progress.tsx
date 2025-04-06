import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ProgressBar } from "@/components/ui/progress-bar";
import { ErrorAlert } from "@/components/ui/error-alert";
import { AnalysisStages } from "@/components/report/analysis-stages";
import { ANALYSIS_STAGES, getCurrentStage, TaskStatusInfo, ExtendedTaskStatusInfo } from "@/lib/types";
import { PollingIndicator } from "@/components/ui/polling-indicator";
import { PartialResult } from "@/components/report/partial-result";
import { AnalysisAnimation } from "@/components/report/analysis-animation";

interface TaskProgressProps {
  status: ExtendedTaskStatusInfo;
  companyName: string;
  onRetry?: () => void;
  className?: string;
  pollingAttempts?: number;
  pollingInterval?: number;
}

export function TaskProgress({
  status,
  companyName,
  onRetry,
  className,
  pollingAttempts,
  pollingInterval
}: TaskProgressProps) {
  // 计算当前阶段
  const currentStage = getCurrentStage(status.progress);
  const hasPartialResult = !!status.partial_result;
  
  return (
    <Card className={className}>
      <CardContent className="pt-6">
        <div className="space-y-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-semibold">{companyName} 分析进度</h2>
              <p className="text-sm text-muted-foreground mt-1">
                任务ID: {status.id}
              </p>
            </div>
            {status.status === "RUNNING" && (
              <LoadingSpinner size={20} text="" />
            )}
          </div>
          
          {status.status === "FAILED" ? (
            <ErrorAlert 
              title="分析任务失败"
              message={status.message || "无法完成分析任务，请稍后重试"}
              onRetry={onRetry}
            />
          ) : (
            <>
              <ProgressBar 
                progress={status.progress} 
                message={status.message}
              />
              
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <p className="text-sm">
                    <span className="font-medium">任务状态:</span> {" "}
                    {status.status === "PENDING" && "等待执行"}
                    {status.status === "RUNNING" && "正在执行"}
                    {status.status === "COMPLETED" && "已完成"}
                  </p>
                  <p className="text-sm">
                    <span className="font-medium">开始时间:</span> {" "}
                    {new Date(status.created_at).toLocaleString()}
                  </p>
                  <p className="text-sm">
                    <span className="font-medium">最近更新:</span> {" "}
                    {new Date(status.updated_at).toLocaleString()}
                  </p>
                </div>
                
                <AnalysisStages 
                  stages={ANALYSIS_STAGES}
                  currentStage={currentStage}
                />
              </div>
              
              {status.status === "RUNNING" && (
                <p className="text-sm text-muted-foreground italic">
                  完整分析可能需要1-2分钟，请耐心等待...
                </p>
              )}
              
              {status.status === "RUNNING" && pollingAttempts !== undefined && (
                <PollingIndicator 
                  attempts={pollingAttempts} 
                  interval={pollingInterval || 5000}
                  className="mt-2"
                />
              )}
              
              {status.status === "RUNNING" && hasPartialResult && (
                <PartialResult result={status.partial_result!} />
              )}
              
              {status.status === "RUNNING" && (
                <div className="flex justify-center my-6">
                  <AnalysisAnimation progress={status.progress} />
                </div>
              )}
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
} 