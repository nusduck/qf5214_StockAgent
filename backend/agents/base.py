from typing import List, Dict, Any
from abc import ABC, abstractmethod
from langchain.agents import AgentExecutor
from langchain_core.tools import BaseTool

class BaseAgent(ABC):
    def __init__(self, name: str, tools: List[BaseTool]):
        self.name = name
        self.tools = tools
        self.executor = self._create_executor()
    
    @abstractmethod
    def _create_executor(self) -> AgentExecutor:
        """创建具体的Agent执行器"""
        pass
    
    @abstractmethod
    def analyze(self, input_data: Dict[str, Any]) -> str:
        """执行分析任务"""
        pass
