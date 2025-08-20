from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models.tool_result import ToolResult

class Browser(ABC):
    """
    Abstract base class defining the interface for browser operations.
    """

    @abstractmethod
    async def navigate(self, url: str) -> ToolResult:
        """Navigates to a specific URL."""
        pass

    @abstractmethod
    async def click(self, index: int) -> ToolResult:
        """Clicks on an element identified by an index."""
        pass

    @abstractmethod
    async def input(self, text: str, index: int, press_enter: bool) -> ToolResult:
        """Inputs text into an element identified by an index."""
        pass

    @abstractmethod
    async def view_page(self) -> ToolResult:
        """Views the content of the current page."""
        pass

    @abstractmethod
    async def screenshot(self) -> bytes:
        """Takes a screenshot of the current page."""
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleans up browser resources."""
        pass
