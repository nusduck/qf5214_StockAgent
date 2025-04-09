"use client";

import React, { useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { Share2, Info } from "lucide-react";
import StockAnalysisMain from "@/components/stockanalysis/StockAnalysisMain";
import { createContext, useContext, useState } from 'react';

// 创建全局状态上下文
export const AnalysisContext = createContext<{ 
  lastTaskId: string | null; 
  setLastTaskId: (id: string | null) => void;
}>({ 
  lastTaskId: null, 
  setLastTaskId: () => {} 
});

// 热门股票推荐列表
const popularStocks = [
  { name: '阿里巴巴', code: 'BABA' },
  { name: '腾讯控股', code: '0700' },
  { name: '京东', code: 'JD' },
  { name: '百度', code: 'BIDU' },
  { name: '美团', code: '3690' },
  { name: '拼多多', code: 'PDD' },
  { name: '网易', code: 'NTES' }
];

export default function StockAnalysisPage() {
  // 路由和URL参数
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialCompany = searchParams.get("company") || "";
  
  // 状态变量
  const [companyName, setCompanyName] = useState(initialCompany);
  const [submitted, setSubmitted] = useState(!!initialCompany);
  const [lastTaskId, setLastTaskId] = useState<string | null>(null);
  const { toast } = useToast();

  // 处理表单提交
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (companyName.trim()) {
      setSubmitted(true);
      // 更新URL，方便分享
      router.push(`/stockanalysis?company=${encodeURIComponent(companyName)}`);
    }
  };

  // 重置分析
  const handleReset = () => {
    setCompanyName("");
    setSubmitted(false);
    router.push('/stockanalysis');
  };

  // 分享当前分析链接
  const handleShare = useCallback(() => {
    if (!companyName) return;
    
    try {
      const shareUrl = `${window.location.origin}/stockanalysis?company=${encodeURIComponent(companyName)}`;
      
      if (navigator.share) {
        navigator.share({
          title: `${companyName} 股票分析报告`,
          text: `查看 ${companyName} 的详细股票分析报告`,
          url: shareUrl,
        });
      } else {
        // 如果不支持原生分享，复制到剪贴板
        navigator.clipboard.writeText(shareUrl).then(() => {
          toast({
            title: "链接已复制",
            description: "分析报告链接已复制到剪贴板",
          });
        });
      }
    } catch (error) {
      console.error("分享失败:", error);
    }
  }, [companyName, toast]);

  // 选择热门股票
  const selectPopularStock = (stock: { name: string, code: string }) => {
    setCompanyName(stock.name);
    setSubmitted(true);
    router.push(`/stockanalysis?company=${encodeURIComponent(stock.name)}`);
  };

  return (
    <AnalysisContext.Provider value={{ lastTaskId, setLastTaskId }}>
      <div className="container mx-auto py-8 px-4">
        <div className="flex flex-col md:flex-row items-start justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 inline-block">股票研究报告</h1>
            <p className="text-muted-foreground mt-2">获取全面的股票分析及研究数据</p>
          </div>
          {submitted && (
            <Button 
              variant="ghost" 
              size="sm" 
              className="mt-4 md:mt-0 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 hover:from-purple-500 hover:to-pink-600 hover:bg-transparent"
              onClick={handleShare}
            >
              <Share2 className="h-4 w-4 mr-2 text-purple-500" />
              分享报告
            </Button>
          )}
        </div>
        
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>输入股票信息</CardTitle>
            <CardDescription>
              输入公司名称或股票代码来获取详细分析报告
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-4">
              <Input
                placeholder="输入公司名称或股票代码（如：阿里巴巴、BABA）"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="flex-1"
                disabled={submitted}
              />
              {!submitted ? (
                <Button type="submit" disabled={!companyName.trim()}>
                  获取报告
                </Button>
              ) : (
                <Button type="button" variant="outline" onClick={handleReset}>
                  新分析
                </Button>
              )}
            </form>
            
            {!submitted && (
              <div className="mt-6">
                <div className="flex items-center gap-2 mb-3">
                  <Info className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">热门股票推荐</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {popularStocks.map((stock) => (
                    <Button 
                      key={stock.code}
                      variant="outline" 
                      size="sm"
                      onClick={() => selectPopularStock(stock)}
                      className="text-xs"
                    >
                      {stock.name} ({stock.code})
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {submitted && (
          <div className="mt-8">
            <StockAnalysisMain companyName={companyName} autoStart={true} />
          </div>
        )}
      </div>
    </AnalysisContext.Provider>
  );
}
