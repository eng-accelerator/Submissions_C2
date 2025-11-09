"""
Base Agent class for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key or Config.get_api_key()
        self.llm = self._initialize_llm()
        self.status = "initialized"
        self.execution_log = []
        
    def _initialize_llm(self) -> Optional[ChatOpenAI]:
        """Initialize the LLM for this agent"""
        try:
            if not Config.validate_api_key(self.api_key):
                logger.warning(f"{self.name}: Invalid API key")
                return None
            
            # Use OpenRouter if configured
            if Config.USE_OPENROUTER:
                return ChatOpenAI(
                    model=Config.OPENROUTER_MODEL,
                    temperature=Config.TEMPERATURE,
                    api_key=self.api_key,
                    base_url=Config.OPENROUTER_BASE_URL,
                    max_tokens=Config.MAX_TOKENS,
                    default_headers={
                        "HTTP-Referer": "https://github.com/devops-incident-suite",
                        "X-Title": "DevOps Incident Analysis Suite"
                    }
                )
            else:
                return ChatOpenAI(
                    model=Config.DEFAULT_MODEL,
                    temperature=Config.TEMPERATURE,
                    api_key=self.api_key,
                    max_tokens=Config.MAX_TOKENS,
                )
        except Exception as e:
            logger.error(f"{self.name}: Failed to initialize LLM: {e}")
            return None
    
    def log_action(self, action: str, details: Any = None):
        """Log agent actions for traceability"""
        log_entry = {
            "agent": self.name,
            "action": action,
            "details": details,
            "status": self.status
        }
        self.execution_log.append(log_entry)
        logger.info(f"{self.name} - {action}")
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
    
    def get_execution_log(self) -> list:
        """Return the execution log"""
        return self.execution_log
    
    def reset(self):
        """Reset agent state"""
        self.status = "initialized"
        self.execution_log = []

