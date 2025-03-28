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
        "report_state": final_state["report_state"].text_reports,
        "visualization_paths": final_state["visualization_paths"],
        "graph_description": final_state["graph_description"],
        "data_file_paths": final_state["data_file_paths"]
    }
    
    return results

def display_basic_info(basic_info):
    if not basic_info["stock_code"]:
        return

    with st.container():
        st.subheader("📌 基本信息")

        cols = st.columns([1, 1, 1])
        with cols[0]:
            st.metric("股票代码", basic_info["stock_code"])
        with cols[1]:
            st.metric("股票名称", basic_info["stock_name"])
        with cols[2]:
            st.metric("所属行业", basic_info["industry"])

        if basic_info["company_info"] is not None and not basic_info["company_info"].empty:
            st.markdown("##### 公司详细信息")
            company_info_df = basic_info["company_info"]
            st.dataframe(company_info_df, use_container_width=True)

def display_market_data(market_data):
    has_data = False
    for key in ["trade_data", "sector_data", "technical_data"]:
        if market_data[key] is not None and not (hasattr(market_data[key], 'empty') and market_data[key].empty):
            has_data = True
            break
            
    if not has_data:
        return

    with st.container():
        st.subheader("📈 市场数据")

        tabs = st.tabs(["交易数据", "行业数据", "技术指标"])

        with tabs[0]:
            st.markdown("##### 交易数据")
            if market_data["trade_data"] is not None and not market_data["trade_data"].empty:
                st.dataframe(market_data["trade_data"].tail(), use_container_width=True)
            else:
                st.info("暂无交易数据")

        with tabs[1]:
            st.markdown("##### 行业数据")
            if market_data["sector_data"] is not None and not market_data["sector_data"].empty:
                st.dataframe(market_data["sector_data"].tail(), use_container_width=True)
            else:
                st.info("暂无行业数据")

        with tabs[2]:
            st.markdown("##### 技术指标")
            if market_data["technical_data"] is not None and not market_data["technical_data"].empty:
                st.dataframe(market_data["technical_data"].tail(), use_container_width=True)
            else:
                st.info("暂无技术指标数据")

def display_financial_data(financial_data):
    if financial_data is None or (hasattr(financial_data, 'empty') and financial_data.empty):
        return

    with st.container():
        st.subheader("💰 财务数据")
        st.dataframe(financial_data, use_container_width=True)

def display_research_data(research_data):
    has_data = False
    
    if research_data["analyst_data"] is not None and not research_data["analyst_data"].empty:
        has_data = True
    
    if research_data["news_data"] and "news" in research_data["news_data"] and research_data["news_data"]["news"]:
        has_data = True
        
    if not has_data:
        return

    with st.container():
        st.subheader("🔍 研究分析")

        tabs = st.tabs(["分析师报告", "相关新闻"])

        with tabs[0]:
            if research_data["analyst_data"] is not None and not research_data["analyst_data"].empty:
                st.dataframe(research_data["analyst_data"], use_container_width=True)
            else:
                st.info("暂无分析师报告数据")

        with tabs[1]:
            if research_data["news_data"] and "news" in research_data["news_data"] and research_data["news_data"]["news"]:
                for news in research_data["news_data"]["news"]:
                    with st.expander(f"{news['News Title']} - {news['Publish Time']}"):
                        st.write(f"**来源:** {news['Source']}")
                        st.write(f"**内容:** {news['News Content']}")
                        if news['News Link']:
                            st.write(f"**链接:** [{news['News Link']}]({news['News Link']})")
            else:
                st.info("暂无相关新闻数据")

def display_visualizations(visualization_paths, graph_description):
    if not visualization_paths:
        return

    with st.container():
        st.subheader("📊 可视化分析")

        # 先显示图表说明（如果有）
        if graph_description and len(graph_description) > 0:
            for i, desc in enumerate(graph_description):
                if desc:
                    st.markdown(f"**图表 {i+1} 说明:** {desc}")
            
            st.markdown("---")
        
        # 按照文件夹分组图像
        image_groups = {}
        for path in visualization_paths:
            folder = path.split('/')[0] if '/' in path else '默认'
            if folder not in image_groups:
                image_groups[folder] = []
            image_groups[folder].append(path)
        
        # 为每个分组创建标签
        for folder, images in image_groups.items():
            st.markdown(f"#### {folder} 分析")
            cols = st.columns(2)
            
            for idx, img_path in enumerate(images):
                try:
                    current_col = cols[idx % len(cols)]
                    with current_col:
                        st.image(img_path, use_container_width=True)
                except Exception as e:
                    with cols[idx % len(cols)]:
                        st.error(f"无法加载图表: {img_path}\n错误: {str(e)}")

