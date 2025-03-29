import os
import sys
import logging
import json
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 导入所需模块
from tools.stock_a_indicator_tools import analyze_stock_indicators
from core.state import StockAnalysisState
from agents.fundamentals_agent import create_fundamentals_agent

# 测试完整流程
def test_full_workflow():
    # 1. 创建状态并设置基本信息
    logger.info("1. 创建状态对象...")
    state = StockAnalysisState()
    state.update_stock_info("000001", "平安银行", "银行")
    
    # 模拟一些新闻数据
    news_data = {"content": "平安银行发布2024年第一季度业绩报告，营收和利润均有所增长。"}
    state.update_news_data(news_data)
    
  # 2. 获取交易指标数据
    logger.info("2. 获取交易指标数据...")
    indicator_data = analyze_stock_indicators.run({
     "symbol": "000001",
     "start_date": "20240101",
     "end_date": "20240331"
     })
    logger.info(f"获取到指标数据: {len(indicator_data)}行")
    
    # 3. 保存数据到状态
    logger.info("3. 保存数据到状态...")
    state.update_indicator_data(indicator_data)
    
    # 4. 检查agent提取数据的过程
    logger.info("4. 检查从状态提取数据的过程...")
    
    # 手动执行一下提取逻辑，类似于create_fundamentals_agent内部的逻辑
    indicator_metrics = {}
    if hasattr(state.financial_data, 'indicator_data') and state.financial_data.indicator_data is not None:
        ind_data = state.financial_data.indicator_data
        
        if isinstance(ind_data, pd.DataFrame) and not ind_data.empty:
            # 获取最新的一行数据（按trade_date排序后的第一行）
            if 'trade_date' in ind_data.columns:
                ind_data = ind_data.sort_values('trade_date', ascending=False)
            indicator_metrics = ind_data.iloc[0].to_dict()
            
            # 打印提取的指标数据
            logger.info(f"提取的交易指标: {json.dumps({k: str(v) for k, v in indicator_metrics.items()}, indent=2)}")
    
    # 5. 创建agent并验证
    logger.info("5. 创建fundamentals_agent...")
    try:
        agent = create_fundamentals_agent(state)
        logger.info("Agent创建成功")
    except Exception as e:
        logger.error(f"创建Agent失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

# 执行测试
if __name__ == "__main__":
    import pandas as pd
    test_full_workflow()