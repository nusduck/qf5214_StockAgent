import streamlit as st
from helpers.hotspot_search import get_market_hotspots
import pandas as pd

def main():
    st.title("🔥 市场热点追踪")
    
    # Initialize session state for hotspot results
    if 'hotspot_results' not in st.session_state:
        st.session_state.hotspot_results = None

    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("获取最新市场热点", use_container_width=True):
            with st.spinner("正在获取市场热点信息..."):
                try:
                    # Fetch and store results in session state
                    st.session_state.hotspot_results = get_market_hotspots()
                except Exception as e:
                    st.error(f"获取市场热点失败: {str(e)}")
                    st.session_state.hotspot_results = None # Clear on error

        # Display results from session state if available
        if st.session_state.hotspot_results:
            st.markdown("### 最新市场热点分析")
            st.markdown(st.session_state.hotspot_results)
        else:
            # Show info only if no results are loaded yet
            st.info("点击按钮获取最新的市场热点信息。")

    with col2:
        st.info("""
        📈 本功能通过AI实时分析获取：
        - 最新市场热点
        - 相关概念股票
        - 市场关注度
        """)

if __name__ == "__main__":
    main() 