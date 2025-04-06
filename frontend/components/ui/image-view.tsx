'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Maximize2, X } from 'lucide-react';
import { getImageUrl } from '@/lib/api';

interface ImageViewProps {
  src: string;
  alt?: string;
  width?: number;
  height?: number;
  className?: string;
  lazyLoad?: boolean;
  thumbnailSize?: number;
  showFullScreenButton?: boolean;
}

export const ImageView: React.FC<ImageViewProps> = ({
  src,
  alt = '图片',
  width,
  height,
  className = '',
  lazyLoad = true,
  thumbnailSize = 300,
  showFullScreenButton = true,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [isInView, setIsInView] = useState(!lazyLoad);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const imageRef = useRef<HTMLImageElement>(null);
  
  // 生成缩略图和全尺寸图片URL
  const thumbnailUrl = getImageUrl(src, { thumbnail: true, width: thumbnailSize });
  const fullSizeUrl = getImageUrl(src);
  
  // 监测图片是否进入视口
  useEffect(() => {
    if (!lazyLoad || isInView) return;
    
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    
    if (imageRef.current) {
      observer.observe(imageRef.current);
    }
    
    return () => {
      observer.disconnect();
    };
  }, [lazyLoad, isInView]);
  
  const handleLoad = () => {
    setIsLoading(false);
  };
  
  const handleError = () => {
    setIsLoading(false);
    setIsError(true);
  };
  
  return (
    <div className={`relative ${className}`} style={{ width, height }}>
      {/* 加载中状态 */}
      {isLoading && (
        <Skeleton className="absolute inset-0 w-full h-full rounded-md" />
      )}
      
      {/* 图片加载错误 */}
      {isError && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted rounded-md">
          <span className="text-sm text-muted-foreground">图片加载失败</span>
        </div>
      )}
      
      {/* 实际图片 */}
      {isInView && (
        <img
          ref={imageRef}
          src={thumbnailUrl}
          alt={alt}
          className={`w-full h-full object-contain rounded-md ${isLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
          onLoad={handleLoad}
          onError={handleError}
        />
      )}
      
      {/* 全屏按钮 */}
      {!isLoading && !isError && showFullScreenButton && (
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button 
              variant="outline" 
              size="icon" 
              className="absolute top-2 right-2 bg-background/80 backdrop-blur-sm"
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-screen-lg h-[90vh] flex items-center justify-center p-0">
            <Button 
              variant="ghost" 
              size="icon" 
              className="absolute top-2 right-2 z-10" 
              onClick={() => setIsDialogOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
            <div className="w-full h-full overflow-auto">
              <img 
                src={fullSizeUrl} 
                alt={alt} 
                className="w-full h-full object-contain"
              />
            </div>
          </DialogContent>
        </Dialog>
      )}
      
      {/* 如果没有启用懒加载，则创建一个空引用容器 */}
      {!isInView && (
        <div ref={imageRef} className="w-full h-full min-h-[200px]" />
      )}
    </div>
  );
};

interface ImageGalleryProps {
  images: string[];
  className?: string;
  thumbnailSize?: number;
}

export const ImageGallery: React.FC<ImageGalleryProps> = ({
  images,
  className = '',
  thumbnailSize = 300
}) => {
  if (!images || images.length === 0) {
    return (
      <div className="text-center p-4 text-muted-foreground">
        暂无图片
      </div>
    );
  }
  
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 ${className}`}>
      {images.map((src, idx) => (
        <div key={idx} className="border rounded-md p-2">
          <ImageView
            src={src}
            alt={`图片 ${idx + 1}`}
            lazyLoad={true}
            thumbnailSize={thumbnailSize}
            className="w-full aspect-video"
          />
          <p className="text-xs text-center mt-1">图表 {idx + 1}</p>
        </div>
      ))}
    </div>
  );
}; 