'use client';

import { useState } from 'react';
import { useFinancialData } from '@/hooks/useFinancialData';
import { formatNumber, formatPercent, formatDate } from '@/lib/utils';

export function FinancialData({ stockCode }: { stockCode: string }) {
  const [dateRange, setDateRange] = useState({
    startDate: formatDate(new Date(Date.now() - 365 * 24 * 60 * 60 * 1000)),
    endDate: formatDate(new Date()),
  });

  const { data, loading, error } = useFinancialData(stockCode, {
    startDate: dateRange.startDate,
    endDate: dateRange.endDate,
  });

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (value.length === 10) {
      setDateRange(prev => ({
        ...prev,
        [name]: value.replace(/-/g, ''),
      }));
    }
  };

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

  const { current, history } = data.data;

  return (
    <div className="space-y-6">
      {/* 日期选择器 */}
      <div className="flex gap-4 items-center">
        <div>
          <label className="block text-sm text-gray-400 mb-1">开始日期</label>
          <input
            type="date"
            name="startDate"
            value={dateRange.startDate.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3')}
            onChange={handleDateChange}
            onKeyDown={(e) => e.preventDefault()}
            className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">结束日期</label>
          <input
            type="date"
            name="endDate"
            value={dateRange.endDate.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3')}
            onChange={handleDateChange}
            onKeyDown={(e) => e.preventDefault()}
            className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm"
          />
        </div>
      </div>

      {/* 财务数据表格 */}
      <div className="overflow-x-auto">
        <div className="max-h-[400px] overflow-y-auto relative">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-900 z-10">
              <tr className="text-gray-400 border-b border-gray-700">
                <th className="py-2 text-left">报告期</th>
                {/* 盈利能力 */}
                <th className="py-2 text-right">营业收入(亿)</th>
                <th className="py-2 text-right">收入增长</th>
                <th className="py-2 text-right">净利润(亿)</th>
                <th className="py-2 text-right">利润增长</th>
                <th className="py-2 text-right">净利率</th>
                <th className="py-2 text-right">ROE</th>
                <th className="py-2 text-right">ROE(摊薄)</th>
                {/* 每股指标 */}
                <th className="py-2 text-right">每股收益</th>
                <th className="py-2 text-right">每股净资产</th>
                <th className="py-2 text-right">每股经营现金流</th>
                {/* 营运能力 */}
                <th className="py-2 text-right">存货周转天数</th>
                <th className="py-2 text-right">应收账款周转天数</th>
                {/* 偿债能力 */}
                <th className="py-2 text-right">流动比率</th>
                <th className="py-2 text-right">速动比率</th>
                <th className="py-2 text-right">资产负债率</th>
              </tr>
            </thead>
            <tbody>
              {history.slice().reverse().map((item) => (
                <tr key={item.report_date} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="py-2 text-gray-300">{item.report_date.split('T')[0]}</td>
                  {/* 盈利能力 */}
                  <td className="py-2 text-right text-gray-300">
                    {(item.total_revenue / 100000000).toFixed(2)}
                  </td>
                  <td className={`py-2 text-right ${
                    Number(item.total_revenue_yoy) >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {formatPercent(Number(item.total_revenue_yoy))}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {(item.net_profit / 100000000).toFixed(2)}
                  </td>
                  <td className={`py-2 text-right ${
                    Number(item.net_profit_yoy) >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {formatPercent(Number(item.net_profit_yoy))}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {formatPercent(Number(item.net_margin))}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {formatPercent(Number(item.roe))}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {formatPercent(Number(item.roe_diluted))}
                  </td>
                  {/* 每股指标 */}
                  <td className="py-2 text-right text-gray-300">
                    {item.basic_eps}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {item.net_asset_ps}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {item.op_cash_flow_ps}
                  </td>
                  {/* 营运能力 */}
                  <td className="py-2 text-right text-gray-300">
                    {item.inventory_turnover_days}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {item.ar_turnover_days}
                  </td>
                  {/* 偿债能力 */}
                  <td className="py-2 text-right text-gray-300">
                    {item.current_ratio}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {item.quick_ratio}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {formatPercent(Number(item.debt_asset_ratio))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
} 