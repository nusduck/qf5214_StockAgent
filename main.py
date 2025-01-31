from agents.demo_stock_agent import StockAnalysisAgent, TechnicalAnalysisAgent

def analyze_stock(symbol: str) -> dict:
    # 创建多个专门的分析师
    fundamental_analyst = StockAnalysisAgent()
    technical_analyst = TechnicalAnalysisAgent()
    
    # 收集各个分析师的分析结果
    results = {
        "基本面分析": fundamental_analyst.analyze({"input": f"分析股票 {symbol} 的基本面情况"}),
        "技术分析": technical_analyst.analyze({"input": f"分析股票 {symbol} 的技术面情况"})
    }
    
    return results

if __name__ == "__main__":
    symbol = "AAPL"  # 示例：分析苹果公司
    analysis_results = analyze_stock(symbol)
    
    for analysis_type, result in analysis_results.items():
        print(f"\n{analysis_type}:")
        print(result)
