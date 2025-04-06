import React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface PollingIndicatorProps {
  attempts: number;
  interval: number;
  className?: string;
}

export function PollingIndicator({
  attempts,
  interval,
  className
}: PollingIndicatorProps) {
  return (
    <div className={cn("flex items-center gap-2 text-xs text-muted-foreground", className)}>
      <Loader2 className="h-3 w-3 animate-spin" />
      <span>
        正在等待服务器响应 (第{attempts}次查询，间隔{Math.round(interval/1000)}秒)
      </span>
    </div>
  );
} 