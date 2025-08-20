from pydantic import BaseModel
from typing import Any, Optional

class ToolResult(BaseModel):
    """
    Represents the result of a tool execution.
    """
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
