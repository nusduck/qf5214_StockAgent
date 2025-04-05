'use client'

import { useEffect, useState } from 'react'

export default function NewsReportPage() {
  const [analysis, setAnalysis] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:8000/api/insight/news-analysis')
      .then(res => res.json())
      .then(data => {
        if (data.analysis) setAnalysis(data.analysis)
        else setError('接口返回数据为空')
      })
      .catch(err => {
        setError('接口请求失败: ' + err.message)
      })
      .finally(() => setLoading(false))
  }, [])

  const parseBlocks = (blockText: string) => {
    const parts = blockText.split(/【(.+?)】板块：/).filter(Boolean)
    const blocks = []
    for (let i = 0; i < parts.length - 1; i += 2) {
      blocks.push({ title: parts[i], content: parts[i + 1] })
    }
    return blocks
  }

  const parseStockTable = (blockContent: string) => {
    const rows = blockContent
      .split('\n')
      .filter((line) =>
        /股票名称[:：]/.test(line) && /推荐理由[:：]/.test(line) && /推荐建议[:：]/.test(line)
      )
  
    if (rows.length === 0) return null
  
    const parsed = rows.map((line) => {
      const nameMatch = line.match(/股票名称[:：](.*?)(\s+股票代码[:：])/)
      const codeMatch = line.match(/股票代码[:：]([^\s]+)/)
      const reasonMatch = line.match(/推荐理由[:：](.*?)\s+推荐建议[:：]/)
      const suggestionMatch = line.match(/推荐建议[:：](.+)$/)
  
      if (!nameMatch || !codeMatch || !reasonMatch || !suggestionMatch) return null
  
      return {
        name: nameMatch[1].trim(),
        code: codeMatch[1].trim(),
        reason: reasonMatch[1].trim(),
        suggestion: suggestionMatch[1].trim(),
      }
    }).filter(Boolean)
  
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
          {parsed.map((row, idx) => (
            <tr key={idx} className="border-t border-white/10">
              <td className="px-4 py-2">{row.name}</td>
              <td className="px-4 py-2">{row.code}</td>
              <td className="px-4 py-2">{row.reason}</td>
              <td className="px-4 py-2">{row.suggestion}</td>
            </tr>
          ))}
        </tbody>
      </table>
    )
  }
  
  const renderSections = (text: string) => {
    const summaryMatch = text.match(/\*\*一、财经热点分析综述：\*\*\n([\s\S]*?)\n\n\*\*二、行业板块分析：\*\*/)
    const blockMatch = text.match(/\*\*二、行业板块分析：\*\*\n([\s\S]*?)\n\n\*\*三、当前市场关注焦点：\*\*/)
    const focusMatch = text.match(/\*\*三、当前市场关注焦点：\*\*\n([\s\S]*)/)

    const summary = summaryMatch?.[1]?.trim() ?? ''
    const blockText = blockMatch?.[1]?.trim() ?? ''
    const focus = focusMatch?.[1]?.trim() ?? ''

    const blocks = parseBlocks(blockText)

    return (
      <div className="space-y-10">
        {/* 财经热点分析综述 */}
        <section className="bg-white/10 text-white rounded-xl p-6 border border-white/20 backdrop-blur-md">
          <h2 className="text-2xl font-bold mb-4">📌 财经热点分析综述</h2>
          <p className="whitespace-pre-wrap text-sm text-gray-200 leading-relaxed">{summary}</p>
        </section>

        {/* 行业板块分析 */}
        <section className="bg-white/10 text-white rounded-xl p-6 border border-white/20 backdrop-blur-md">
          <h2 className="text-2xl font-bold mb-4">📌 行业板块分析</h2>
          {blocks.length === 0 ? (
            <p className="text-sm text-gray-400">暂无板块内容</p>
          ) : (
            blocks.map((block, idx) => {
              const contentWithoutStocks = block.content.split('个股表现分析及建议：')[0]?.trim()
              return (
                <div key={idx} className="mb-6">
                  <h3 className="text-xl font-semibold text-teal-300 mb-2">{block.title}</h3>
                  <p className="whitespace-pre-wrap text-sm text-gray-200 mb-2">{contentWithoutStocks}</p>
                  {parseStockTable(block.content)}
                </div>
              )
            })
          )}
        </section>

        {/* 当前市场关注焦点 */}
        <section className="bg-white/10 text-white rounded-xl p-6 border border-white/20 backdrop-blur-md">
          <h2 className="text-2xl font-bold mb-4">📌 当前市场关注焦点</h2>
          <p className="whitespace-pre-wrap text-sm text-gray-200 leading-relaxed">{focus}</p>
        </section>
      </div>
    )
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
      ) : (
        renderSections(analysis)
      )}
    </div>
  )
}
