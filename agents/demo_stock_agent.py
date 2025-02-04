from langchain.agents import AgentExecutor, create_openai_tools_agent, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent
from tools.demo_stock_tools import get_company_info, get_trading_data, get_financial_data
from tools.tech_indictator_tools import analyze_stock_technical


class StockAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="股票分析师",
            tools=[get_company_info, get_trading_data, get_financial_data]
        )
    
    def _create_executor(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的股票分析师。使用提供的工具来分析公司信息。
                         请分别获取并分析公司基本信息、交易数据和财务指标。
                         将所有信息整合成结构化的分析报告。"""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        # agent = create_openai_tools_agent(llm, self.tools, prompt)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro",temperature=0)
        agent = create_tool_calling_agent(llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def analyze(self, input_data: dict) -> str:
        result = self.executor.invoke(input_data)
        return result["output"]

class TechnicalAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="技术分析师",
            tools=[analyze_stock_technical]
        )
    
    def _create_executor(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的技术分析师，请查看所有数据，专注于分析股票的技术指标和走势并给出相关建议。"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        # agent = create_openai_tools_agent(llm, self.tools, prompt)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro",temperature=0)
        agent = create_tool_calling_agent(llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def analyze(self, input_data: dict) -> str:
        result = self.executor.invoke(input_data)
        return result["output"]
