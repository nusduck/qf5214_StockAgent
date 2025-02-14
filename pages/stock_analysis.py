import streamlit as st
import pandas as pd
from core.workflow import run_stock_analysis
from datetime import datetime

def analyze_stock(company_name: str):
    """
    Analyze a stock using the workflow and return relevant data
    
    Args:
        company_name (str): Name of the company to analyze
    """
    # Run the analysis workflow
    final_state = run_stock_analysis(company_name)
    
    # Access different parts of the state using dictionary access
    results = {
        "basic_info": {
            "stock_code": final_state["basic_info"].stock_code,
            "stock_name": final_state["basic_info"].stock_name,
            "industry": final_state["basic_info"].industry,
            "company_info": final_state["basic_info"].company_info
        },
        "market_data": {
            "trade_data": final_state["market_data"].trade_data,
            "sector_data": final_state["market_data"].sector_data,
            "technical_data": final_state["market_data"].technical_data
        },
        "financial_data": final_state["financial_data"].financial_data,
        "research_data": {
            "analyst_data": final_state["research_data"].analyst_data,
            "news_data": final_state["research_data"].news_data
        },
        "visualization_paths": final_state["visualization_paths"],
        "graph_description": final_state["graph_description"],
        "data_file_paths": final_state["data_file_paths"]
    }
    
    return results

def display_basic_info(basic_info):
    st.subheader("📌 基本信息")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("股票代码", basic_info["stock_code"])
    with col2:
        st.metric("股票名称", basic_info["stock_name"])
    with col3:
        st.metric("所属行业", basic_info["industry"])
    
    if basic_info["company_info"] is not None:
        st.markdown("##### 公司详细信息")
        company_info_df = basic_info["company_info"]
        st.dataframe(company_info_df, use_container_width=True)

def display_market_data(market_data):
    st.subheader("📈 市场数据")
    
    tabs = st.tabs(["交易数据", "行业数据", "技术指标"])
    
    with tabs[0]:
        st.markdown("##### 交易数据")
        if market_data["trade_data"] is not None:
            st.dataframe(market_data["trade_data"].tail(), use_container_width=True)
    
    with tabs[1]:
        st.markdown("##### 行业数据")
        if market_data["sector_data"] is not None:
            st.dataframe(market_data["sector_data"].tail(), use_container_width=True)
    
    with tabs[2]:
        st.markdown("##### 技术指标")
        if market_data["technical_data"] is not None:
            st.dataframe(market_data["technical_data"].tail(), use_container_width=True)

def display_financial_data(financial_data):
    st.subheader("💰 财务数据")
    if financial_data is not None:
        # Display the most recent financial data
        st.dataframe(financial_data, use_container_width=True)

def display_research_data(research_data):
    st.subheader("🔍 研究分析")
    
    tabs = st.tabs(["分析师报告", "相关新闻"])
    
    with tabs[0]:
        if research_data["analyst_data"] is not None and not research_data["analyst_data"].empty:
            st.dataframe(research_data["analyst_data"], use_container_width=True)
        else:
            st.info("暂无分析师报告数据")
    
    with tabs[1]:
        if research_data["news_data"] and "news" in research_data["news_data"]:
            for news in research_data["news_data"]["news"]:
                with st.expander(f"{news['News Title']} - {news['Publish Time']}"):
                    st.write(f"**来源:** {news['Source']}")
                    st.write(f"**内容:** {news['News Content']}")
                    if news['News Link']:
                        st.write(f"**链接:** [{news['News Link']}]({news['News Link']})")

def display_visualizations(visualization_paths, graph_description):
    if visualization_paths:
        st.subheader("📊 可视化分析")
        
        for viz_path in visualization_paths:
            try:
                st.image(viz_path)
                # If there's a description in data_file_paths, display it
                
            except Exception as e:
                st.error(f"无法加载图表: {str(e)}")
        for desc in graph_description:
            st.markdown(desc)

def main():
    st.title("📊 个股智能分析")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        stock_input = st.text_input(
            "请输入股票名称或代码",
            placeholder="例如: 宁德时代、300750"
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
                            # Display all sections
                            display_basic_info(results["basic_info"])
                            st.markdown("---")
                            
                            display_market_data(results["market_data"])
                            st.markdown("---")
                            
                            display_financial_data(results["financial_data"])
                            st.markdown("---")
                            
                            display_research_data(results["research_data"])
                            st.markdown("---")
                            
                            display_visualizations(
                                results["visualization_paths"],
                                results["graph_description"]
                            )
                            
                    except Exception as e:
                        st.error(f"分析过程中出现错误: {str(e)}")
    
    with col1:
        st.info("""
        💡 使用说明：
        1. 输入股票名称或代码
        2. 选择分析类型
        3. 点击开始分析
        
        分析结果将包含：
        - 基本信息
        - 市场数据（交易/行业/技术指标）
        - 财务数据
        - 研究分析（分析师报告/新闻）
        - 可视化图表
        """)

if __name__ == "__main__":
    main()