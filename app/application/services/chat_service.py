from app.application.services.session_service import SessionService
from app.domain.external.llm import LLM
from app.infrastructure.external.llm.gemini_llm import GeminiLLM
import json

class ChatService:
    """
    Service for handling the chat logic within a session.
    """

    def __init__(self, session_service: SessionService):
        self.session_service = session_service
        self.llm = GeminiLLM()
        # In a real app, you'd have a more sophisticated way of managing tools
        self.tools = ["navigate", "view_page", "exec_command", "file_write", "file_read"]

    async def chat(self, session_id: str, message: str):
        """
        Handles a chat message, orchestrates tool use, and generates a response.
        This will be a streaming response (SSE).
        """
        sandbox = await self.session_service.get_session_sandbox(session_id)
        
        # This is a simplified conversation loop. A real implementation would be more complex.
        yield {"event": "message", "data": "Thinking..."}

        # 1. Send the initial prompt to the LLM to get a plan or tool call
        initial_response = await self.llm.ask([
            {"role": "system", "content": f"You are a helpful assistant with access to these tools: {', '.join(self.tools)}. Decide which tool to use."},
            {"role": "user", "content": message}
        ])
        
        # For simplicity, we'll assume the LLM returns a JSON with a tool call.
        # A real implementation would need to parse the response more robustly.
        try:
            tool_call = json.loads(initial_response["content"])
            tool_name = tool_call.get("tool")
            tool_args = tool_call.get("args", {})
            
            yield {"event": "tool", "data": json.dumps(tool_call)}

            # 2. Execute the tool
            if tool_name == "navigate":
                browser = await sandbox.get_browser()
                result = await browser.navigate(tool_args.get("url"))
            elif tool_name == "view_page":
                browser = await sandbox.get_browser()
                result = await browser.view_page()
            # ... other tool implementations ...
            else:
                result = {"success": False, "message": "Unknown tool"}

            yield {"event": "tool_result", "data": json.dumps(result)}

            # 3. Send the result back to the LLM for a final response
            final_response = await self.llm.ask([
                {"role": "user", "content": message},
                {"role": "assistant", "content": json.dumps(tool_call)},
                {"role": "user", "content": f"Tool result: {json.dumps(result)}"}
            ])
            
            yield {"event": "message", "data": final_response["content"]}

        except (json.JSONDecodeError, KeyError):
            # If the LLM didn't return a tool call, just return its response.
            yield {"event": "message", "data": initial_response["content"]}

        yield {"event": "done", "data": ""}
