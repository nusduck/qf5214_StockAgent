import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PartialAnalysisResult } from "@/lib/types";
import { CheckCircle2, XCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface PartialResultProps {
  result: PartialAnalysisResult;
  className?: string;
}

export function PartialResult({ result, className }: PartialResultProps) {
  const analysisStatus = result.analysis_status || {
    basic_info_ready: !!result.basic_info,
    market_data_ready: !!result.market_data,
    financial_data_ready: !!result.financial_data,
    research_data_ready: !!result.research_data
  };
  
  // 获取可展示的内容类型
  const hasBasicInfo = !!result.basic_info;
  const hasMarketData = !!result.market_data;
  const hasFinancialData = !!result.financial_data;
  const hasResearchData = !!result.research_data;
  const hasVisualization = !!result.visualization_paths?.length;
  
  return (
    <Card className={cn("mt-4", className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">分析进度</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* 分析模块状态 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <StatusItem 
              title="基本信息" 
              ready={analysisStatus.basic_info_ready} 
            />
            <StatusItem 
              title="市场数据" 
              ready={analysisStatus.market_data_ready} 
            />
            <StatusItem 
              title="财务数据" 
              ready={analysisStatus.financial_data_ready} 
            />
            <StatusItem 
              title="研究报告" 
              ready={analysisStatus.research_data_ready} 
            />
          </div>
          
          {/* 基本信息展示 */}
          {hasBasicInfo && (
            <div className="border rounded-md p-3">
              <h3 className="text-sm font-medium mb-2 flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-1" />
                基本信息
              </h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {result.basic_info?.stock_name && (
                  <div>
                    <span className="text-muted-foreground">公司名称:</span>{" "}
                    {result.basic_info.stock_name}
                  </div>
                )}
                {result.basic_info?.stock_code && (
                  <div>
                    <span className="text-muted-foreground">股票代码:</span>{" "}
                    {result.basic_info.stock_code}
                  </div>
                )}
                {result.basic_info?.industry && (
                  <div>
                    <span className="text-muted-foreground">所属行业:</span>{" "}
                    {result.basic_info.industry}
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* 市场数据摘要 */}
          {hasMarketData && (
            <div className="border rounded-md p-3">
              <h3 className="text-sm font-medium mb-2 flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-1" />
                市场数据摘要
              </h3>
              <p className="text-sm text-muted-foreground">
                市场数据已准备就绪，将在完整报告中显示
              </p>
            </div>
          )}
          
          {/* 可视化图表预览 */}
          {hasVisualization && (
            <div className="border rounded-md p-3">
              <h3 className="text-sm font-medium mb-2 flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-1" />
                图表预览
              </h3>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {result.visualization_paths?.slice(0, 2).map((path, idx) => (
                  <div key={idx} className="aspect-video bg-muted rounded-md overflow-hidden">
                    <img 
                      src={path} 
                      alt={`预览图 ${idx+1}`}
                      className="w-full h-full object-contain" 
                    />
                  </div>
                ))}
                {(result.visualization_paths?.length || 0) > 2 && (
                  <div className="text-sm text-muted-foreground mt-1">
                    还有 {result.visualization_paths!.length - 2} 张图表...
                  </div>
                )}
              </div>
            </div>
          )}
          
          <p className="text-sm text-muted-foreground italic">
            分析仍在进行中，完整结果将在分析完成后显示...
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// 状态项组件
function StatusItem({ title, ready }: { title: string; ready: boolean }) {
  return (
    <div className={cn(
      "flex items-center gap-1.5 p-2 rounded-md text-sm",
      ready ? "bg-green-50 text-green-700" : "bg-muted text-muted-foreground"
    )}>
      {ready ? (
        <CheckCircle2 className="h-4 w-4 text-green-500" />
      ) : (
        <Clock className="h-4 w-4" />
      )}
      <span>{title}</span>
    </div>
  );
} 