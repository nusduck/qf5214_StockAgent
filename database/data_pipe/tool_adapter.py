#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LangGraph 工具适配器
将现有工具包装为 LangGraph 兼容格式
"""

import importlib
import inspect
from functools import wraps

class ToolAdapter:
    """工具适配器类，将普通工具函数包装成支持invoke方法的格式"""
    
    def __init__(self, module_name):
        self.module = importlib.import_module(module_name)
        self.module_name = module_name
        self._functions = {}
        
        # 自动发现并注册所有公共函数
        for name, obj in inspect.getmembers(self.module):
            if inspect.isfunction(obj) and not name.startswith('_'):
                self._functions[name] = obj
    
    def invoke(self, function_name, **kwargs):
        """调用指定的工具函数"""
        if function_name not in self._functions:
            raise ValueError(f"函数 '{function_name}' 在模块 '{self.module_name}' 中不存在")
        
        func = self._functions[function_name]
        return func(**kwargs)
    
    def __getattr__(self, name):
        """允许直接通过属性访问函数"""
        if name in self._functions:
            return self._functions[name]
        raise AttributeError(f"'{self.__class__.__name__}' 对象没有 '{name}' 属性")

# 创建工具适配器实例
stock_info_adapter = ToolAdapter('tools.stock_info_tools')
finance_info_adapter = ToolAdapter('tools.finance_info_tools')
stock_news_adapter = ToolAdapter('tools.stock_news_tools')
sector_adapter = ToolAdapter('tools.sector_tools')
company_info_adapter = ToolAdapter('tools.company_info_tools')
individual_stock_adapter = ToolAdapter('tools.individual_stock_tools')
analyst_adapter = ToolAdapter('tools.analyst_tools')
tech1_adapter = ToolAdapter('tools.tech1_tools')
tech2_adapter = ToolAdapter('tools.tech2_tools') 