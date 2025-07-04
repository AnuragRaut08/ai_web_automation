import asyncio
import logging
import pytest

from core.browser_manager import BrowserManager
from core.ai_agent import AIAgent
from core.data_extractor import DataExtractor
from utils.auth_handler import AuthHandler
from utils.captcha_solver import CaptchaSolver
from utils.config import load_config
from adapters.dropbox_adapter import DropboxAdapter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_dropbox_workflow():
    config = load_config("config.yaml")
    browser_manager = BrowserManager(headless=True)
    ai_agent = AIAgent()
    data_extractor = DataExtractor()
    auth_handler = AuthHandler()
    captcha_solver = CaptchaSolver(browser_manager)

    adapter = DropboxAdapter(config, browser_manager, ai_agent, data_extractor)
    adapter.auth_handler = auth_handler
    adapter.captcha_solver = captcha_solver

    credentials = {
        'email': config['credentials']['email'],
        'password': config['credentials']['password']
    }

    try:
        await browser_manager.start()

        # LOGIN
        logger.info("Testing login...")
        login_success = await adapter.login(credentials)
        assert login_success, "Login should succeed"

        await auth_handler.store_session_timestamp()

        # EXTRACT USERS
        logger.info("Testing user extraction...")
        users = await adapter.extract_users()
        assert isinstance(users, list), "Extracted users should be a list"
        assert all('email' in user for user in users), "All users should have email field"
        logger.info(f"Extracted {len(users)} users.")

        # CREATE USER
        logger.info("Testing user creation...")
        test_user = {
            'email': 'testuser@example.com',
            'name': 'Test User',
            'role': 'Member'
        }
        creation_success = await adapter.create_user(test_user)
        assert creation_success, "User creation should succeed"

        # DELETE USER
        logger.info("Testing user deletion...")
        deletion_success = await adapter.delete_user(test_user['email'])
        assert deletion_success, "User deletion should succeed"

        # LOGOUT
        logger.info("Testing logout...")
        logout_success = await adapter.logout()
        assert logout_success, "Logout should succeed"

    except Exception as e:
        logger.error(f"Test failed due to unexpected error: {e}")
        raise
    finally:
        await browser_manager.stop()


