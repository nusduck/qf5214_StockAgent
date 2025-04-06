"use client";

import React from "react";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    // 记录客户端错误
    console.error("页面错误:", error);
  }, [error]);

  return (
    <div className="container mx-auto py-12 px-4 flex justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="bg-destructive/10 text-destructive">
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            <span>发生错误</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="py-6">
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              分析报告页面加载时遇到问题。错误信息：
            </p>
            <div className="bg-muted p-3 rounded-md text-xs overflow-auto max-h-[150px]">
              <code>{error.message || "未知错误"}</code>
            </div>
            {error.digest && (
              <p className="text-xs text-muted-foreground">
                错误ID: {error.digest}
              </p>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex gap-3">
          <Button 
            variant="outline" 
            className="flex-1"
            onClick={() => window.location.href = "/"}
          >
            返回首页
          </Button>
          <Button 
            className="flex-1"
            onClick={reset}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            重试
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
} 