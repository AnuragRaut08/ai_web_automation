import asyncio
import logging
from utils.config import load_config
from core.browser_manager import BrowserManager
from core.ai_agent import AIAgent
from core.data_extractor import DataExtractor
from utils.auth_handler import AuthHandler
from utils.captcha_solver import CaptchaSolver
from adapters.notion_adapter import NotionAdapter
from adapters.dropbox_adapter import DropboxAdapter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Load configuration
    config = load_config("config.yaml")

    # Initialize core components
    browser_manager = BrowserManager(headless=False)  # Headless=False for dev
    ai_agent = AIAgent()
    data_extractor = DataExtractor()
    auth_handler = AuthHandler()
    captcha_solver = CaptchaSolver(browser_manager)

    # Choose SaaS adapter (example: Notion)
    adapter = NotionAdapter(config, browser_manager, ai_agent, data_extractor)
    adapter.auth_handler = auth_handler
    adapter.captcha_solver = captcha_solver

    credentials = {
        'email': config['credentials']['email'],
        'password': config['credentials']['password']
    }

    try:
        # Start browser
        await browser_manager.start()

        # Login
        logger.info("Attempting login...")
        login_success = await adapter.login(credentials)
        if not login_success:
            logger.error("Login failed.")
            return

        await auth_handler.store_session_timestamp()

        # Extract users
        logger.info("Extracting users...")
        users = await adapter.extract_users()
        logger.info(f"Extracted {len(users)} users: {users}")

        # Create a new user (example)
        new_user = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'role': 'Member'
        }
        creation_success = await adapter.create_user(new_user)
        logger.info(f"User creation success: {creation_success}")

        # Delete user (example)
        deletion_success = await adapter.delete_user('newuser@example.com')
        logger.info(f"User deletion success: {deletion_success}")

        # Logout
        await adapter.logout()

    except Exception as e:
        logger.error(f"Unhandled error: {e}")
    finally:
        await browser_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())

