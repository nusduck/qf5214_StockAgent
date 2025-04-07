from typing import TypedDict, List, Dict, Annotated
from langgraph.types import Send
from langgraph.graph import END, START, Graph

from pydantic import BaseModel
from core.state import StockAnalysisState

def continue_to_graph(state: StockAnalysisState):
    """ send graph task parallelly """
    return [Send("visualization", {"file_path": s[1],"file_type":s[0],"stock_code":state.basic_info.stock_code}) for s in state.data_file_paths.items()]