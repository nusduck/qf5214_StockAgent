import React from "react";
import { AlertCircle } from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ErrorMessageProps {
  title?: string;
  message: string;
  className?: string;
  onRetry?: () => void;
}

export function ErrorMessage({
  title = "发生错误",
  message,
  className,
  onRetry
}: ErrorMessageProps) {
  return (
    <Alert variant="destructive" className={cn("", className)}>
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription className="mt-2">
        <p>{message}</p>
        {onRetry && (
          <Button 
            variant="outline" 
            className="mt-4" 
            onClick={onRetry}
          >
            重试
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
} 