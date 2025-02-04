from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from logger import setup_logger

class LanguageModelManager:
    def __init__(self):
        """Initialize the language model manager"""
        self.logger = setup_logger()
        self.llm_oai = None
        self.llm_gg = None
        self.power_llm = None
        self.json_llm = None
        self.initialize_llms()

    def initialize_llms(self):
        """Initialize language models"""
        try:
            self.llm_oai = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            self.llm_gg = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
            self.power_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
            self.json_llm = ChatOpenAI(
                model="gpt-4o",
                model_kwargs={"response_format": {"type": "json_object"}},
                temperature=0,
                max_tokens=4096
            )
            self.logger.info("Language models initialized successfully.")
        except Exception as e:
            self.logger.error(f"Error initializing language models: {str(e)}")
            raise

    def get_models(self):
        """Return all initialized language models"""
        return {
            "llm_oai": self.llm_oai,
            "llm_gg": self.llm_gg,
            "power_llm": self.power_llm,
            "json_llm": self.json_llm
        }