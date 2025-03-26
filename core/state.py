from typing import Dict, Any, Optional, List, Annotated
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, Field
from operator import add


class StockDataState(BaseModel):
    """股票数据状态基类"""
    last_updated: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class BasicInfo(StockDataState):
    """基础信息状态"""
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    industry: Optional[str] = None
    company_info: Optional[pd.DataFrame] = None

class MarketData(StockDataState):
    """市场交易数据状态"""
    trade_data: Optional[pd.DataFrame] = None  # from individual_stock_tools
    sector_data: Optional[pd.DataFrame] = None  # from sector_tools
    technical_data: Optional[pd.DataFrame] = None  # from tech2_tools

class FinancialData(StockDataState):
    """财务数据状态"""
    financial_data: Optional[pd.DataFrame] = None  # from finance_info_tools
    
class ResearchData(StockDataState):
    """研究数据状态"""
    analyst_data: Optional[pd.DataFrame] = None  # from analyst_tools
    news_data: Optional[Dict[str, Any]] = None  # from stock_news_tools

class ReportState(StockDataState):
    """分析报告状态"""
    text_reports: Dict[str, str] = Field(default_factory=dict)  # 文本报告
    charts: Dict[str, str] = Field(default_factory=dict)  # 图表路径
    attachments: Dict[str, str] = Field(default_factory=dict)  # 附件路径

class StockAnalysisState(BaseModel):
    """股票分析完整工作流状态"""
    
    # 工作流控制
    current_step: str = Field(default="init", description="当前执行步骤")
    completed_steps: List[str] = Field(default_factory=list, description="已完成步骤")
    messages: List[Any] = Field(default_factory=list, description="消息历史")
    
    # 数据状态
    basic_info: BasicInfo = Field(default_factory=BasicInfo, description="基础信息")
    market_data: MarketData = Field(default_factory=MarketData, description="市场交易数据")
    financial_data: FinancialData = Field(default_factory=FinancialData, description="财务数据")
    research_data: ResearchData = Field(default_factory=ResearchData, description="研究数据")
    report_state: ReportState = Field(default_factory=ReportState, description="报告状态")
    data_file_paths: Dict[str, str] = Field(default_factory=dict, description="数据文件路径")
    
    # 数据可视化属性
    visualization_paths: Annotated[List[str],add] = Field(default_factory=list, description="可视化图表路径")
    graph_description: Annotated[List[str], add] = Field(default_factory=list, description="图表描述")
    
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        # First initialize the parent class (BaseModel)
        super().__init__(**kwargs)
        
        # Then initialize our attributes if they haven't been set
        if not hasattr(self, 'current_step'):
            self.current_step = "init"
        if not hasattr(self, 'completed_steps'):
            self.completed_steps = []
        if not hasattr(self, 'messages'):
            self.messages = []
        if not hasattr(self, 'basic_info'):
            self.basic_info = BasicInfo()
        if not hasattr(self, 'market_data'):
            self.market_data = MarketData()
        if not hasattr(self, 'financial_data'):
            self.financial_data = FinancialData()
        if not hasattr(self, 'research_data'):
            self.research_data = ResearchData()
        if not hasattr(self, 'report_state'):
            self.report_state = ReportState()

    def update_stock_info(self, stock_code: str, stock_name: str, industry: str) -> None:
        """更新股票基本信息"""
        self.basic_info.stock_code = stock_code
        self.basic_info.stock_name = stock_name
        self.basic_info.industry = industry
        self.basic_info.last_updated = datetime.now()

    def update_company_info(self, data: pd.DataFrame) -> None:
        """更新公司信息"""
        self.basic_info.company_info = data
        self.basic_info.last_updated = datetime.now()

    def update_trade_data(self, data: pd.DataFrame) -> None:
        """更新交易数据"""
        self.market_data.trade_data = data
        self.market_data.last_updated = datetime.now()

    def update_financial_data(self, data: pd.DataFrame) -> None:
        """更新财务数据"""
        self.financial_data.financial_data = data
        self.financial_data.last_updated = datetime.now()

    def update_technical_data(self, data: pd.DataFrame) -> None:
        """更新技术分析数据"""
        self.market_data.technical_data = data
        self.market_data.last_updated = datetime.now()

    def update_analyst_data(self, data: pd.DataFrame) -> None:
        """更新分析师数据"""
        self.research_data.analyst_data = data
        self.research_data.last_updated = datetime.now()

    def update_sector_data(self, data: pd.DataFrame) -> None:
        """更新板块数据"""
        self.market_data.sector_data = data
        self.market_data.last_updated = datetime.now()

    def update_news_data(self, data: Dict[str, Any]) -> None:
        """更新新闻数据"""
        self.research_data.news_data = data
        self.research_data.last_updated = datetime.now()

    def add_report(self, report_type: str, content: str) -> None:
        """添加分析报告"""
        self.report_state.text_reports[report_type] = content
        self.report_state.last_updated = datetime.now()

    def add_chart(self, chart_name: str, file_path: str) -> None:
        """添加图表"""
        self.report_state.charts[chart_name] = file_path
        self.report_state.last_updated = datetime.now()

    def set_error(self, component: str, error_msg: str) -> None:
        """设置错误信息"""
        if hasattr(self, component):
            getattr(self, component).error_message = error_msg
            getattr(self, component).last_updated = datetime.now()

    def clear_error(self, component: str) -> None:
        """清除错误信息"""
        if hasattr(self, component):
            getattr(self, component).error_message = None
            getattr(self, component).last_updated = datetime.now()
            
    def add_data_file_path(self, data_type: str, file_path: str) -> None:
        """添加数据文件路径"""
        self.data_file_paths[data_type] = file_path

    def add_visualization(self, path: str) -> None:
        """添加可视化图表路径"""
        self.visualization_paths.append(path)

    def add_description(self, description: str) -> None:
        """添加图表描述"""
        self.graph_description.append(description)

    def to_dict(self) -> Dict[str, Any]:
        """将状态转换为字典格式"""
        return {
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "basic_info": {
                "stock_code": self.basic_info.stock_code,
                "stock_name": self.basic_info.stock_name,
                "industry": self.basic_info.industry,
                "company_info": self.basic_info.company_info.to_dict() if self.basic_info.company_info is not None else None,
            },
            "market_data": {
                "trade_data": self.market_data.trade_data.to_dict() if self.market_data.trade_data is not None else None,
                "sector_data": self.market_data.sector_data.to_dict() if self.market_data.sector_data is not None else None,
                "technical_data": self.market_data.technical_data.to_dict() if self.market_data.technical_data is not None else None,
            },
            "financial_data": {
                "financial_data": self.financial_data.financial_data.to_dict() if self.financial_data.financial_data is not None else None,
            },
            "research_data": {
                "analyst_data": self.research_data.analyst_data.to_dict() if self.research_data.analyst_data is not None else None,
                "news_data": self.research_data.news_data,
            },
            "report_state": {
                "text_reports": self.report_state.text_reports,
                "charts": self.report_state.charts,
                "attachments": self.report_state.attachments,
            },
            "data_file_paths": self.data_file_paths,
            "visualization_paths": self.visualization_paths,
            "graph_description": self.graph_description
        }


