import streamlit as st

# 强制设置页面配置为第一个命令
st.set_page_config(
    page_title="智能股票分析系统",
    page_icon="🤖",
    layout="wide",
)



# 隐藏默认的导航栏和页脚
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 主页面内容
st.title("🤖 智能股票分析系统")

# 项目简介
st.markdown("""
## 📌 项目简介
这是一个基于 LLMs 的智能股票分析系统，利用多个专业 Agent 来分析中国 A 股市场。

### 🎯 主要功能
- **市场热点追踪**: 实时获取市场热点信息和相关概念股
- **个股智能分析**: 提供技术面分析和投资建议

### 🔧 技术架构
- 前端：Streamlit
- AI模型：GPT-4 & Gemini Pro
- Agent框架：LangChain
- 数据来源：多个金融数据API

### 📊 数据分析维度
- 技术面分析
- 市场热点分析
- 智能投资建议
""")

# 添加GitHub仓库链接
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 🔗 项目链接
[![GitHub](https://img.shields.io/badge/GitHub-qf5214_StockAgent-blue?logo=github)](https://github.com/nusduck/qf5214_StockAgent)
""")

# 在主页面添加使用说明
with st.expander("💡 使用说明", expanded=True):
    st.markdown("""
    1. 使用左侧导航栏选择功能模块
    2. **市场热点追踪**：
        - 点击获取按钮实时获取市场热点
        - 查看相关概念股票信息
    3. **个股分析**：
        - 输入股票名称或代码
        - 选择分析类型
        - 获取详细分析报告
    """)