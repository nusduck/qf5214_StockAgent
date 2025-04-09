'use client';

import React, { useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw, AlertCircle, Maximize2, ZoomIn } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog";

// 添加API基础URL常量
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

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

  // 辅助函数：修正图片URL确保使用正确的域名
  const getCorrectImageUrl = (path: string): string => {
    if (!path) return '';
    // 如果是完整URL，直接返回
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }
    // 如果路径以/static/开头，转换为完整URL
    if (path.startsWith('/static/')) {
      return `${API_BASE_URL}${path}`;
    }
    return path;
  };

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

  // 提取图像数据和描述信息
  let images: string[] = [];
  let descriptions: string[] = [];

  // 处理两种可能的数据结构
  if (data) {
    // 情况1: 直接返回图片路径数组
    if (Array.isArray(data)) {
      images = data;
    } 
    // 情况2: 返回包含visualization_paths和graph_description的对象
    else if (typeof data === 'object') {
      images = Array.isArray(data.visualization_paths) ? data.visualization_paths : [];
      descriptions = Array.isArray(data.graph_description) ? data.graph_description : [];
    }
  }

  // 如果没有图片数据，记录到控制台
  if (images.length === 0) {
    console.warn("VisualizationsModule: 没有找到图片数据", data);
  } else {
    console.log(`VisualizationsModule: 找到 ${images.length} 张图片`);
    console.log("图片路径示例:", images[0]);
  }

  // 首先，展示所有图表的通用描述
  const renderDescriptions = () => {
    if (descriptions.length === 0) return null;
    
    return (
      <div className="mb-8 border-l-4 border-cyan-500 dark:border-cyan-400 pl-5 pr-2 py-4 bg-slate-900/30 backdrop-blur-sm rounded-r-md">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
          <span className="mr-2 bg-gradient-to-r from-cyan-400 to-blue-500 p-0.5 rounded">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
          </span>
          图表分析概述
        </h3>
        <div className="space-y-4 text-slate-200">
          {descriptions.map((desc, idx) => (
            <div key={idx} className="text-base">
              {formatDescription(desc)}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // 格式化描述
  const formatDescription = (desc: string) => {
    if (!desc) return null;
    return desc.split('\n').map((paragraph, i) => 
      paragraph.trim() ? <p key={i} className="text-slate-200 my-2 leading-relaxed text-opacity-90">{paragraph}</p> : null
    );
  };

  return (
    <div className="space-y-8">
      {/* 先显示所有图表的描述 */}
      {renderDescriptions()}
      
      {/* 然后显示图表网格 */}
      {images.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {images.map((src: string, idx: number) => (
            <div key={idx} className="group">
              <div className="relative overflow-hidden rounded-md bg-slate-900/40 backdrop-blur-sm border border-slate-800/60 hover:border-cyan-800/60 transition-all duration-300 p-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-white font-medium flex items-center">
                    <span className="bg-gradient-to-r from-cyan-400 to-blue-500 w-2 h-4 inline-block mr-2 rounded-sm"></span>
                    图表 {idx + 1}
                  </h4>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-slate-300 hover:text-white hover:bg-cyan-700/20 rounded-full transition-colors">
                        <ZoomIn className="h-4 w-4" />
                        <span className="sr-only">放大查看</span>
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-5xl w-[95vw] max-h-[95vh] bg-slate-900/95 border border-cyan-900/50 backdrop-blur-xl [&>button]:text-white [&>button]:hover:bg-cyan-800/30 [&>button]:transition-colors">
                      <DialogHeader className="border-b border-slate-700/50 pb-2">
                        <DialogTitle className="text-white">图表 {idx + 1}</DialogTitle>
                      </DialogHeader>
                      <div className="mt-2 overflow-auto max-h-[80vh] p-2">
                        <img 
                          src={getCorrectImageUrl(src)} 
                          alt={`图表 ${idx + 1} 大图`}
                          className="w-full h-auto object-contain"
                        />
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
                
                <div className="overflow-hidden rounded-md bg-gradient-to-b from-slate-900/10 to-slate-900/30 p-2 group-hover:from-slate-900/20 group-hover:to-slate-900/40 transition-all duration-300">
                  <img 
                    src={getCorrectImageUrl(src)} 
                    alt={`图表 ${idx + 1}`}
                    className="w-full h-auto transition-transform duration-500 group-hover:scale-[1.02]"
                    onError={(e) => {
                      console.error(`图片加载失败: ${src}`, e);
                      e.currentTarget.style.display = 'none';
                      e.currentTarget.parentElement?.appendChild(
                        Object.assign(document.createElement('div'), {
                          className: 'p-4 border border-red-900/50 bg-red-900/10 rounded-md text-red-400 text-center',
                          textContent: `图片加载失败: ${src}`
                        })
                      );
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-slate-400 p-4 rounded-md border border-slate-800/50 bg-slate-900/30 backdrop-blur-sm flex items-center justify-center">
          <span className="mr-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
          暂无图表数据
        </div>
      )}
    </div>
  );
};

export default VisualizationsModule; 