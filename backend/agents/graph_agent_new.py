from langgraph_codeact import create_codeact
from core.model import LanguageModelManager
from core.state import StockAnalysisState
from helpers.logger import setup_logger
from tools.code_executor import eval


logger = setup_logger("agent_coder.log")
llm = LanguageModelManager().get_models()["llm_oai_o3"]



def agent_coder(state: StockAnalysisState):
    logger.info("Start agent coder")

    
    codeact = create_codeact(model=llm,tools=[],eval_fn=eval)
    return codeact.compile()
