
import asyncio
from typing import List, Dict, Any
import logging
from .base_adapter import BaseSaaSAdapter

logger = logging.getLogger(__name__)

class NotionAdapter(BaseSaaSAdapter):
    def __init__(self, config, browser_manager, ai_agent, data_extractor):
        super().__init__(config, browser_manager, ai_agent, data_extractor)
        self.base_url = config.get('notion', {}).get('base_url', 'https://notion.so')
        self.login_url = config.get('notion', {}).get('login_url', 'https://notion.so/login')
        self.admin_url = config.get('notion', {}).get('admin_url', 'https://notion.so/settings/members')
    
    async def login(self, credentials: Dict[str, str]) -> bool:
        """Login to Notion"""
        try:
            # Navigate to login page
            await self.browser_manager.navigate(self.login_url)
            
            # Wait for login form
            if not await self.browser_manager.wait_for_element('input[type="email"]'):
                return False
            
            # Fill credentials
            await self.browser_manager.type_text('input[type="email"]', credentials['email'])
            await self.browser_manager.type_text('input[type="password"]', credentials['password'])
            
            # Submit form
            await self.browser_manager.click_element('button[type="submit"]')
            
            # Wait for login to complete
            await asyncio.sleep(3)
            
            # Check for MFA or CAPTCHA
            if not await self.handle_mfa(self.browser_manager.page):
                return False
            
            if not await self.handle_captcha(self.browser_manager.page):
                return False
            
            # Verify login success
            await asyncio.sleep(2)
            current_url = self.browser_manager.page.url
            
            if 'login' not in current_url:
                self.session_active = True
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Notion login failed: {e}")
            return False
    
    async def extract_users(self) -> List[Dict[str, str]]:
        """Extract users from Notion workspace"""
        if not self.session_active:
            logger.error("Not logged in")
            return []
        
        try:
            # Navigate to members page
            await self.browser_manager.navigate(self.admin_url)
            
            # Wait for members list to load
            await asyncio.sleep(3)
            
            # Get page content
            html_content = await self.browser_manager.get_page_content()
            
            # Use AI to analyze page structure
            page_analysis = self.ai_agent.analyze_page_structure(html_content, "extract_users")
            
            # Extract user data
            users = self.data_extractor.extract_users_from_table(html_content)
            
            # Handle pagination if present
            pagination_info = self.data_extractor.extract_pagination_info(html_content)
            
            if pagination_info.get('has_next'):
                additional_users = await self._extract_paginated_users(pagination_info)
                users.extend(additional_users)
            
            logger.info(f"Extracted {len(users)} users from Notion")
            return users
            
        except Exception as e:
            logger.error(f"User extraction failed: {e}")
            return []
    
    async def _extract_paginated_users(self, pagination_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract users from multiple pages"""
        all_users = []
        
        while pagination_info.get('has_next'):
            # Click next page
            if pagination_info.get('next_selector'):
                await self.browser_manager.click_element(pagination_info['next_selector'])
                await asyncio.sleep(2)
                
                # Extract users from current page
                html_content = await self.browser_manager.get_page_content()
                users = self.data_extractor.extract_users_from_table(html_content)
                all_users.extend(users)
                
                # Update pagination info
                pagination_info = self.data_extractor.extract_pagination_info(html_content)
            else:
                break
        
        return all_users
    
    async def create_user(self, user_data: Dict[str, str]) -> bool:
        """Create a new user in Notion"""
        if not self.session_active:
            return False
        
        try:
            # Navigate to members page
            await self.browser_manager.navigate(self.admin_url)
            
            # Look for "Add member" or "Invite" button
            invite_selectors = [
                'button:has-text("Invite")',
                'button:has-text
