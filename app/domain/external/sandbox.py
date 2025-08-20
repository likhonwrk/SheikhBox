from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from app.domain.models.tool_result import ToolResult
from app.domain.external.browser import Browser

class Sandbox(ABC):
    """
    Abstract base class defining the interface for a sandbox environment.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """The unique identifier of the sandbox."""
        pass

    @classmethod
    @abstractmethod
    async def create(cls) -> 'Sandbox':
        """Creates a new sandbox instance."""
        pass
    
    @classmethod
    @abstractmethod
    async def get(cls, id: str) -> 'Sandbox':
        """Gets an existing sandbox instance by its ID."""
        pass

    @abstractmethod
    async def destroy(self) -> bool:
        """Destroys the sandbox and cleans up resources."""
        pass

    @abstractmethod
    async def get_browser(self) -> Browser:
        """Gets a browser instance within the sandbox."""
        pass

    @abstractmethod
    async def exec_command(self, session_id: str, exec_dir: str, command: str) -> ToolResult:
        """Executes a shell command."""
        pass

    @abstractmethod
    async def file_write(self, file: str, content: str) -> ToolResult:
        """Writes content to a file."""
        pass

    @abstractmethod
    async def file_read(self, file: str) -> ToolResult:
        """Reads content from a file."""
        pass
