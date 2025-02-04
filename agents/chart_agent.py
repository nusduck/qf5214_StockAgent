from langchain.agents import AgentExecutor, create_openai_tools_agent,create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent
from tools.chart_tools import create_technical_chart, create_combined_chart
from typing import List, Dict, Any

class ChartExpertAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="金融绘图专家",
            tools=[create_technical_chart, create_combined_chart]
        )
    
    def _create_executor(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的金融图表分析专家。
                         你的任务是分析技术指标数据，并决定需要绘制哪些图表来最好地展示市场走势和信号。
                         
                         在分析数据时，请考虑：
                         1. 当前市场趋势是否明显
                         2. 是否存在重要的技术信号
                         3. 哪些指标组合可以更好地说明问题
                         
                         请使用提供的工具来创建专业的技术分析图表。"""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        agent = create_openai_tools_agent(llm, self.tools, prompt)
        # llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro",temperature=0)
        # agent = create_tool_calling_agent(llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def analyze(self, input_data: Dict[str, Any]) -> str:
        """实现基类要求的analyze方法"""
        return self.analyze_and_plot(input_data)
    
    def analyze_and_plot(self, technical_data: dict) -> List[Dict[str, Any]]:
        """分析技术数据并生成相应的图表"""
        result = self.executor.invoke({
            "input": f"""
                请分析以下技术数据并创建合适的图表。
                
                可用的图表类型包括：
                1. K线图 - 展示股票价格走势
                2. MACD - 展示趋势和动量
                3. RSI - 展示超买超卖
                4. KDJ - 展示价格动量
                5. 成交量 - 展示交易活跃度
                
                请按照以下步骤进行：
                1. 创建K线图展示基本走势
                2. 创建MACD、RSI等技术指标图
                3. 创建一个包含K线、MACD和RSI的组合图表
                
                技术数据：{technical_data}
            """
        })
        return result["output"] 