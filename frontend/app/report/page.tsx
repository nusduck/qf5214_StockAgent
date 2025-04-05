'use client';

import { useState } from 'react';
import { StockInfo } from '@/components/report/StockInfo';
import { MarketData } from '@/components/report/MarketData';
import { FinancialData } from '@/components/report/FinancialData';
import { ResearchData } from '@/components/report/ResearchData';

export default function ReportPage() {
  const [stockCode, setStockCode] = useState('600519');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const code = formData.get('stockCode') as string;
    if (code) {
      setStockCode(code);
    }
  };

  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 搜索栏 */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex gap-4 max-w-md">
            <input
              type="text"
              name="stockCode"
              defaultValue={stockCode}
              placeholder="请输入股票代码"
              className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg 
                       text-white placeholder:text-gray-400 focus:outline-none 
                       focus:ring-2 focus:ring-purple-500"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-purple-600 text-white rounded-lg 
                       hover:bg-purple-700 focus:outline-none focus:ring-2 
                       focus:ring-purple-500 focus:ring-offset-2 
                       focus:ring-offset-black"
            >
              分析
            </button>
          </form>
        </div>

        {/* 四个数据区块 */}
        <div className="space-y-8">
          {/* 股票信息 */}
          <section>
            <h2 className="text-xl font-bold text-white mb-4">🏢 股票信息</h2>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 p-6 rounded-lg">
              <StockInfo stockCode={stockCode} />
            </div>
          </section>

          {/* 市场数据 */}
          <section>
            <h2 className="text-xl font-bold text-white mb-4">📈 市场数据</h2>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 p-6 rounded-lg">
              <MarketData stockCode={stockCode} />
            </div>
          </section>

          {/* 财务数据 */}
          <section>
            <h2 className="text-xl font-bold text-white mb-4">💰 财务数据</h2>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 p-6 rounded-lg">
              <FinancialData stockCode={stockCode} />
            </div>
          </section>

          {/* 研究报告 */}
          <section>
            <h2 className="text-xl font-bold text-white mb-4">🔍 研究分析</h2>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 p-6 rounded-lg">
              <ResearchData stockCode={stockCode} />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
