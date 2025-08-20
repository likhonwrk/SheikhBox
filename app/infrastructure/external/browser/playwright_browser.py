from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page
import asyncio
from markdownify import markdownify
from app.domain.external.llm import LLM
from app.domain.models.tool_result import ToolResult
import logging

# A placeholder for a real LLM implementation
class PlaceholderLLM(LLM):
    async def ask(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        # In a real scenario, this would call the Gemini API
        return {"content": messages[-1].get("content", "")}

logger = logging.getLogger(__name__)

class PlaywrightBrowser:
    """Playwright client that provides specific implementation of browser operations"""
    
    def __init__(self, cdp_url: str):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.llm = PlaceholderLLM() # Using a placeholder for now
        self.cdp_url = cdp_url
        
    async def initialize(self):
        """Initialize and ensure resources are available"""
        max_retries = 5
        retry_delay = 1
        for attempt in range(max_retries):
            try:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.connect_over_cdp(self.cdp_url)
                contexts = self.browser.contexts
                if contexts and contexts[0].pages:
                    self.page = contexts[0].pages[0]
                else:
                    context = contexts[0] if contexts else await self.browser.new_context()
                    self.page = await context.new_page()
                return True
            except Exception as e:
                await self.cleanup()
                if attempt == max_retries - 1:
                    logger.error(f"Initialization failed after {max_retries} retries: {e}")
                    return False
                retry_delay = min(retry_delay * 2, 10)
                logger.warning(f"Initialization failed, retrying in {retry_delay} seconds: {e}")
                await asyncio.sleep(retry_delay)

    async def cleanup(self):
        """Clean up Playwright resources"""
        try:
            if self.page and not self.page.is_closed():
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            self.page = None
            self.browser = None
            self.playwright = None
    
    async def _ensure_page(self):
        """Ensure the browser and page are initialized."""
        if not self.browser or not self.page or self.page.is_closed():
            if not await self.initialize():
                raise Exception("Failed to initialize browser resources.")

    async def navigate(self, url: str, timeout: int = 60000) -> ToolResult:
        await self._ensure_page()
        try:
            await self.page.goto(url, timeout=timeout)
            return ToolResult(success=True, data={"message": f"Navigated to {url}"})
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to navigate to {url}: {e}")

    async def view_page(self) -> ToolResult:
        await self._ensure_page()
        try:
            content = await self.page.content()
            html_content = await self.page.evaluate("document.body.outerHTML")
            markdown_content = markdownify(html_content)
            
            # Placeholder for content extraction with LLM
            extracted_content = await self.llm.ask([
                {"role": "system", "content": "Extract all information from the page content and convert it to Markdown."},
                {"role": "user", "content": markdown_content[:20000]}
            ])
            
            return ToolResult(success=True, data={"content": extracted_content.get("content", "")})
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to view page: {e}")

    async def click(self, index: int) -> ToolResult:
        # This is a simplified implementation. A real one would use selectors.
        return ToolResult(success=False, message="Click by index is not fully implemented.")

    async def input(self, text: str, index: int, press_enter: bool) -> ToolResult:
        # This is a simplified implementation.
        return ToolResult(success=False, message="Input by index is not fully implemented.")

    async def screenshot(self) -> bytes:
        await self._ensure_page()
        return await self.page.screenshot(type="png")
