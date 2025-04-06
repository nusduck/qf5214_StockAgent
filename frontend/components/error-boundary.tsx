"use client";

import React, { ErrorInfo, Component, ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({
      error,
      errorInfo
    });
    
    // 可以在这里添加错误日志记录
    console.error("Error caught by boundary:", error, errorInfo);
  }

  resetError = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // 使用自定义回退UI或默认错误UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Card className="w-full max-w-md mx-auto my-8">
          <CardHeader className="bg-destructive/10 text-destructive">
            <CardTitle className="flex items-center gap-2">
              <ExclamationTriangleIcon className="h-5 w-5" />
              <span>发生错误</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="py-4">
            <div className="space-y-4">
              <p className="text-sm">
                应用程序遇到了问题。错误信息：
              </p>
              <div className="bg-muted p-3 rounded-md text-xs overflow-auto max-h-[200px]">
                {this.state.error?.message || "未知错误"}
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              className="w-full" 
              onClick={() => {
                this.resetError();
                window.location.reload();
              }}
            >
              刷新页面
            </Button>
          </CardFooter>
        </Card>
      );
    }

    return this.props.children;
  }
} 