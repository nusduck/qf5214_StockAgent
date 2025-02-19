'use client';

import { useState } from 'react';
import { useResearchData } from '@/hooks/useResearchData';
import { formatDate } from '@/lib/utils';

export function ResearchData({ stockCode }: { stockCode: string }) {
  const { data, loading, error } = useResearchData(stockCode);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-gray-700 rounded w-1/4"></div>
        <div className="space-y-4">
          <div className="h-4 bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-700 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error) return <div className="text-red-400">错误: {error.message}</div>;
  if (!data?.data) return null;

  const { news, statistics, summary, snapshot_time } = data.data;

  return (
    <div className="space-y-6">
      {/* 新闻列表 */}
      <div>
        <h3 className="text-lg font-medium text-white mb-4">新闻报道</h3>
        <div className="max-h-[500px] overflow-y-auto">
          {news.map((item, index) => (
            <div key={index} className="mb-4 p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800/80">
              <div className="flex justify-between items-start mb-2">
                <a 
                  href={item.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-white hover:text-blue-400 text-lg font-medium"
                >
                  {item.title}
                </a>
                <span className="text-gray-400 text-sm whitespace-nowrap ml-4">
                  {item.publish_time}
                </span>
              </div>
              <p className="text-gray-300 text-sm mb-2">{item.content}</p>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-400">来源：{item.source}</span>
                <a 
                  href={item.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300"
                >
                  查看原文
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 新闻统计信息 */}
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="text-gray-400 mb-2">新闻总量</h4>
          <p className="text-white text-2xl">{statistics.total_news}</p>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="text-gray-400 mb-2">总字数</h4>
          <p className="text-white text-2xl">{statistics.total_chars.toLocaleString()}</p>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h4 className="text-gray-400 mb-2">主要来源</h4>
          <div className="space-y-1 max-h-[100px] overflow-y-auto">
            {Object.entries(statistics.source_distribution)
              .sort(([,a], [,b]) => b - a)
              .slice(0, 5)
              .map(([source, count]) => (
                <div key={source} className="flex justify-between text-sm">
                  <span className="text-gray-300">{source}</span>
                  <span className="text-gray-400">{count}</span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* 分析师报告统计 */}
      <div className="p-4 bg-gray-800/50 rounded-lg">
        <h3 className="text-lg font-medium text-white mb-4">分析师报告</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <h4 className="text-gray-400 mb-2">分析师数量</h4>
            <p className="text-white text-2xl">{summary?.analyst_count ?? 0}</p>
          </div>
          <div>
            <h4 className="text-gray-400 mb-2">报告数量</h4>
            <p className="text-white text-2xl">{summary?.report_count ?? 0}</p>
          </div>
          <div>
            <h4 className="text-gray-400 mb-2">评级分布</h4>
            <div className="space-y-1">
              {Object.entries(summary?.rating_distribution ?? {}).map(([rating, count]) => (
                <div key={rating} className="flex justify-between text-sm">
                  <span className="text-gray-300">{rating}</span>
                  <span className="text-gray-400">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="text-right text-sm text-gray-400">
        数据更新时间：{snapshot_time}
      </div>
    </div>
  );
} 