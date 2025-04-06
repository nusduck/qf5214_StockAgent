import React, { useEffect, useState } from "react";
import { Sparkles, Brain, LineChart, FileText, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";

interface AnalysisAnimationProps {
  progress: number;
  className?: string;
}

export function AnalysisAnimation({ progress, className }: AnalysisAnimationProps) {
  const [phase, setPhase] = useState(0);
  
  useEffect(() => {
    // 根据进度自动切换动画阶段
    const newPhase = Math.floor(progress / 20);
    setPhase(newPhase);
    
    // 低进度时的动画效果
    const interval = setInterval(() => {
      if (progress < 100) {
        setPhase(prev => (prev + 1) % 5);
      } else {
        clearInterval(interval);
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [progress]);
  
  return (
    <div className={cn("flex flex-col items-center py-6", className)}>
      <div className="relative w-48 h-48 mb-4">
        {/* 数据收集 */}
        <div className={cn(
          "absolute inset-0 flex items-center justify-center transition-opacity duration-500",
          phase === 0 ? "opacity-100" : "opacity-0"
        )}>
          <Sparkles className="h-16 w-16 text-blue-500 animate-pulse" />
        </div>
        
        {/* 处理分析 */}
        <div className={cn(
          "absolute inset-0 flex items-center justify-center transition-opacity duration-500",
          phase === 1 ? "opacity-100" : "opacity-0"
        )}>
          <Brain className="h-16 w-16 text-purple-500 animate-pulse" />
        </div>
        
        {/* 图表生成 */}
        <div className={cn(
          "absolute inset-0 flex items-center justify-center transition-opacity duration-500",
          phase === 2 ? "opacity-100" : "opacity-0"
        )}>
          <LineChart className="h-16 w-16 text-green-500 animate-pulse" />
        </div>
        
        {/* 报告编写 */}
        <div className={cn(
          "absolute inset-0 flex items-center justify-center transition-opacity duration-500",
          phase === 3 ? "opacity-100" : "opacity-0"
        )}>
          <FileText className="h-16 w-16 text-orange-500 animate-pulse" />
        </div>
        
        {/* 结论生成 */}
        <div className={cn(
          "absolute inset-0 flex items-center justify-center transition-opacity duration-500",
          phase === 4 ? "opacity-100" : "opacity-0"
        )}>
          <Lightbulb className="h-16 w-16 text-yellow-500 animate-pulse" />
        </div>
      </div>
      
      <p className="text-center text-sm text-muted-foreground">
        {phase === 0 && "收集和处理市场数据..."}
        {phase === 1 && "分析财务指标和公司基本面..."}
        {phase === 2 && "生成技术分析图表..."}
        {phase === 3 && "撰写研究报告..."}
        {phase === 4 && "总结投资建议和见解..."}
      </p>
    </div>
  );
} 