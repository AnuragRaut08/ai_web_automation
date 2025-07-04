
import logging
from typing import Dict, List, Any
from .base_adapter import BaseSaaSAdapter

logger = logging.getLogger(__name__)

class DropboxAdapter(BaseSaaSAdapter):
    def __init__(self, config, browser_manager, ai_agent, data_extractor):
        super().__init__(config, browser_manager, ai_agent, data_extractor)

    async def login(self, credentials: Dict[str, str]) -> bool:
        """Login to Dropbox admin console"""
        try:
            logger.info("Navigating to Dropbox login page")
            await self.browser_manager.goto_url("https://www.dropbox.com/login")

            await self.browser_manager.fill_input('input[name="login_email"]', credentials["email"])
            await self.browser_manager.fill_input('input[name="login_password"]', credentials["password"])
            await self.browser_manager.click_element('button[type="submit"]')

            if not await self.handle_mfa(None):
                logger.warning("MFA required, login cannot proceed automatically.")
                return False

            if not await self.handle_captcha(None):
                logger.warning("CAPTCHA detected during login.")
                return False

            await self.browser_manager.wait_for_element('nav[role="navigation"]', timeout=10000)
            self.session_active = True
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    async def extract_users(self) -> List[Dict[str, str]]:
        """Extract user data from Dropbox admin console"""
        users = []
        try:
            logger.info("Navigating to user management page")
            await self.browser_manager.goto_url("https://www.dropbox.com/team/admin/members")

            await self.browser_manager.wait_for_element('table', timeout=10000)

            # Use AI agent to get column mappings dynamically
            page_html = await self.browser_manager.get_page_html()
            selectors = await self.ai_agent.get_user_table_selectors(page_html)

            rows = await self.browser_manager.query_selector_all(selectors["row_selector"])
            logger.info(f"Found {len(rows)} user rows")

            for row in rows:
                user_data = await self.data_extractor.extract_user_data(row, selectors)
                users.append(user_data)

            logger.info("User extraction completed")
        except Exception as e:
            logger.error(f"User extraction failed: {e}")

        return users

    async def create_user(self, user_data: Dict[str, str]) -> bool:
        """Create new Dropbox user"""
        try:
            logger.info(f"Creating user: {user_data}")
            await self.browser_manager.goto_url("https://www.dropbox.com/team/admin/members/invite")

            await self.browser_manager.fill_input('input[name="email"]', user_data["email"])
            if "name" in user_data:
                await self.browser_manager.fill_input('input[name="full_name"]', user_data["name"])
            if "role" in user_data:
                # Handle role dropdown via AI agent or hardcoded selector
                await self.browser_manager.select_dropdown('select[name="role"]', user_data["role"])

            await self.browser_manager.click_element('button[type="submit"]')
            await self.browser_manager.wait_for_element('div.success-message', timeout=5000)
            
            logger.info("User created successfully")
            return True
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return False

    async def delete_user(self, user_identifier: str) -> bool:
        """Delete a Dropbox user"""
        try:
            logger.info(f"Attempting to delete user: {user_identifier}")
            await self.browser_manager.goto_url("https://www.dropbox.com/team/admin/members")

            # Search for the user
            await self.browser_manager.fill_input('input[type="search"]', user_identifier)
            await self.browser_manager.wait_for_element('.user-row', timeout=5000)

            await self.browser_manager.click_element('.user-row .delete-user-button')
            await self.browser_manager.click_element('.confirm-delete-button')
            await self.browser_manager.wait_for_element('div.success-message', timeout=5000)

            logger.info("User deleted successfully")
            return True
        except Exception as e:
            logger.error(f"User deletion failed: {e}")
            return False

    async def update_user(self, user_identifier: str, updates: Dict[str, str]) -> bool:
        """Update Dropbox user details"""
        try:
            logger.info(f"Updating user {user_identifier} with {updates}")
            await self.browser_manager.goto_url("https://www.dropbox.com/team/admin/members")

            await self.browser_manager.fill_input('input[type="search"]', user_identifier)
            await self.browser_manager.wait_for_element('.user-row', timeout=5000)

            await self.browser_manager.click_element('.user-row .edit-user-button')

            if "email" in updates:
                await self.browser_manager.fill_input('input[name="email"]', updates["email"])
            if "name" in updates:
                await self.browser_manager.fill_input('input[name="full_name"]', updates["name"])
            if "role" in updates:
                await self.browser_manager.select_dropdown('select[name="role"]', updates["role"])

            await self.browser_manager.click_element('button[type="submit"]')
            await self.browser_manager.wait_for_element('div.success-message', timeout=5000)

            logger.info("User updated successfully")
            return True
        except Exception as e:
            logger.error(f"User update failed: {e}")
            return False
