import streamlit as st
from dotenv import load_dotenv
import os

# 加载.env文件中的环境变量
load_dotenv()

# 现在可以访问环境变量
# os.environ["OPENAI_API_KEY"] 应该已经可用

# 强制设置页面配置为第一个命令
st.set_page_config(
    page_title="智能股票分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置自定义CSS样式
custom_css = """
<style>
    /* Futuristic Theme Refined - 统一配色方案 */
    :root {
        --primary-color: #00bcd4; /* Refined Cyan/Teal */
        --secondary-color: #ffeb3b; /* Yellow accent */
        --background-color: #0f172a; /* Dark Slate Blue */
        --card-bg-color: #1e293b; /* Lighter Slate Blue */
        --text-color: #e2e8f0; /* Light Gray/ quase White */
        --text-color-darker: #94a3b8; /* Medium Gray */
        --border-color: #00bcd4; /* Match primary */
        --success-color: #4caf50; /* Green */
        --info-color: #2196f3; /* Blue */
        --warning-color: #ff9800; /* Orange */
        --error-color: #f44336; /* Red */
        --input-bg-color: #334155; /* Input background */
    }

    /* 统一了子页面和主页面的样式 */
    .main .block-container {
        background-color: var(--background-color);
        padding: 1.5rem;
    }

    /* 修复指标和图表的边框和颜色 */
    [data-testid="stMetric"] {
        background-color: var(--card-bg-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-color);
    }

    /* 统一标签页风格 */
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        border-bottom: none;
    }

    /* 统一图像内容样式 */
    .stImage > img {
        border-radius: 6px;
        border: 1px solid var(--border-color);
    }

    body {
        color: var(--text-color);
        background-color: var(--background-color); /* Ensure body background is set */
    }

    .main {
        background-color: var(--background-color);
        padding: 1.5rem; /* Adjusted padding */
    }

    /* General Card styling (applied via st.container potentially or specific classes) */
    /* We might need to apply a class like 'stCard' manually if needed */
    .stCard, [data-testid="stExpander"], [data-testid="stMetric"], .report-section {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 188, 212, 0.1); /* Primary color glow */
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: var(--card-bg-color);
        transition: all 0.3s ease;
        color: var(--text-color); /* Ensure text color inside cards */
    }
    .stCard:hover, [data-testid="stExpander"]:hover, .report-section:hover {
         box-shadow: 0 6px 16px rgba(0, 188, 212, 0.2); /* Enhanced glow on hover */
         /* transform: translateY(-2px); Removed transform for stability */
    }

    /* Headers */
    h1, h2, h3 {
        color: var(--primary-color);
        font-weight: 600;
        text-shadow: 0 0 4px rgba(0, 188, 212, 0.3);
    }
    h1 {
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem; /* Increased margin */
    }
     h3 { /* Make h3 slightly smaller/less prominent than h2 */
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
     }
     h4, h5, h6 {
         color: var(--text-color);
         font-weight: 500;
     }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Keep header visible for consistency if expander headers are visible */
    /* header {visibility: hidden;} */

    /* Button styling */
    .stButton button {
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s ease;
        background-color: var(--primary-color);
        color: var(--background-color); /* Dark text on bright button */
        border: none;
        padding: 10px 20px;
        width: 100%; /* Make buttons fill container width by default */
    }
    .stButton button:hover {
        background-color: #00e5ff; /* Brighter cyan on hover */
        box-shadow: 0 0 15px rgba(0, 188, 212, 0.7);
        transform: scale(1.03);
    }
    .stButton button:active {
        transform: scale(0.98);
    }

    /* Input field styling */
    [data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: var(--input-bg-color);
        color: var(--text-color);
        border: 1px solid var(--border-color) !important;
        border-radius: 5px;
    }
    [data-testid="stTextInput"] label, [data-testid="stSelectbox"] label {
        color: var(--text-color-darker);
    }

    /* Dataframe styling */
    .dataframe-container, [data-testid="stDataFrame"] { /* Target both potential containers */
        width: 100% !important;
        font-size: 13px;
        border-collapse: separate;
        border-spacing: 0;
        background-color: var(--card-bg-color);
        border: 1px solid var(--border-color);
        border-radius: 6px; /* Rounded corners for dataframe */
        overflow: hidden; /* Clip content to rounded corners */
    }
    .dataframe-container table, [data-testid="stDataFrame"] table {
         width: 100%;
    }
    /* Style dataframe headers */
    .dataframe thead th, [data-testid="stDataFrame"] thead th {
        background-color: var(--primary-color);
        color: var(--background-color);
        text-align: left;
        padding: 8px 10px;
        font-weight: 600;
    }
    /* Style dataframe rows */
    .dataframe tbody tr, [data-testid="stDataFrame"] tbody tr {
        border-bottom: 1px solid #334155; /* Separator line between rows */
    }
    .dataframe tbody tr:nth-child(even), [data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background-color: #273448; /* Slightly different background for even rows */
    }
    .dataframe tbody tr:hover, [data-testid="stDataFrame"] tbody tr:hover {
        background-color: #334155; /* Highlight row on hover */
        color: var(--text-color);
    }
     .dataframe tbody td, [data-testid="stDataFrame"] tbody td {
        padding: 8px 10px;
     }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 2px; /* Ensure gap below tabs before content */
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px; /* Adjusted padding */
        border-radius: 6px 6px 0 0;
        background-color: var(--card-bg-color);
        color: var(--text-color-darker);
        border: 1px solid var(--border-color);
        border-bottom: none;
        margin-bottom: -2px;
        font-weight: 500;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
     .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: var(--background-color);
        border-color: var(--primary-color);
        font-weight: 700;
        box-shadow: 0 -3px 6px rgba(0, 188, 212, 0.2);
     }

     /* Expander styling */
    [data-testid="stExpander"] { /* Already styled like a card above */
        margin-bottom: 1rem;
    }
    [data-testid="stExpander"] header {
        background-color: transparent; /* Use container background */
        color: var(--primary-color);
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.8rem 1.5rem; /* Match card padding H */
        border-radius: 8px 8px 0 0; /* Match top corners */
        border-bottom: 1px solid var(--border-color); /* Separator when closed */
    }
     [data-testid="stExpander"][aria-expanded="true"] header {
        border-bottom: none; /* No separator when open */
     }
     [data-testid="stExpander"] .streamlit-expanderContent {
        padding: 1rem 1.5rem; /* Content padding */
     }

    /* Metric styling */
    [data-testid="stMetric"] {
         padding: 1rem; /* Slightly less padding for metrics */
         text-align: center;
    }
    [data-testid="stMetric"] label { /* Metric Label */
        color: var(--text-color-darker);
        font-size: 0.9rem;
        font-weight: 500;
    }
    [data-testid="stMetric"] div:nth-of-type(2) { /* Metric Value */
        color: var(--primary-color);
        font-size: 1.8rem;
        font-weight: 700;
    }
     [data-testid="stMetric"] p { /* Hide delta if not needed */
         display: none;
     }

     /* Info/Warning/Error boxes */
     [data-testid="stInfo"], [data-testid="stWarning"], [data-testid="stError"] {
        border-radius: 6px;
        padding: 1rem;
        margin: 1rem 0;
        border-left-width: 5px;
        border-left-style: solid;
        background-color: var(--card-bg-color); /* Match card background */
     }
     [data-testid="stInfo"] {
        border-left-color: var(--info-color);
        color: var(--info-color);
     }
     [data-testid="stWarning"] {
        border-left-color: var(--warning-color);
        color: var(--warning-color);
     }
      [data-testid="stError"] {
        border-left-color: var(--error-color);
        color: var(--error-color);
     }
     /* Ensure text inside alerts is readable */
     [data-testid="stInfo"] *, [data-testid="stWarning"] *, [data-testid="stError"] * {
        color: inherit !important;
     }


    /* Sidebar styling */
    .stSidebar {
        background-color: var(--card-bg-color);
        padding: 1.5rem;
        border-right: 1px solid var(--border-color);
    }
    .stSidebar h3 {
         color: var(--secondary-color);
         text-shadow: none;
         font-size: 1.2rem;
         margin-bottom: 0.5rem;
    }
    .stSidebar a {
         color: var(--info-color);
         text-decoration: none;
         transition: color 0.3s ease;
    }
     .stSidebar a:hover {
          color: var(--primary-color);
     }
     .stSidebar .stRadio > label { /* Style radio buttons in sidebar if any */
        color: var(--text-color);
        padding-bottom: 0.5rem;
     }

     /* Report Headers in stock_analysis.py */
     .report-header {
        font-size: 1.4rem; /* Use rem for scalability */
        font-weight: bold;
        margin-top: 1.5em;
        padding: 10px 0;
        border-bottom-width: 2px;
        border-bottom-style: solid;
     }
    .report-header-sentiment { color: #3498DB; border-bottom-color: #3498DB; }
    .report-header-technical { color: #2ECC71; border-bottom-color: #2ECC71; }
    .report-header-fundamentals { color: #9B59B6; border-bottom-color: #9B59B6; }
    .report-header-adversarial { color: #E74C3C; border-bottom-color: #E74C3C; }
    .report-header-default { color: #D35400; border-bottom-color: #D35400; }

    /* Add spacing after report content */
    .report-content {
        margin-bottom: 1.5rem;
    }

</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# 初始化 session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = ""

# 主页面内容
st.title("📊 智能股票分析系统")

# 添加Logo和导航栏样式的容器
col_logo, col_nav = st.columns([1, 4])
with col_logo:
    st.image("sources/icon/image_fx_-2.jpg", width=100)

# 项目简介 - 使用卡片样式
with st.container():
    st.markdown("""
    ## 📌 项目简介
    这是一个基于 LLMs 的智能股票分析系统，利用多个专业 Agent 来分析中国 A 股市场。

    ### 🎯 主要功能
    - **市场热点追踪**: 实时获取市场热点信息和相关概念股
    - **个股智能分析**: 提供技术面分析和投资建议
    """)

# 技术架构和数据分析维度 - 使用双列布局
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown("""
        ### 🔧 技术架构
        - 前端：Streamlit
        - AI模型：GPT-4 & Gemini Pro
        - Agent框架：LangChain
        - 数据来源：多个金融数据API
        """)

with col2:
    with st.container():
        st.markdown("""
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

# 在主页面添加使用说明 - 使用卡片样式
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
