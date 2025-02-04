import streamlit as st
from agents.demo_stock_agent import TechnicalAnalysisAgent,StockAnalysisAgent
import pandas as pd

def analyze_stock(symbol: str) -> dict:
    # 创建技术分析师
    technical_analyst = TechnicalAnalysisAgent()
    fundamental_analyst = StockAnalysisAgent()
    # 收集分析结果
    results = {
        # "基本面分析": fundamental_analyst.analyze({
        #     "input": f"首先请自行查询 {symbol} 的yfinance的代码，然后调用工具获取股票"
        # }),
        "技术分析": technical_analyst.analyze({
            "input": f"首先请自行查询 {symbol} 的股票代码，然后调用工具获取股票2024-06到2025-01的技术面情况"
        })
    }
    
    return results

def main():
    st.title("📊 个股智能分析")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        stock_input = st.text_input(
            "请输入股票名称或代码",
            placeholder="例如: 比亚迪、600519"
        )
        
        if stock_input:
            analysis_type = st.radio(
                "选择分析类型",
                ["技术面分析", "基本面分析", "综合分析"]
            )
            
            if st.button("开始分析", use_container_width=True):
                with st.spinner("正在进行分析..."):
                    try:
                        results = analyze_stock(stock_input)
                        
                        with col2:
                            for analysis_type, result in results.items():
                                st.subheader(analysis_type)
                                st.markdown(result)
                                st.markdown("---")
                            
                    except Exception as e:
                        st.error(f"分析过程中出现错误: {str(e)}")
    
    with col1:
        st.info("""
        💡 使用说明：
        1. 输入股票名称或代码
        2. 选择分析类型
        3. 点击开始分析
        """)

if __name__ == "__main__":
    main() 