from typing import List, Dict, Any
from langgraph.prebuilt import create_react_agent
import pandas as pd
from datetime import datetime

from core.model import LanguageModelManager
from core.state import StockAnalysisState
from helpers.logger import setup_logger
from helpers.prompt import make_system_prompt
from tools.company_info_tools import analyze_company_info
from tools.stock_news_tools import get_stock_news
from tools.stock_info_tools import analyze_stock_info
from tools.sector_tools import get_stock_sector_data
from tools.individual_stock_tools import get_stock_trade_data
from tools.finance_info_tools import analyze_stock_financial
from tools.analyst_tools import get_analyst_data_tool
from tools.tech1_tools import analyze_stock_technical

class DataCollectAgent:
    """数据收集代理，负责收集数据并更新状态"""
    
    def __init__(self, state: StockAnalysisState):
        self.state = state
        self.logger = setup_logger()
        self.model_manager = LanguageModelManager()
        self.llm = self.model_manager.get_llm("llm_google_flash")
        
        # 工具到状态更新方法的映射
        self.tool_state_mapping = {
            'analyze_company_info': self._update_company_info,
            'analyze_stock_info': self._update_stock_info,
            'get_stock_trade_data': self._update_trade_data,
            'analyze_stock_financial': self._update_financial_data,
            'analyze_stock_technical': self._update_technical_data,
            'get_analyst_data_tool': self._update_analyst_data,
            'get_stock_sector_data': self._update_sector_data,
            'get_stock_news': self._update_news_data
        }
        
        # 初始化agent
        self.agent = self._create_agent()

    def _create_agent(self):
        """创建ReAct agent"""
        tools = [
            analyze_company_info,
            get_stock_news,
            analyze_stock_info,
            get_stock_sector_data,
            get_stock_trade_data,
            analyze_stock_financial,
            get_analyst_data_tool,
            analyze_stock_technical
        ]
        
        system_prompt = """你是一个专业的数据收集助手。你的任务是：
        1. 使用所有可用的工具收集给定股票的完整数据
        2. 确保每个工具都被正确调用并获取数据
        3. 按照工具的返回结果更新状态
        4. 如果任何工具调用失败，记录错误信息
        
        请按照以下顺序收集数据：
        1. 首先获取基本信息（公司信息和股票信息）
        2. 然后获取市场数据（交易数据、板块数据和技术数据）
        3. 接着获取财务数据
        4. 最后获取研究数据（分析师报告和新闻）
        """
        
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            system_message=make_system_prompt(system_prompt)
        )
        
        self.logger.info("Data collect agent created successfully.")
        return agent

    def _update_company_info(self, data: pd.DataFrame) -> None:
        self.state.update_company_info(data)
        self.logger.info("Company info updated")

    def _update_stock_info(self, data: pd.DataFrame) -> None:
        self.state.basic_info.stock_info = data
        self.state.basic_info.last_updated = datetime.now()
        self.logger.info("Stock info updated")

    def _update_trade_data(self, data: pd.DataFrame) -> None:
        self.state.update_trade_data(data)
        self.logger.info("Trade data updated")

    def _update_financial_data(self, data: pd.DataFrame) -> None:
        self.state.update_financial_data(data)
        self.logger.info("Financial data updated")

    def _update_technical_data(self, data: pd.DataFrame) -> None:
        self.state.update_technical_data(data)
        self.logger.info("Technical data updated")

    def _update_analyst_data(self, data: pd.DataFrame) -> None:
        self.state.update_analyst_data(data)
        self.logger.info("Analyst data updated")

    def _update_sector_data(self, data: pd.DataFrame) -> None:
        self.state.update_sector_data(data)
        self.logger.info("Sector data updated")

    def _update_news_data(self, data: Dict[str, Any]) -> None:
        self.state.update_news_data(data)
        self.logger.info("News data updated")

    def _handle_tool_output(self, tool_name: str, output: Any) -> None:
        """处理工具输出并更新相应状态"""
        if tool_name in self.tool_state_mapping:
            try:
                self.tool_state_mapping[tool_name](output)
            except Exception as e:
                error_msg = f"Error updating state for {tool_name}: {str(e)}"
                self.logger.error(error_msg)
                self.state.set_error(tool_name, error_msg)

    async def collect_data(self, stock_code: str) -> StockAnalysisState:
        """收集指定股票的所有数据并更新状态"""
        try:
            self.state.current_step = "data_collection"
            
            # 构建输入消息
            input_message = f"""请收集股票代码 {stock_code} 的所有相关数据，包括：
            1. 公司基本信息
            2. 股票交易数据
            3. 财务数据
            4. 技术分析数据
            5. 行业数据
            6. 分析师报告
            7. 相关新闻
            
            请确保使用所有可用的工具来获取完整的数据集。"""
            
            # 执行agent
            result = await self.agent.ainvoke(
                {"messages": [("human", input_message)]}
            )
            
            # 处理agent的输出，更新状态
            for action in result.get("intermediate_steps", []):
                tool_name = action[0].tool
                tool_output = action[1]
                self._handle_tool_output(tool_name, tool_output)
            
            self.state.completed_steps.append("data_collection")
            self.logger.info(f"Data collection completed for stock {stock_code}")
            
            return self.state
            
        except Exception as e:
            error_msg = f"Data collection failed: {str(e)}"
            self.logger.error(error_msg)
            self.state.set_error("data_collection", error_msg)
            raise

# 使用示例
async def collect_stock_data(stock_code: str) -> StockAnalysisState:
    """收集股票数据的便捷函数"""
    state = StockAnalysisState()
    agent = DataCollectAgent(state)
    return await agent.collect_data(stock_code)
