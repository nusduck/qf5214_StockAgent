import React from "react";
import { AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface ErrorAlertProps {
  title?: string;
  message: string;
  className?: string;
  onRetry?: () => void;
}

export function ErrorAlert({
  title = "发生错误",
  message,
  className,
  onRetry
}: ErrorAlertProps) {
  return (
    <div className={cn(
      "bg-destructive/10 border border-destructive/20 rounded-md p-4",
      className
    )}>
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
        <div className="space-y-2">
          <h3 className="font-medium text-destructive">{title}</h3>
          <p className="text-sm text-muted-foreground">{message}</p>
          {onRetry && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onRetry}
              className="mt-2"
            >
              重试
            </Button>
          )}
        </div>
      </div>
    </div>
  );
} 