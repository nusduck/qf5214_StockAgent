from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, Field

class StockAnalysisState(BaseModel):
    """State class for stock analysis workflow"""
    
    # 基础信息
    stock_code: Optional[str] = Field(default=None, description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")
    
    # 公司基本信息 (来自 company_info_tools)
    company_info: Optional[pd.DataFrame] = Field(default=None, description="公司基本信息")
    
    # 股票基本信息 (来自 stock_info_tools)
    stock_info: Optional[pd.DataFrame] = Field(default=None, description="股票基本信息")
    
    # 交易数据 (来自 individual_stock_tools)
    trade_data: Optional[pd.DataFrame] = Field(default=None, description="股票交易数据")
    
    # 财务数据 (来自 finance_info_tools)
    financial_data: Optional[pd.DataFrame] = Field(default=None, description="财务数据")
    
    # 技术分析数据 (来自 tech1_tools)
    technical_data: Optional[pd.DataFrame] = Field(default=None, description="技术分析数据")
    
    # 分析师数据 (来自 analyst_tools)
    analyst_data: Optional[pd.DataFrame] = Field(default=None, description="分析师跟踪数据")
    
    # 板块数据 (来自 sector_tools)
    sector_data: Optional[pd.DataFrame] = Field(default=None, description="板块数据")
    
    # 新闻数据 (来自 stock_news_tools)
    news_data: Optional[Dict[str, Any]] = Field(default=None, description="新闻数据")
    
    # 工作流程控制
    current_step: str = Field(default="init", description="当前执行步骤")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")

    class Config:
        arbitrary_types_allowed = True

    def update_stock_info(self, stock_code: str, stock_name: str) -> None:
        """更新股票基本信息"""
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.last_updated = datetime.now()

    def update_company_info(self, data: pd.DataFrame) -> None:
        """更新公司信息"""
        self.company_info = data
        self.last_updated = datetime.now()

    def update_trade_data(self, data: pd.DataFrame) -> None:
        """更新交易数据"""
        self.trade_data = data
        self.last_updated = datetime.now()

    def update_financial_data(self, data: pd.DataFrame) -> None:
        """更新财务数据"""
        self.financial_data = data
        self.last_updated = datetime.now()

    def update_technical_data(self, data: pd.DataFrame) -> None:
        """更新技术分析数据"""
        self.technical_data = data
        self.last_updated = datetime.now()

    def update_analyst_data(self, data: pd.DataFrame) -> None:
        """更新分析师数据"""
        self.analyst_data = data
        self.last_updated = datetime.now()

    def update_sector_data(self, data: pd.DataFrame) -> None:
        """更新板块数据"""
        self.sector_data = data
        self.last_updated = datetime.now()

    def update_news_data(self, data: Dict[str, Any]) -> None:
        """更新新闻数据"""
        self.news_data = data
        self.last_updated = datetime.now()

    def set_error(self, error_msg: str) -> None:
        """设置错误信息"""
        self.error_message = error_msg
        self.last_updated = datetime.now()

    def clear_error(self) -> None:
        """清除错误信息"""
        self.error_message = None
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """将状态转换为字典格式"""
        return {
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "company_info": self.company_info.to_dict() if self.company_info is not None else None,
            "stock_info": self.stock_info.to_dict() if self.stock_info is not None else None,
            "trade_data": self.trade_data.to_dict() if self.trade_data is not None else None,
            "financial_data": self.financial_data.to_dict() if self.financial_data is not None else None,
            "technical_data": self.technical_data.to_dict() if self.technical_data is not None else None,
            "analyst_data": self.analyst_data.to_dict() if self.analyst_data is not None else None,
            "sector_data": self.sector_data.to_dict() if self.sector_data is not None else None,
            "news_data": self.news_data,
            "current_step": self.current_step,
            "error_message": self.error_message,
            "last_updated": self.last_updated.isoformat()
        }
