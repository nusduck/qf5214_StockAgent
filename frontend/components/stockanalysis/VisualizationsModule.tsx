'use client';

import React from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw, AlertCircle } from "lucide-react";
import { ImageGallery } from "@/components/ui/image-view";

interface VisualizationsModuleProps {
  moduleData: {
    data: any;
    loading: boolean;
    loaded: boolean;
    error?: string;
  };
  onRetry: (moduleType: string) => void;
}

const VisualizationsModule: React.FC<VisualizationsModuleProps> = ({ moduleData, onRetry }) => {
  const { data, loading, loaded, error } = moduleData;

  // 渲染加载中状态
  if (loading) {
    return (
      <div className="space-y-3 mt-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  // 渲染错误状态
  if (error) {
    return (
      <Alert variant="destructive" className="mt-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>加载错误</AlertTitle>
        <AlertDescription className="flex justify-between items-center">
          <span>{error}</span>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => onRetry('visualizations')}
            className="ml-2"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            重试
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  // 渲染未加载状态
  if (!loaded) {
    return (
      <div className="p-8 text-center">
        <Button 
          variant="outline" 
          onClick={() => onRetry('visualizations')}
        >
          加载数据
        </Button>
      </div>
    );
  }

  return (
    <div>
      {data && data.length > 0 ? (
        <ImageGallery 
          images={data} 
          thumbnailSize={300}
        />
      ) : (
        <p className="text-muted-foreground">暂无图表数据</p>
      )}
    </div>
  );
};

export default VisualizationsModule; 