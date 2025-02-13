from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from helpers.logger import setup_logger

class LanguageModelManager:
    def __init__(self):
        """Initialize the language model manager"""
        self.logger = setup_logger("model_manager.log")
        self.llm_oai_mini = None
        self.llm_google_flash = None
        self.llm_oai_4o = None
        self.json_oai_llm = None
        self.initialize_llms()

    def initialize_llms(self):
        """Initialize language models"""
        try:
            self.llm_oai_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
            self.llm_google_flash = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
            self.llm_oai_4o = ChatOpenAI(model="gpt-4o", temperature=0.5)
            self.json_oai_llm = ChatOpenAI(
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
            "llm_oai_mini": self.llm_oai_mini,
            "llm_google_flash": self.llm_google_flash,
            "llm_oai_4o": self.llm_oai_4o,
            "json_oai_llm": self.json_oai_llm
        }