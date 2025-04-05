#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LangGraph 工具适配器
将现有工具包装为 LangGraph 兼容格式
"""

import importlib
import inspect
import sys
import os
from functools import wraps

# Add project root to sys.path to make tools package importable
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(project_root)

# Import the tools directly to ensure they exist
try:
    from tools import finance_info_tools
    from tools import stock_news_tools
    from tools import sector_tools
    from tools import company_info_tools
    from tools import individual_stock_tools
    from tools import analyst_tools
    from tools import tech1_tools
    from tools import tech2_tools
    from tools import stock_a_indicator_tools
    
    # Print available functions for debugging
    print("Available functions in stock_info_tools:", [f for f in dir(company_info_tools) if callable(getattr(company_info_tools, f)) and not f.startswith("_")])
except ImportError as e:
    print(f"Import error: {e}")
    print("Creating fallback module structures to allow execution...")
    
    # Create fallback empty modules
    class EmptyModule:
        def __init__(self, name):
            self.__name__ = name
            
        def __getattr__(self, name):
            def empty_func(*args, **kwargs):
                print(f"[WARNING] Called {self.__name__}.{name}, but module is not available")
                return None
            return empty_func
    
    finance_info_tools = EmptyModule("finance_info_tools")
    stock_news_tools = EmptyModule("stock_news_tools")
    sector_tools = EmptyModule("sector_tools")
    company_info_tools = EmptyModule("company_info_tools")
    individual_stock_tools = EmptyModule("individual_stock_tools")
    analyst_tools = EmptyModule("analyst_tools")
    tech1_tools = EmptyModule("tech1_tools")
    tech2_tools = EmptyModule("tech2_tools") 
    stock_a_indicator_tools = EmptyModule("stock_a_indicator_tools")

class ToolAdapter:
    """工具适配器类，将普通工具函数包装成支持invoke方法的格式"""
    
    def __init__(self, module):
        self.module = module
        self.module_name = module.__name__ if hasattr(module, "__name__") else str(module)
        self._functions = {}
        
        # 自动发现并注册所有公共函数
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith('_'):
                self._functions[name] = obj
    
    def invoke(self, function_name, **kwargs):
        """调用指定的工具函数"""
        if function_name not in self._functions:
            # 如果找不到指定的函数，尝试找到可能的替代函数
            available_funcs = list(self._functions.keys())
            if available_funcs:
                # 选择第一个可用函数
                alt_func_name = available_funcs[0]
                print(f"[WARNING] Function '{function_name}' not found in '{self.module_name}', using '{alt_func_name}' instead")
                function_name = alt_func_name
            else:
                raise ValueError(f"No available functions in module '{self.module_name}'")
        
        func = self._functions[function_name]
        return func(**kwargs)
    
    def __getattr__(self, name):
        """允许直接通过属性访问函数"""
        if name in self._functions:
            return self._functions[name]
        raise AttributeError(f"'{self.__class__.__name__}' 对象没有 '{name}' 属性")

# 创建工具适配器实例 - 使用直接导入的模块
finance_info_adapter = ToolAdapter(finance_info_tools)
stock_news_adapter = ToolAdapter(stock_news_tools)
sector_adapter = ToolAdapter(sector_tools)
company_info_adapter = ToolAdapter(company_info_tools)
individual_stock_adapter = ToolAdapter(individual_stock_tools)
analyst_adapter = ToolAdapter(analyst_tools)
tech1_adapter = ToolAdapter(tech1_tools)
tech2_adapter = ToolAdapter(tech2_tools)
stock_a_indicator_adapter = ToolAdapter(stock_a_indicator_tools)


