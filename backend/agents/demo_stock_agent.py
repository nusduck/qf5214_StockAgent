from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from .base import BaseAgent
# from tools.demo_stock_tools import get_company_info, get_trading_data, get_financial_data
from tools.company_info_tools import analyze_company_info
from tools.tech1_tools import analyze_stock_technical
from langgraph.checkpoint.memory import MemorySaver

class StockAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="股票分析师",
            tools=[analyze_company_info]
        )
    
    def _create_executor(self):
        # Option 1: Using system message directly
        system_message = """你是一个专业的股票分析师。使用提供的工具来分析公司信息。
                         请分别获取并分析公司基本信息、交易数据和财务指标。
                         将所有信息整合成结构化的分析报告。"""
        
        # Option 2: Using hub prompt template
        # prompt = hub.pull("hwchase17/react")
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
        
        # Create memory checkpointer for persistence
        memory = MemorySaver()
        
        # Create the LangGraph agent
        agent_executor = create_react_agent(
            llm, 
            self.tools,
            prompt=system_message,
            checkpointer=memory
        )
        
        # Configure timeout and recursion limits
        agent_executor.step_timeout = 60  # 60 second timeout per step
        
        return agent_executor

    def analyze(self, input_data: dict) -> str:
        # Convert input to messages format expected by LangGraph
        messages = [("human", input_data["input"])]
        
        # Configure execution parameters
        config = {
            "recursion_limit": 10,  # Similar to max_iterations
            "configurable": {
                "thread_id": input_data.get("thread_id", "default")
            }
        }
        
        try:
            # Execute the agent and get final messages
            result = self.executor.invoke({"messages": messages}, config)
            # Return the last assistant message
            return result["messages"][-1].content
        except Exception as e:
            return f"Analysis failed: {str(e)}"

class TechnicalAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="技术分析师",
            tools=[analyze_stock_technical]
        )
    
    def _create_executor(self):
        system_message = "你是一个专业的技术分析师，请查看所有数据，专注于分析股票的技术指标和走势并给出相关建议。"
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
        
        memory = MemorySaver()
        
        agent_executor = create_react_agent(
            llm,
            self.tools,
            prompt=system_message,
            checkpointer=memory
        )
        
        agent_executor.step_timeout = 60
        
        return agent_executor

    def analyze(self, input_data: dict) -> str:
        messages = [("human", input_data["input"])]
        
        config = {
            "recursion_limit": 10,
            "configurable": {
                "thread_id": input_data.get("thread_id", "default")
            }
        }
        
        try:
            result = self.executor.invoke({"messages": messages}, config)
            return result["messages"][-1].content
        except Exception as e:
            return f"Technical analysis failed: {str(e)}"