def display_report(report_state):
    if not report_state:
        return

    with st.container():
        st.subheader("📝 分析报告")

        report_class_mapping = {
            "sentiment_report": "report-header-sentiment",
            "technical_report": "report-header-technical",
            "fundamentals_report": "report-header-fundamentals",
            "adversarial_report": "report-header-adversarial"
        }
        report_name_mapping = {
            "sentiment_report": "SENTIMENT REPORT",
            "technical_report": "TECHNICAL REPORT",
            "fundamentals_report": "FUNDAMENTAL REPORT",
            "adversarial_report": "ADVERSARIAL REPORT"
        }

        for report_type, content in report_state.items():
            if not content:
                continue

            display_name = report_name_mapping.get(report_type, report_type.replace('_', ' ').upper())
            header_class = report_class_mapping.get(report_type, "report-header-default")

            st.markdown(f'<h2 class="report-header {header_class}">{display_name}</h2>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-content">{content}</div>', unsafe_allow_html=True)

def main():
    st.title("📊 个股智能分析")

    if 'stock_results' not in st.session_state:
        st.session_state.stock_results = None
    if 'stock_input' not in st.session_state:
        st.session_state.stock_input = ""

    col_input, col_button = st.columns([4, 1])
    with col_input:
        stock_input = st.text_input(
            "请输入股票名称或代码",
            value=st.session_state.stock_input,
            placeholder="例如: 宁德时代、300750",
            key="stock_input_widget",
            label_visibility="collapsed"
        )
    st.session_state.stock_input = stock_input

    with col_button:
        analyze_button = st.button("开始分析", type="primary", use_container_width=True)

    if analyze_button and st.session_state.stock_input:
        with st.spinner("正在进行分析..."):
            try:
                results = analyze_stock(st.session_state.stock_input)
                st.session_state.stock_results = results
            except Exception as e:
                st.error(f"分析过程中出现错误: {str(e)}")
                st.session_state.stock_results = None
    elif analyze_button and not st.session_state.stock_input:
        st.warning("请输入股票名称或代码。")

    if st.session_state.stock_results:
        results = st.session_state.stock_results
        
        tabs = st.tabs(["📋 基本信息 & 图表", "📈 市场数据", "💰 财务分析", "🔍 研究 & 报告"])
        
        with tabs[0]:
            display_basic_info(results["basic_info"])
            display_visualizations(
                results["visualization_paths"],
                results["graph_description"]
            )
            
        with tabs[1]:
            display_market_data(results["market_data"])
            
        with tabs[2]:
            display_financial_data(results["financial_data"])
            
        with tabs[3]:
            display_research_data(results["research_data"])
            display_report(results["report_state"])
    else:
        st.info("""
        #### 👋 欢迎使用个股智能分析工具

        1. 在上方搜索框中输入 **股票名称** 或 **代码** (例如: 宁德时代 或 300750)。
        2. 点击 **开始分析** 按钮。
        3. 系统将获取并展示多维度分析结果，助您做出更明智的投资决策。
        """)
        
        st.markdown("---")
        st.markdown("##### 功能示例")
        cols = st.columns(3)
        with cols[0]:
            st.markdown("###### 📈 技术面分析")
            st.image("https://via.placeholder.com/300x200.png?text=技术分析示例", use_container_width=True)
        
        with cols[1]:
            st.markdown("###### 💰 基本面分析")
            st.image("https://via.placeholder.com/300x200.png?text=基本面分析示例", use_container_width=True)
            
        with cols[2]:
            st.markdown("###### 📰 新闻情感分析")
            st.image("https://via.placeholder.com/300x200.png?text=新闻分析示例", use_container_width=True)

if __name__ == "__main__":
    main()