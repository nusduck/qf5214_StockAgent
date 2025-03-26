import os
from typing import Any
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent

from core.model import LanguageModelManager
from core.state import StockAnalysisState
from helpers.logger import setup_logger
from helpers.prompt import adversarial_prompt  


state = StockAnalysisState()
state.basic_info.stock_name = "贵州茅台"

state.report_state.text_reports["sentiment"] = "This is a sentiment report."
state.report_state.text_reports["fundamental"] = "This is a financial report."
state.report_state.text_reports["technical"] = "This is a technical report."

def create_adversarial_agent(state: StockAnalysisState) -> Any:
    """
    创建对抗性分析 Agent，输入为三份分析报告，输出批判性总结。
    """
    logger = setup_logger("adversarial_agent.log")
    llm = LanguageModelManager().get_models()["llm_oai_o3"]

    # 读取已有报告内容
    sentiment = state.report_state.text_reports.get("sentiment_report", "无情绪分析")
    fundamental = state.report_state.text_reports.get("fundamental_report", "无基本面分析")
    technical = state.report_state.text_reports.get("technical_report", "无技术面分析")

    # 构建 Prompt
    prompt = adversarial_prompt.format(
    sentiment_report=sentiment,
    fundamental_report=fundamental,
    technical_report=technical
    )


    logger.info("✅ 对抗性分析 Agent 已创建")
    return create_react_agent(llm, tools=[], prompt=prompt)