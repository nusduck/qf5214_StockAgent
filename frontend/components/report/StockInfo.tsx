'use client';

import { useStockInfo } from '@/hooks/useStockInfo';

export function StockInfo({ stockCode }: { stockCode: string }) {
  const { data, loading, error } = useStockInfo(stockCode);

  if (loading) return <div className="text-gray-400">加载中...</div>;
  if (error) return <div className="text-red-400">错误: {error.message}</div>;
  if (!data?.data?.stock_info) return null;

  const { stock_info } = data.data;
  
  // 格式化日期
  const formatDate = (dateNum: number) => {
    const str = dateNum.toString();
    const year = str.substring(0, 4);
    const month = str.substring(4, 6);
    const day = str.substring(6, 8);
    return `${year}-${month}-${day}`;
  };

  // 格式化市值
  const formatMarketCap = (value: number) => {
    return (value / 100000000).toFixed(2) + '亿';
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <h3 className="text-gray-400">股票代码</h3>
        <p className="text-white">{stock_info.stock_code}</p>
      </div>
      <div>
        <h3 className="text-gray-400">股票名称</h3>
        <p className="text-white">{stock_info.stock_name}</p>
      </div>
      <div>
        <h3 className="text-gray-400">所属行业</h3>
        <p className="text-white">{stock_info.industry}</p>
      </div>
      <div>
        <h3 className="text-gray-400">上市时间</h3>
        <p className="text-white">{formatDate(stock_info.ipo_date)}</p>
      </div>
      <div>
        <h3 className="text-gray-400">总市值</h3>
        <p className="text-white">{formatMarketCap(stock_info.total_market_cap)}</p>
      </div>
      <div>
        <h3 className="text-gray-400">流通市值</h3>
        <p className="text-white">{formatMarketCap(stock_info.float_market_cap)}</p>
      </div>
      <div>
        <h3 className="text-gray-400">总股本</h3>
        <p className="text-white">{(stock_info.total_shares / 100000000).toFixed(2)}亿股</p>
      </div>
      <div>
        <h3 className="text-gray-400">流通股本</h3>
        <p className="text-white">{(stock_info.float_shares / 100000000).toFixed(2)}亿股</p>
      </div>
      <div className="col-span-2 text-right">
        <p className="text-gray-400 text-sm">
          数据更新时间：{stock_info.snapshot_time}
        </p>
      </div>
    </div>
  );
} 