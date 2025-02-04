import streamlit as st
from helpers.hotspot_search import get_market_hotspots
import pandas as pd

def main():
    st.title("🔥 市场热点追踪")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("获取最新市场热点", use_container_width=True):
            with st.spinner("正在获取市场热点信息..."):
                try:
                    hotspot_results = get_market_hotspots()
                    st.markdown(hotspot_results)
                except Exception as e:
                    st.error(f"获取市场热点失败: {str(e)}")
    
    with col2:
        st.info("""
        📈 本功能通过AI实时分析获取：
        - 最新市场热点
        - 相关概念股票
        - 市场关注度
        """)

if __name__ == "__main__":
    main() 