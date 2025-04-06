import React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingIndicatorProps {
  size?: number;
  className?: string;
  text?: string;
}

export function LoadingIndicator({
  size = 24,
  className,
  text = "加载中..."
}: LoadingIndicatorProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center", className)}>
      <Loader2 
        className="animate-spin text-primary" 
        size={size} 
      />
      {text && (
        <p className="mt-2 text-sm text-muted-foreground">{text}</p>
      )}
    </div>
  );
} 