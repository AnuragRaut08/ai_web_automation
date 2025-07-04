import asyncio
from playwright.async_api import async_playwright, Page, Browser
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def start(self):
        """Initialize browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.get('headless', True)
        )
        
        context = await self.browser.new_context(
            viewport=self.config.get('viewport', {'width': 1920, 'height': 1080}),
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.page = await context.new_page()
        await self.page.set_default_timeout(self.config.get('timeout', 30000))
        
        return self.page
    
    async def navigate(self, url: str):
        """Navigate to URL with error handling"""
        try:
            await self.page.goto(url, wait_until='domcontentloaded')
            await self.page.wait_for_timeout(2000)  # Wait for dynamic content
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    async def wait_for_element(self, selector: str, timeout: int = 10000):
        """Wait for element to be visible"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Element not found: {selector}, Error: {e}")
            return False
    
    async def click_element(self, selector: str):
        """Click element with retry logic"""
        for attempt in range(3):
            try:
                await self.page.click(selector)
                return True
            except Exception as e:
                logger.warning(f"Click attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)
        return False
    
    async def type_text(self, selector: str, text: str):
        """Type text into element"""
        try:
            await self.page.fill(selector, text)
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    async def get_page_content(self):
        """Get current page HTML content"""
        return await self.page.content()
    
    async def screenshot(self, path: str):
        """Take screenshot for debugging"""
        await self.page.screenshot(path=path)
    
    async def close(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
