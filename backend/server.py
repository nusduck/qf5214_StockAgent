import os
from dotenv import load_dotenv

# 确保在导入任何依赖模块之前加载.env文件
load_dotenv()  
print(f"OpenAI API密钥是否存在: {'是' if os.getenv('OPENAI_API_KEY') else '否'}")
print(f"API密钥前缀: {os.getenv('OPENAI_API_KEY')[:5]}..." if os.getenv('OPENAI_API_KEY') else "无API密钥")

from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from core.workflow import run_stock_analysis
from helpers.utility import convert_numpy_types, dataframe_to_json_friendly
import asyncio
import traceback
from helpers.logger import setup_logger
import uuid
import time
import json
import threading
from pathlib import Path
import mimetypes
from PIL import Image
import io
from utils.cache import RedisCache, cached
from config.settings import REDIS_CACHE_TTL

# 设置日志记录器
logger = setup_logger("api_server.log")

# 初始化Redis缓存
cache = RedisCache()
if cache.available:
    logger.info("成功连接到Redis服务器")
else:
    logger.warning("Redis缓存不可用，将不会使用缓存功能")

app = FastAPI(title="Stock Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建静态文件目录用于提供图片访问
os.makedirs("database/data", exist_ok=True)
os.makedirs("database/cache", exist_ok=True)  # 添加缓存目录
app.mount("/static", StaticFiles(directory="database"), name="static")

# 在应用启动时检查并创建必要的目录结构
def ensure_directories_exist():
    """确保所有必要的目录结构存在"""
    dirs = [
        "database/data",
        "database/cache",
        "database/task_store"
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"确保目录存在: {dir_path}")

# 应用启动时执行
ensure_directories_exist()

class WorkflowRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str

class HotspotRequest(BaseModel):
    keywords: List[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class StockAnalysisRequest(BaseModel):
    company_name: str
    stock_code: Optional[str] = None  # 可选股票代码
    analysis_type: str = "综合分析"  # 可选值: "技术面分析", "基本面分析", "综合分析"
    force_refresh: bool = False  # 是否强制刷新，忽略缓存

# 修改task_store的定义，使用更持久的存储方案
# 用于存储任务状态和结果的内存存储
# 实际应用中可替换为Redis等分布式存储
task_store = {}
TASK_STORE_FILE = "database/task_store.json"

# 首先定义TaskStatus类，然后再定义load_task_store函数
class TaskStatus:
    """任务状态跟踪类"""
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.status = "pending"  # pending, processing, completed, failed
        self.progress = 0  # 0-100
        self.message = "任务已创建，等待处理"
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.stage = "初始化"
        self.stock_code = None  # 添加股票代码字段，用于缓存查询
        
    def update(self, status=None, progress=None, message=None, result=None, error=None, stage=None, stock_code=None):
        """更新任务状态"""
        if status:
            self.status = status
        if progress is not None:
            self.progress = progress
        if message:
            self.message = message
        if result:
            self.result = result
        if error:
            self.error = error
        if stage:
            self.stage = stage
        if stock_code:
            self.stock_code = stock_code
        self.updated_at = datetime.now()
        
    def to_dict(self):
        """转换为字典"""
        return {
            "company_name": self.company_name,
            "stock_code": self.stock_code,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "stage": self.stage,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error": self.error
        }

# 加载已有的任务数据
def load_task_store():
    """从本地文件加载任务存储"""
    global task_store
    try:
        if os.path.exists(TASK_STORE_FILE):
            with open(TASK_STORE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 转换回TaskStatus对象
                for task_id, task_data in data.items():
                    status = TaskStatus(task_data['company_name'])
                    status.__dict__.update(task_data)
                    task_store[task_id] = status
            logger.info(f"从 {TASK_STORE_FILE} 加载了 {len(task_store)} 个任务")
    except Exception as e:
        logger.error(f"加载任务存储失败: {str(e)}")

# 保存任务数据到本地文件
def save_task_store():
    """保存任务存储到本地文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(TASK_STORE_FILE), exist_ok=True)
        
        # 将TaskStatus对象转换为可序列化的字典
        serializable_data = {}
        for task_id, task in task_store.items():
            task_dict = task.to_dict()
            # 添加结果数据
            if hasattr(task, 'result') and task.result:
                task_dict['result'] = task.result
            serializable_data[task_id] = task_dict
            
        with open(TASK_STORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        logger.info(f"保存了 {len(task_store)} 个任务到 {TASK_STORE_FILE}")
    except Exception as e:
        logger.error(f"保存任务存储失败: {str(e)}")

# 在应用启动时加载任务存储
load_task_store()

# 缓存辅助函数
def generate_cache_key(stock_code: str, analysis_type: str = "综合分析") -> str:
    """根据股票代码和分析类型生成缓存键"""
    today = datetime.now().strftime("%Y%m%d")
    return f"stock_analysis:{stock_code}:{analysis_type}:{today}"

def generate_task_id(company_name: str, stock_code: str = None) -> str:
    """生成与公司名称和股票代码关联的任务ID
    
    如果存在相同公司的已完成任务，则返回该任务ID
    否则创建新的任务ID
    """
    # 查找已有的已完成任务
    for task_id, task in task_store.items():
        if (task.company_name == company_name or 
            (stock_code and task.stock_code == stock_code)) and task.status == "completed":
            logger.info(f"找到已有的任务: {task_id} 对应公司: {company_name}")
            return task_id
            
    # 没有找到已有任务，创建新ID
    if stock_code:
        # 使用股票代码作为基础生成一个确定性但唯一的ID
        task_id = f"task_{stock_code}_{int(time.time())}"
    else:
        # 否则使用UUID
        task_id = str(uuid.uuid4())
        
    logger.info(f"创建新任务ID: {task_id}")
    return task_id

def get_cached_result(stock_code: str, analysis_type: str = "综合分析") -> Optional[Dict]:
    """从缓存获取分析结果"""
    # 首先尝试从Redis缓存获取
    if cache.available:
        try:
            cache_key = generate_cache_key(stock_code, analysis_type)
            cached_data = cache.get(cache_key)
            
            if cached_data:
                logger.info(f"从Redis缓存获取到股票{stock_code}的数据")
                return cached_data
        except Exception as e:
            logger.error(f"从Redis缓存获取数据失败: {str(e)}")
    
    # 如果Redis没有数据，尝试从本地文件加载
    try:
        cache_dir = os.path.join("database", "cache")
        cache_file = os.path.join(cache_dir, f"{stock_code}_{analysis_type.replace(' ', '_')}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                local_cached_data = json.load(f)
                logger.info(f"从本地文件缓存获取到股票{stock_code}的数据")
                return local_cached_data
    except Exception as e:
        logger.error(f"从本地文件缓存获取数据失败: {str(e)}")
    
    # 两种缓存都没有找到
    return None

def save_to_cache(stock_code: str, result_data: Dict, analysis_type: str = "综合分析", expire_time: int = REDIS_CACHE_TTL) -> bool:
    """保存分析结果到缓存"""
    if not cache.available:
        return False
    
    try:
        cache_key = generate_cache_key(stock_code, analysis_type)
        # 直接使用cache.set，内部已经处理JSON序列化
        return cache.set(cache_key, result_data, expire_time)
    except Exception as e:
        logger.error(f"保存数据到缓存失败: {str(e)}")
        return False

def process_stock_analysis(task_id: str, company_name: str, analysis_type: str = "综合分析", force_refresh: bool = False):
    """
    处理股票分析任务，并更新任务状态
    
    Args:
        task_id: 任务ID
        company_name: 公司名称
        analysis_type: 分析类型
        force_refresh: 是否强制刷新
    """
    task = task_store[task_id]
    logger.info(f"开始处理任务 {task_id} - 公司: {company_name}")
    # 更新初始状态
    task.update(
        status="processing", 
        progress=5, 
        message="正在初始化...",
        stage="准备中"
    )
    
    try:
        # 从公司名称获取股票代码
        stock_code = None
        try:
            from tools.stock_info_tools import get_stock_code_by_name
            task.update(progress=8, message="正在获取股票代码...", stage="数据收集")
            stock_code = get_stock_code_by_name(company_name)
            if stock_code:
                task.update(stock_code=stock_code, progress=12, message=f"成功获取股票代码: {stock_code}", stage="数据收集")
                logger.info(f"获取到股票代码: {stock_code}")
        except Exception as e:
            logger.warning(f"获取股票代码失败: {str(e)}")
            
        # 如果启用了缓存且不是强制刷新，尝试从缓存获取
        if not force_refresh and cache.available:
            task.update(progress=15, message="检查缓存数据...", stage="数据收集")
            cache_key = generate_cache_key(stock_code, analysis_type)
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"从缓存获取到分析结果 - 股票: {stock_code}")
                task.update(progress=20, message="从缓存获取数据...", stage="数据收集")
                
                # 定义所有支持的模块 - 需要与前端组件相匹配
                modules_info = [
                    {"type": "basic_info", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/basic_info"},
                    {"type": "market_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/market_data"},
                    {"type": "financial_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/financial_data"},
                    {"type": "research_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/research_data"},
                    {"type": "visualizations", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/visualizations"},
                    {"type": "report", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/report"}
                ]
                
                # 模拟加载过程更新进度
                for progress in range(30, 101, 10):
                    task.update(
                        progress=progress,
                        message=f"从缓存加载数据 ({progress}%)...",
                        stage="数据加载"
                    )
                    time.sleep(0.2)  # 短暂停顿，模拟加载过程
                
                # 更新任务为缓存获取完成
                task.update(
                    status="completed",
                    progress=100,
                    message="从缓存获取分析完成",
                    result={
                        "success": True,
                        "task_id": task_id,
                        "status": "completed",
                        "cached": True,
                        "modules": modules_info,
                        "data": cached_result
                    },
                    stage="完成(缓存)"
                )
                
                # 保存任务状态到本地文件
                save_task_store()
                
                return
                
        # 执行分析前确保创建存储目录
        if stock_code:
            base_dir = f"database/data/{stock_code}"
            vis_dir = f"{base_dir}/visualizations"
            os.makedirs(base_dir, exist_ok=True)
            os.makedirs(vis_dir, exist_ok=True)
            os.makedirs(f"{vis_dir}/trade_data", exist_ok=True)
            os.makedirs(f"{vis_dir}/technical_data", exist_ok=True)
            
        # 如果没有缓存或强制刷新，执行分析
        task.update(progress=18, message="正在获取基础数据...", stage="数据收集")
        
        # 执行分析 - 使用更低的递归限制
        # 创建一个进度更新函数，用于在分析过程中更新进度
        def progress_callback(stage, progress_value, message):
            # 将stage和progress调整到适当的范围
            adjusted_progress = 20 + int(progress_value * 0.7)  # 将进度调整到20%-90%之间
            task.update(progress=adjusted_progress, message=message, stage=stage)
            # 确保立即写入到响应流中
            logger.info(f"Progress update: {stage} - {adjusted_progress}% - {message}")
            
        # 开始分析前更新进度
        task.update(progress=20, message="开始深度分析...", stage="数据分析")
        
        # 执行分析
        results = run_stock_analysis(company_name, recursion_limit=100, progress_callback=progress_callback)
        
        # 数据收集阶段完成
        task.update(progress=65, message="基础数据收集完成，开始分析...", stage="数据分析")
        
        # 处理结果数据，准备响应格式
        task.update(progress=75, message="处理分析结果...", stage="结果整理")
        
        # 添加一个监听函数来检查特定的完成事件
        def check_analysis_progress():
            # 检查报告是否已经生成
            if "report_state" in results and hasattr(results["report_state"], "text_reports"):
                reports = results["report_state"].text_reports
                
                # 更新进度基于已完成的报告数量
                completed_reports = 0
                total_reports = 4  # 基本面、技术面、情感和对抗性分析
                
                if "fundamentals_report" in reports:
                    completed_reports += 1
                    task.update(progress=65, message="基本面分析已完成", stage="深度分析")
                
                if "technical_report" in reports:
                    completed_reports += 1
                    task.update(progress=70, message="技术面分析已完成", stage="深度分析")
                
                if "sentiment_report" in reports:
                    completed_reports += 1
                    task.update(progress=75, message="情感分析已完成", stage="深度分析")
                
                if "adversarial_report" in reports:
                    completed_reports += 1
                    task.update(progress=85, message="对抗性分析已完成", stage="结果整理")
                
                # 如果所有报告都完成了，更新总体进度
                if completed_reports == total_reports:
                    task.update(progress=90, message="所有分析已完成，正在生成综合报告...", stage="结果整理")
        
        # 检查分析进度
        check_analysis_progress()
        
        response_data = {
            # 基本信息模块
            "basic_info": {
                "stock_code": results["basic_info"].stock_code,
                "stock_name": results["basic_info"].stock_name,
                "industry": results["basic_info"].industry,
                "company_info": dataframe_to_json_friendly(results["basic_info"].company_info) if results["basic_info"].company_info is not None else None
            },
            # 市场数据模块
            "market_data": {
                "trade_data": dataframe_to_json_friendly(results["market_data"].trade_data) if results["market_data"].trade_data is not None else None,
                "sector_data": dataframe_to_json_friendly(results["market_data"].sector_data) if results["market_data"].sector_data is not None else None,
                "technical_data": dataframe_to_json_friendly(results["market_data"].technical_data) if results["market_data"].technical_data is not None else None
            },
            # 财务数据模块 
            "financial_data": None,  # 先初始化为None
            # 研究数据模块
            "research_data": {
                "analyst_data": dataframe_to_json_friendly(results["research_data"].analyst_data) if results["research_data"].analyst_data is not None else None,
                "news_data": results["research_data"].news_data
            },
            # 可视化模块 - 处理图表路径，确保正确格式
            "visualization_paths": [f"/static/{path.replace('database/', '')}" for path in results["visualization_paths"]],
            "graph_description": results.get("graph_description", []),
            "data_file_paths": {k: f"/static/{v.replace('database/', '')}" for k, v in results["data_file_paths"].items()},
            
            # 报告模块 - 综合分析报告
            "report_state": results["report_state"].to_dict() if "report_state" in results else {}
        }
        
        # 安全处理财务数据 - 检查是否为ConnectTimeout
        task.update(progress=82, message="处理财务数据...", stage="结果整理")
        try:
            if results["financial_data"] is not None:
                # 检查类型，避免处理非法类型
                if hasattr(results["financial_data"], "financial_data") and hasattr(results["financial_data"].financial_data, "to_dict"):
                    response_data["financial_data"] = dataframe_to_json_friendly(results["financial_data"].financial_data)
                else:
                    logger.warning(f"财务数据对象类型不正确: {type(results['financial_data'])}")
        except Exception as err:
            logger.error(f"处理财务数据时出错: {str(err)}")
        
        # 转换所有 NumPy 数据类型
        task.update(progress=90, message="处理数据类型...", stage="结果整理")
        
        # 确保所有数据都能被正确序列化
        # 特别处理研究数据中的日期和Timestamp
        if "research_data" in response_data and response_data["research_data"] is not None:
            if "analyst_data" in response_data["research_data"] and response_data["research_data"]["analyst_data"] is not None:
                # 如果analyst_data是DataFrame，确保转换为JSON友好格式
                if hasattr(response_data["research_data"]["analyst_data"], "to_dict"):
                    response_data["research_data"]["analyst_data"] = dataframe_to_json_friendly(
                        response_data["research_data"]["analyst_data"]
                    )
        
        # 应用全局NumPy类型转换
        converted_response = convert_numpy_types(response_data)
        
        # 定义所有支持的模块 - 需要与前端组件相匹配
        modules_info = [
            {"type": "basic_info", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/basic_info"},
            {"type": "market_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/market_data"},
            {"type": "financial_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/financial_data"},
            {"type": "research_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/research_data"},
            {"type": "visualizations", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/visualizations"},
            {"type": "report", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/report"}
        ]
        
        # 保存到缓存
        task.update(progress=95, message="保存分析结果到缓存...", stage="结果整理")
        if cache.available and results["basic_info"].stock_code:
            real_stock_code = results["basic_info"].stock_code
            cache_key = generate_cache_key(real_stock_code, analysis_type)
            save_success = cache.set(cache_key, converted_response, REDIS_CACHE_TTL)
            logger.info(f"缓存保存{'成功' if save_success else '失败'} - 股票: {real_stock_code}")
            
            # 同时保存结果到本地文件
            try:
                cache_dir = os.path.join("database", "cache")
                os.makedirs(cache_dir, exist_ok=True)
                cache_file = os.path.join(cache_dir, f"{real_stock_code}_{analysis_type.replace(' ', '_')}.json")
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(converted_response, f, ensure_ascii=False, indent=2)
                logger.info(f"本地缓存保存成功: {cache_file}")
            except Exception as e:
                logger.error(f"保存本地缓存失败: {str(e)}")
        
        # 更新任务完成状态
        task.update(
            status="completed", 
            progress=100, 
            message="分析完成", 
            result={
                "success": True, 
                "task_id": task_id,
                "status": "completed",
                "cached": False,
                "modules": modules_info,
                "data": converted_response
            },
            stage="完成"
        )
        
        # 保存任务状态到本地文件
        save_task_store()
        
        logger.info(f"任务 {task_id} 成功完成")
        
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(f"任务 {task_id} 处理失败: {str(e)}\n{error_stack}")
        task.update(
            status="failed", 
            progress=100, 
            message=f"分析失败: {str(e)}", 
            error=str(e),
            stage="错误"
        )
        
        # 即使失败也保存任务状态
        save_task_store()

@app.post("/api/v1/stock-analysis/task")
async def create_analysis_task(request: StockAnalysisRequest):
    """
    创建股票分析任务并立即返回任务ID
    """
    try:
        # 如果提供了股票代码，先尝试从缓存获取结果
        if request.stock_code and not request.force_refresh:
            cached_result = get_cached_result(request.stock_code, request.analysis_type)
            if cached_result:
                logger.info(f"找到股票 {request.stock_code} 的缓存结果")
                
                # 使用已有的任务ID或创建新ID
                task_id = generate_task_id(request.company_name, request.stock_code)
                
                # 如果是新任务，初始化并填充结果
                if task_id not in task_store:
                    task = TaskStatus(request.company_name)
                    task.stock_code = request.stock_code
                    task.status = "completed"
                    task.progress = 100
                    task.message = "从缓存加载数据完成"
                    task.stage = "完成(缓存)"
                    
                    # 定义所有支持的模块
                    modules_info = [
                        {"type": "basic_info", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/basic_info"},
                        {"type": "market_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/market_data"},
                        {"type": "financial_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/financial_data"},
                        {"type": "research_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/research_data"},
                        {"type": "visualizations", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/visualizations"},
                        {"type": "report", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/report"}
                    ]
                    
                    task.result = {
                        "success": True,
                        "task_id": task_id,
                        "status": "completed",
                        "cached": True,
                        "modules": modules_info,
                        "data": cached_result
                    }
                    
                    task_store[task_id] = task
                    save_task_store()
                
                return {
                    "success": True, 
                    "task_id": task_id, 
                    "message": "任务已创建，从缓存获取结果"
                }
        
        # 创建任务ID，可能复用已有任务
        task_id = generate_task_id(request.company_name, request.stock_code)
        
        # 如果是已完成的任务且不需要强制刷新，直接返回
        if task_id in task_store and task_store[task_id].status == "completed" and not request.force_refresh:
            logger.info(f"复用已完成的任务 {task_id}")
            return {
                "success": True, 
                "task_id": task_id, 
                "message": "任务已创建，使用已有结果"
            }
        
        # 否则初始化新任务或重置旧任务
        task = TaskStatus(request.company_name)
        if request.stock_code:
            task.stock_code = request.stock_code
        task_store[task_id] = task
        
        logger.info(f"创建任务 {task_id} - 公司: {request.company_name}")
        
        # 启动后台线程处理任务
        thread = threading.Thread(
            target=process_stock_analysis,
            args=(task_id, request.company_name, request.analysis_type, request.force_refresh)
        )
        thread.daemon = True
        thread.start()
        
        return {
            "success": True, 
            "task_id": task_id, 
            "message": "任务已创建，请使用任务ID查询进度"
        }
        
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(f"创建任务失败: {str(e)}\n{error_stack}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stock-analysis/progress/{task_id}")
async def get_task_progress(task_id: str):
    """
    获取任务进度
    """
    try:
        if task_id not in task_store:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = task_store[task_id]
        return task.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(f"获取任务进度失败: {str(e)}\n{error_stack}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stock-analysis/result/{task_id}")
async def get_task_result(task_id: str):
    """
    获取任务结果摘要信息
    """
    try:
        if task_id not in task_store:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = task_store[task_id]
        
        if task.status == "completed":
            # 为减小响应大小，仅返回任务状态和模块信息
            result = task.result
            if isinstance(result, dict) and "data" in result:
                # 定义所有支持的模块 - 需要与前端组件相匹配
                modules_info = [
                    {"type": "basic_info", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/basic_info"},
                    {"type": "market_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/market_data"},
                    {"type": "financial_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/financial_data"},
                    {"type": "research_data", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/research_data"},
                    {"type": "visualizations", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/visualizations"},
                    {"type": "report", "endpoint": f"/api/v1/stock-analysis/result/{task_id}/report"}
                ]
                
                # 返回任务ID、状态、缓存状态和模块信息
                return {
                    "success": True,
                    "task_id": task_id,
                    "status": "completed",
                    "cached": result.get("cached", False),
                    "modules": modules_info
                }
            return result
        elif task.status == "failed":
            raise HTTPException(status_code=500, detail=task.error or "任务执行失败")
        else:
            raise HTTPException(status_code=202, detail="任务仍在处理中")
        
    except HTTPException:
        raise
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(f"获取任务结果失败: {str(e)}\n{error_stack}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stock-analysis/result/{task_id}/{module_type}")
async def get_module_data(task_id: str, module_type: str):
    """
    获取特定模块的分析结果
    
    支持的模块类型:
    - basic_info: 基本信息模块
    - market_data: 市场数据模块
    - financial_data: 财务数据模块
    - research_data: 研究数据模块
    - visualizations: 可视化图表模块
    - report: 综合报告模块
    """
    try:
        if task_id not in task_store:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = task_store[task_id]
        
        if task.status != "completed":
            if task.status == "failed":
                raise HTTPException(status_code=500, detail=task.error or "任务执行失败")
            else:
                raise HTTPException(status_code=202, detail="任务仍在处理中")
        
        # 从完整结果中提取模块数据
        result = task.result
        if not isinstance(result, dict) or "data" not in result:
            raise HTTPException(status_code=500, detail="结果格式错误")
        
        data = result["data"]
        
        # 根据模块类型返回对应数据
        if module_type == "basic_info":
            # 基本信息模块 - 公司基础信息
            return data.get("basic_info", {})
        elif module_type == "market_data":
            # 市场数据模块 - 交易数据、板块数据、技术指标
            return data.get("market_data", {})
        elif module_type == "financial_data":
            # 财务数据模块 - 各种财务指标
            return data.get("financial_data", {})
        elif module_type == "research_data":
            # 研究数据模块 - 分析师报告、新闻
            return data.get("research_data", {})
        elif module_type == "visualizations":
            # 可视化模块 - 各种图表的URL和描述信息
            return {
                "visualization_paths": data.get("visualization_paths", []),
                "graph_description": data.get("graph_description", [])
            }
        elif module_type == "report":
            # 综合报告模块 - 包含所有报告文本和图表
            return data.get("report_state", {})
        else:
            raise HTTPException(status_code=400, detail=f"不支持的模块类型: {module_type}")
        
    except HTTPException:
        raise
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(f"获取模块数据失败: {str(e)}\n{error_stack}")
        raise HTTPException(status_code=500, detail=str(e))

# 保留原有API端点，但修改为使用异步处理
@app.post("/api/v1/stock-analysis")
async def analyze_stock(request: StockAnalysisRequest, background_tasks: BackgroundTasks):
    """
    个股分析接口 (保留向后兼容性)
    """
    logger.info(f"接收到分析请求: {request.company_name}")
    
    try:
        # 创建任务ID
        task_id = generate_task_id(request.company_name, request.stock_code)
        
        # 初始化任务状态
        task = TaskStatus(request.company_name)
        task_store[task_id] = task
        
        # 添加后台任务
        background_tasks.add_task(
            process_stock_analysis,
            task_id,
            request.company_name,
            request.analysis_type,
            request.force_refresh
        )
        
        # 返回任务信息
        return {
            "success": True,
            "message": "分析请求已接收，正在处理中",
            "task_id": task_id
        }
        
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(f"API错误: {str(e)}\n{error_stack}")
        raise HTTPException(status_code=500, detail=str(e))

# 添加图片服务API
@app.get("/api/v1/images/{image_path:path}")
async def get_image(image_path: str, width: Optional[int] = None, height: Optional[int] = None, thumbnail: bool = False):
    """
    获取图片，支持调整大小和生成缩略图
    
    参数:
    - image_path: 图片路径
    - width: 可选，指定宽度
    - height: 可选，指定高度
    - thumbnail: 是否生成缩略图
    """
    try:
        # 构建完整路径
        full_path = os.path.join("database", image_path)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="图片不存在")
        
        # 获取图片MIME类型
        content_type, _ = mimetypes.guess_type(full_path)
        if not content_type:
            content_type = "application/octet-stream"
        
        # 如果不需要调整大小，直接返回原图
        if not width and not height and not thumbnail:
            with open(full_path, "rb") as f:
                image_data = f.read()
            return Response(content=image_data, media_type=content_type)
        
        # 使用PIL处理图片
        try:
            img = Image.open(full_path)
            
            if thumbnail:
                # 缩略图模式（保持比例）
                thumb_size = (width or 200, height or 200)  # 默认200x200
                img.thumbnail(thumb_size)
            elif width or height:
                # 调整大小（可能改变比例）
                new_width = width or img.width
                new_height = height or img.height
                img = img.resize((new_width, new_height))
            
            # 保存到内存中
            img_byte_arr = io.BytesIO()
            img_format = img.format or "JPEG"
            img.save(img_byte_arr, format=img_format)
            img_byte_arr.seek(0)
            
            return Response(content=img_byte_arr.getvalue(), media_type=content_type)
        
        except Exception as e:
            logger.error(f"处理图片失败: {str(e)}")
            # 如果处理失败，返回原图
            with open(full_path, "rb") as f:
                image_data = f.read()
            return Response(content=image_data, media_type=content_type)
        
    except HTTPException:
        raise
    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(f"获取图片失败: {str(e)}\n{error_stack}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
