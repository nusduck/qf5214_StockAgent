'use client'
#recommendation

import { useEffect, useRef, useState } from 'react'



type StockItem = {
  name: string
  code: string
  reason: string
  suggestion: string
}

type SectorItem = {
  name: string
  news: string
  drivers: string
  impact: {
    short_term: string
    mid_term: string
  }
  stocks: StockItem[]
}

type AnalysisData = {
  overview: string
  sectors: SectorItem[]
  focus: string
}

export default function NewsReportPage() {
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  // 用于防止重复请求的引用
  const requestInProgress = useRef(false);

  useEffect(() => {
    // API 请求，假设后端接口返回的数据结构符合要求
    setLoading(true);
    fetch('http://localhost:8001/api/insight/news-analysis')
      .then(res => {
        if (!res.ok) {
          throw new Error(`API响应错误: ${res.status} ${res.statusText}`);
        }
        return res.json();
      })
      .then(data => {
        console.log('API 返回的数据：', data);  // 调试日志
        
        // 确保数据结构是符合预期的
        if (data?.analysis) {
          // 使用默认值防止缺失字段
          const processedData = {
            overview: data.analysis.overview || '暂无分析综述',
            sectors: Array.isArray(data.analysis.sectors) ? data.analysis.sectors : [],
            focus: data.analysis.focus || '暂无市场焦点分析'
          };
          setAnalysis(processedData);
        } else {
          setError('接口返回数据结构不符合预期');
        }
      })
      .catch(err => {
        console.error('API请求错误:', err);
        setError('接口请求失败: ' + err.message);
      })
      .finally(() => setLoading(false));
  }, [])

  const renderStockTable = (stocks: StockItem[]) => {
    // 确保stocks是数组且不为空
    if (!stocks || !Array.isArray(stocks) || stocks.length === 0) {
      return (
        <div className="p-4 text-white/70 italic">
          暂无推荐股票信息
        </div>
      );
    }
    
    return (
      <table className="w-full text-sm text-left text-white border border-white/20 my-4">
        <thead className="text-xs uppercase bg-white/10 text-white border-b border-white/20">
          <tr>
            <th className="px-4 py-2">股票名称</th>
            <th className="px-4 py-2">股票代码</th>
            <th className="px-4 py-2">推荐理由</th>
            <th className="px-4 py-2">推荐建议</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock, idx) => (
            <tr key={idx} className="border-t border-white/10">
              <td className="px-4 py-2">{stock.name}</td>
              <td className="px-4 py-2">{stock.code}</td>
              <td className="px-4 py-2">{stock.reason}</td>
              <td className="px-4 py-2">{stock.suggestion}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  }

  return (
    <div className="max-w-5xl mx-auto p-8">
      <h1 className="text-3xl font-bold text-white mb-8 flex items-center gap-3">
        <span>📊</span>
        财经热点分析报告
      </h1>

      {loading ? (
        <p className="text-gray-400">正在加载财经热点分析...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : analysis ? (
        <div className="space-y-10">
          {/* 财经热点分析综述 */}
          <section className="bg-white/10 text-white rounded-xl p-6 border border-white/20 backdrop-blur-md">
            <h2 className="text-2xl font-bold mb-4">📌 财经热点分析综述</h2>
            <p className="whitespace-pre-wrap text-sm text-gray-200 leading-relaxed">
              {analysis.overview}
            </p>
          </section>

          {/* 行业板块分析 */}
          <section className="bg-white/10 text-white rounded-xl p-6 border border-white/20 backdrop-blur-md">
            <h2 className="text-2xl font-bold mb-4">📌 行业板块分析</h2>
            {analysis.sectors && Array.isArray(analysis.sectors) ? (
              analysis.sectors.map((sector, idx) => (
                <div key={idx} className="mb-6">
                  <h3 className="text-xl font-semibold text-teal-300 mb-2">{sector.name || '未命名'}板块</h3>
                  <p className="text-sm text-gray-200 mb-1">
                    <strong>核心新闻：</strong> {sector.news || '暂无数据'}
                  </p>
                  <p className="text-sm text-gray-200 mb-1">
                    <strong>驱动因素分析：</strong> {sector.drivers || '暂无数据'}
                  </p>
                  <p className="text-sm text-gray-200 mb-1">
                    <strong>市场影响推演：</strong>
                  </p>
                  <ul className="text-sm text-gray-200 mb-2 list-disc list-inside pl-4">
                    <li><strong>短期：</strong>{sector.impact?.short_term || '暂无数据'}</li>
                    <li><strong>中期：</strong>{sector.impact?.mid_term || '暂无数据'}</li>
                  </ul>
                  {renderStockTable(sector.stocks || [])}
                </div>
              ))
            ) : (
              <p className="text-gray-400">暂无行业板块分析数据</p>
            )}
          </section>

          {/* 当前市场关注焦点 */}
          <section className="bg-white/10 text-white rounded-xl p-6 border border-white/20 backdrop-blur-md">
            <h2 className="text-2xl font-bold mb-4">📌 当前市场关注焦点</h2>
            <p className="whitespace-pre-wrap text-sm text-gray-200 leading-relaxed">{analysis.focus}</p>
          </section>
        </div>
      ) : null}
    </div>
  )
}
