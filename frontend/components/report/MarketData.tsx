'use client';

import { useState } from 'react';
import { useMarketData } from '@/hooks/useMarketData';
import { formatNumber, formatPercent, formatDate } from '@/lib/utils';

export function MarketData({ stockCode }: { stockCode: string }) {
  const [dateRange, setDateRange] = useState({
    startDate: formatDate(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)),
    endDate: formatDate(new Date()),
  });

  const { data, loading, error } = useMarketData(stockCode, {
    startDate: dateRange.startDate,
    endDate: dateRange.endDate,
  });

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    // 只有当用户完成日期选择（输入完整的年月日）时才更新状态
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
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="h-4 bg-gray-700 rounded w-20 mb-2"></div>
            <div className="h-8 bg-gray-700 rounded w-32"></div>
          </div>
          <div>
            <div className="h-4 bg-gray-700 rounded w-20 mb-2"></div>
            <div className="h-8 bg-gray-700 rounded w-32"></div>
          </div>
        </div>
        <div className="h-[400px] bg-gray-700 rounded"></div>
      </div>
    );
  }
  if (error) return <div className="text-red-400">错误: {error.message}</div>;
  if (!data?.data?.trade?.data) return null;

  const latestData = data.data.trade.data[data.data.trade.data.length - 1];
  const { summary } = data.data.trade;

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

      {/* 实时行情概览 */}
      <div className="flex justify-between items-center">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-gray-400">最新价格</h3>
            <p className="text-white text-2xl font-bold">{latestData.close}</p>
            <span className={`text-sm ${latestData.change_percent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {latestData.change_percent >= 0 ? '+' : ''}{latestData.change_percent.toFixed(2)}%
            </span>
          </div>
          <div>
            <h3 className="text-gray-400">成交量</h3>
            <p className="text-white">{formatNumber(latestData.volume)}</p>
            <p className="text-gray-400 text-sm">换手率: {latestData.turnover_rate.toFixed(2)}%</p>
          </div>
        </div>
        <div className="text-gray-400 text-sm">
          更新时间：{new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* 交易数据表格 */}
      <div className="overflow-x-auto">
        <div className="max-h-[400px] overflow-y-auto relative">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-900 z-10">
              <tr className="text-gray-400 border-b border-gray-700">
                <th className="py-2 text-left">日期</th>
                <th className="py-2 text-right">开盘</th>
                <th className="py-2 text-right">最高</th>
                <th className="py-2 text-right">最低</th>
                <th className="py-2 text-right">收盘</th>
                <th className="py-2 text-right">涨跌幅</th>
                <th className="py-2 text-right">成交量</th>
                <th className="py-2 text-right">换手率</th>
              </tr>
            </thead>
            <tbody>
              {data.data.trade.data.slice().reverse().map((item) => (
                <tr key={item.date} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="py-2 text-gray-300">{item.date}</td>
                  <td className="py-2 text-right text-gray-300">
                    {item.open.toFixed(2)}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {item.high.toFixed(2)}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {item.low.toFixed(2)}
                  </td>
                  <td className="py-2 text-right text-gray-300">
                    {item.close.toFixed(2)}
                  </td>
                  <td className={`py-2 text-right ${
                    item.change_percent >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {formatPercent(item.change_percent)}
                  </td>
                  <td className="py-2 text-right text-gray-300">{formatNumber(item.volume)}</td>
                  <td className="py-2 text-right text-gray-300">{item.turnover_rate.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 技术指标 */}
      <div className="mt-4">
        <h3 className="text-gray-400 mb-2">技术指标</h3>
        <div className="overflow-x-auto">
          <div className="max-h-[200px] overflow-y-auto relative">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-900 z-10">
                <tr className="text-gray-400 border-b border-gray-700">
                  <th className="py-2 text-left">日期</th>
                  <th className="py-2 text-center">MACD</th>
                  <th className="py-2 text-center">RSI</th>
                  <th className="py-2 text-center">KDJ</th>
                </tr>
              </thead>
              <tbody>
                {data.data.technical.data.slice().reverse().map((item) => (
                  <tr key={item.trade_date} className="border-b border-gray-800 hover:bg-gray-800/50">
                    <td className="py-2 text-gray-300">{item.trade_date}</td>
                    <td className="py-2 text-center">
                      <span className={`px-2 py-1 rounded text-xs ${
                        item.macd_signal === '金叉' ? 'bg-green-500/20 text-green-400' :
                        item.macd_signal === '死叉' ? 'bg-red-500/20 text-red-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {item.macd_signal}
                      </span>
                    </td>
                    <td className="py-2 text-center">
                      <span className={`px-2 py-1 rounded text-xs ${
                        item.rsi_signal === '超买' ? 'bg-red-500/20 text-red-400' :
                        item.rsi_signal === '超卖' ? 'bg-green-500/20 text-green-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {item.rsi_signal}
                      </span>
                    </td>
                    <td className="py-2 text-center">
                      <span className={`px-2 py-1 rounded text-xs ${
                        item.kdj_signal === '超买' ? 'bg-red-500/20 text-red-400' :
                        item.kdj_signal === '超卖' ? 'bg-green-500/20 text-green-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {item.kdj_signal}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* 指标说明 */}
        <div className="grid grid-cols-3 gap-4 mt-4 text-sm">
          <div>
            <h4 className="text-gray-400 mb-1">MACD</h4>
            <p className="text-gray-500 text-xs">
              趋势指标，金叉看多，死叉看空
            </p>
          </div>
          <div>
            <h4 className="text-gray-400 mb-1">RSI</h4>
            <p className="text-gray-500 text-xs">
              超买超卖指标，高于70超买，低于30超卖
            </p>
          </div>
          <div>
            <h4 className="text-gray-400 mb-1">KDJ</h4>
            <p className="text-gray-500 text-xs">
              随机指标，高于80超买，低于20超卖
            </p>
          </div>
        </div>
      </div>

      {/* 市场统计 */}
      <div className="mt-4">
        <h3 className="text-gray-400 mb-2">市场统计</h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="space-y-2">
            <p className="text-sm">
              <span className="text-gray-400">平均成交量: </span>
              <span className="text-white">{formatNumber(summary.avg_volume)}</span>
            </p>
            <p className="text-sm">
              <span className="text-gray-400">平均换手率: </span>
              <span className="text-white">{summary.avg_turnover.toFixed(2)}%</span>
            </p>
            <p className="text-sm">
              <span className="text-gray-400">总成交额: </span>
              <span className="text-white">{(summary.total_amount / 100000000).toFixed(2)}亿</span>
            </p>
          </div>
        </div>

        {/* 板块数据表格 */}
        <div className="overflow-x-auto">
          <div className="max-h-[200px] overflow-y-auto relative">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-900 z-10">
                <tr className="text-gray-400 border-b border-gray-700">
                  <th className="py-2 text-left">日期</th>
                  <th className="py-2 text-right">板块涨跌幅</th>
                  <th className="py-2 text-right">成交额(亿)</th>
                  <th className="py-2 text-right">换手率</th>
                  <th className="py-2 text-right">领涨股</th>
                  <th className="py-2 text-right">领涨幅度</th>
                </tr>
              </thead>
              <tbody>
                {data.data.sector?.history?.slice().reverse().map((item) => (
                  <tr key={item.date} className="border-b border-gray-800 hover:bg-gray-800/50">
                    <td className="py-2 text-gray-300">{item.date}</td>
                    <td className={`py-2 text-right ${
                      item.change_percent >= 0 ? 'text-green-500' : 'text-red-500'
                    }`}>
                      {formatPercent(item.change_percent)}
                    </td>
                    <td className="py-2 text-right text-gray-300">
                      {(item.amount / 100000000).toFixed(2)}
                    </td>
                    <td className="py-2 text-right text-gray-300">
                      {item.turnover_rate.toFixed(2)}%
                    </td>
                    <td className="py-2 text-right text-gray-300">
                      {item.leading_stock_name}
                    </td>
                    <td className={`py-2 text-right ${
                      item.leading_stock_change >= 0 ? 'text-green-500' : 'text-red-500'
                    }`}>
                      {formatPercent(item.leading_stock_change)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 板块统计信息 */}
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div>
            <h4 className="text-gray-400 text-sm mb-1">板块表现</h4>
            <p className="text-white text-lg">
              {data.data.sector?.summary?.performance_score || '--'} 
              <span className="text-gray-400 text-sm ml-1">分</span>
            </p>
          </div>
          <div>
            <h4 className="text-gray-400 text-sm mb-1">成分股数量</h4>
            <p className="text-white text-lg">
              {data.data.sector?.summary?.stock_count || '--'}
              <span className="text-gray-400 text-sm ml-1">只</span>
            </p>
          </div>
          <div>
            <h4 className="text-gray-400 text-sm mb-1">总市值</h4>
            <p className="text-white text-lg">
              {data.data.sector?.summary?.total_market_cap 
                ? (data.data.sector.summary.total_market_cap / 100000000).toFixed(2)
                : '--'}
              <span className="text-gray-400 text-sm ml-1">亿</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 