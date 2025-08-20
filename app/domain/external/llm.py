from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLM(ABC):
    """
    Abstract base class defining the interface for a Large Language Model.
    """

    @abstractmethod
    async def ask(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Sends a request to the LLM and gets a response.
        """
        pass
