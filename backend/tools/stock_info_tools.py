import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from typing import Dict, Any
import numpy as np
import time
from requests.exceptions import RequestException, Timeout
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyInput(BaseModel):
    """Stock company input parameters"""
    symbol: str = Field(description="股票代码")

def retry_on_network_error(func, max_retries=3, delay=2):
    """重试装饰器"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except (RequestException, Timeout) as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"网络请求失败，尝试重试 {attempt + 1}/{max_retries}")
                time.sleep(delay)
        return None
    return wrapper

@tool(args_schema=CompanyInput)
def analyze_stock_info(symbol: str) -> Dict[str, Any]:
    """分析股票基本信息。
    
    Args:
        symbol: 股票代码
        
    Returns:
        包含股票基本信息的字典
    """
    try:
        logger.info(f"开始获取股票 {symbol} 的信息")
        
        # 验证股票代码格式
        if not symbol.isdigit() or len(symbol) != 6:
            raise ValueError("无效的股票代码格式，应为6位数字")

        # 使用重试机制获取数据
        @retry_on_network_error
        def fetch_stock_info():
            return ak.stock_individual_info_em(symbol=symbol)

        company_info = fetch_stock_info()
        
        if company_info is None or company_info.empty:
            raise ValueError(f"未找到股票 {symbol} 的信息")
    
        # 定义字段映射关系
        field_mapping = {
            '股票代码': 'stock_code',
            '股票简称': 'stock_name',
            '总市值': 'total_market_cap',
            '流通市值': 'float_market_cap',
            '总股本': 'total_shares',
            '流通股': 'float_shares',
            '行业': 'industry',
            '上市时间': 'ipo_date'
        }
        
        # 创建结果字典
        result = {}
        for index, row in company_info.iterrows():
            if row['item'] in field_mapping:
                value = row['value']
                # 处理数值类型
                if isinstance(value, (np.int64, np.float64)):
                    value = float(value)
                result[field_mapping[row['item']]] = value
        
        # 添加时间戳
        result['snapshot_time'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"成功获取股票 {symbol} 的信息")
        return result
        
    except (RequestException, Timeout) as e:
        logger.error(f"网络请求失败: {str(e)}")
        raise ValueError(f"网络连接超时，请稍后重试: {str(e)}")
    except Exception as e:
        logger.error(f"获取股票信息失败: {str(e)}")
        raise ValueError(f"获取股票信息失败: {str(e)}")

# 示例调用
if __name__ == "__main__":
    try:
        symbol = "600519"
        logger.info(f"测试获取股票 {symbol} 的信息")
        result = analyze_stock_info.invoke({"symbol": symbol})
        print(result)
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")