from __future__ import annotations

import asyncio

from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

from noqa_runner.logging_config import get_logger
from shared.utils.retry_decorator import with_retry

logger = get_logger(__name__)


class AppiumClient:
    """Appium client adapter for mobile automation (async context manager)"""

    driver: webdriver.Remote
    resolution: dict
    _loop: asyncio.AbstractEventLoop | None
    _capabilities: dict | None
    _platform_name: str | None

    @with_retry(
        max_attempts=3, min_wait=1, max_wait=3, exceptions=(WebDriverException,)
    )
    def __init__(self, appium_url: str, appium_capabilities=None):
        self.appium_url = appium_url
        self.appium_capabilities = appium_capabilities
        self._loop = None
        self._capabilities = None
        self._platform_name = None

        # Initialize driver immediately with retry
        self.driver = webdriver.Remote(
            self.appium_url,
            options=AppiumOptions().load_capabilities(self.appium_capabilities or {}),
        )
        self.driver.implicitly_wait(5)
        self.resolution = self.driver.get_window_size()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup driver"""
        await self.close()
        return False

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop"""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    @property
    def capabilities(self) -> dict:
        """Get driver capabilities"""
        if self._capabilities is None:
            self._capabilities = self.driver.capabilities
        return self._capabilities

    @property
    def platform_name(self) -> str:
        """Get platform name (iOS or Android)"""
        if self._platform_name is None:
            self._platform_name = self.capabilities.get("platformName", "iOS").lower()
        return self._platform_name

    @with_retry(max_attempts=3)
    async def get_page_source(self) -> str:
        """Get page source XML from driver"""
        # Run in executor to avoid blocking the event loop
        return await self.loop.run_in_executor(None, lambda: self.driver.page_source)

    async def get_element(self, element_locator):
        """Get single element by XPath locator"""
        try:
            element = await self.loop.run_in_executor(
                None, lambda: self.driver.find_element(AppiumBy.XPATH, element_locator)
            )
            return element
        except Exception:
            logger.debug(f"Element with locator {element_locator} not found")
            return None

    async def get_elements(self, element_locator):
        """Get multiple elements by XPath locator"""
        try:
            elements = await self.loop.run_in_executor(
                None, lambda: self.driver.find_elements(AppiumBy.XPATH, element_locator)
            )
            return elements
        except Exception:
            logger.debug(f"Elements with locator {element_locator} not found")
            return None

    async def tap_by_coords(self, x: int, y: int) -> None:
        """Tap at specific coordinates"""
        await self.loop.run_in_executor(None, lambda: self.driver.tap([(x, y)]))

    @with_retry(
        max_attempts=3,
        min_wait=1,
        max_wait=2,
        exceptions=(StaleElementReferenceException,),
    )
    async def tap(self, element_locator: str) -> bool:
        """Tap element by XPath locator"""
        element = await self.get_element(element_locator)
        if not element:
            logger.error(f"Element to tap with locator {element_locator} not found")
            return False

        await self.loop.run_in_executor(None, lambda: element.click())
        return True

    async def swipe(self, direction: str, start_x: int, start_y: int) -> None:
        """Swipe from element center, swipe distance is always half of screen size"""
        # Get screen dimensions
        screen_width = self.resolution["width"]
        screen_height = self.resolution["height"]

        # Swipe distance is half of screen
        swipe_distance_vertical = screen_height // 2
        swipe_distance_horizontal = screen_width // 2

        if direction == "down":
            # Swipe up (from start to top)
            end_x = start_x
            end_y = max(0, start_y - swipe_distance_vertical)
        elif direction == "up":
            # Swipe down (from start to bottom)
            end_x = start_x
            end_y = min(screen_height, start_y + swipe_distance_vertical)
        elif direction == "right":
            # Swipe right (from start to right)
            end_x = min(screen_width, start_x + swipe_distance_horizontal)
            end_y = start_y
        elif direction == "left":
            # Swipe left (from start to left)
            end_x = max(0, start_x - swipe_distance_horizontal)
            end_y = start_y
        else:
            raise ValueError(f"Invalid swipe direction: {direction}")
        logger.info(
            f"Performing swipe from ({start_x}, {start_y}) to ({end_x}, {end_y})"
        )

        await self.loop.run_in_executor(
            None, lambda: self.driver.swipe(start_x, start_y, end_x, end_y, 1000)
        )

    async def open_url(self, url: str) -> None:
        """Navigate to URL"""
        await self.loop.run_in_executor(None, lambda: self.driver.get(url))

    async def accept_system_alert(self) -> None:
        """Accept system alert"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.switch_to.alert.accept()
        )

    async def dismiss_system_alert(self) -> None:
        """Dismiss system alert"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.switch_to.alert.dismiss()
        )

    @with_retry(max_attempts=2)
    async def get_screenshot(self) -> str:
        """Get current screenshot as base64"""
        return await self.loop.run_in_executor(
            None, lambda: self.driver.get_screenshot_as_base64()
        )

    async def hide_keyboard(self) -> None:
        """Hide keyboard using platform-specific approach"""
        # iOS: Look for Done button in toolbar
        done_button = await self.get_element(
            "//XCUIElementTypeToolbar//XCUIElementTypeButton[@name='Done']"
        )
        if done_button:
            await self.loop.run_in_executor(None, lambda: done_button.click())

    @with_retry(
        max_attempts=3,
        min_wait=1,
        max_wait=2,
        exceptions=(StaleElementReferenceException,),
    )
    async def input_text_in_element(self, element_locator: str, text: str) -> bool:
        """Input text into element"""
        element = await self.get_element(element_locator)
        if not element:
            return False

        def _input_text():
            element.send_keys(text)
            return True

        result = await self.loop.run_in_executor(None, _input_text)
        # Sleep asynchronously after the synchronous operation
        await asyncio.sleep(2)
        return result

    async def get_alert_text(self) -> str | None:
        """Get alert text"""

        def _get_alert_text():
            try:
                return self.driver.switch_to.alert.text
            except Exception:
                return None

        return await self.loop.run_in_executor(None, _get_alert_text)

    async def activate_app(self, bundle_id: str) -> None:
        """Activate app by bundle ID"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.activate_app(bundle_id)
        )

    async def terminate_app(self, bundle_id: str) -> None:
        """Terminate app by bundle ID"""
        await self.loop.run_in_executor(
            None, lambda: self.driver.terminate_app(bundle_id)
        )

    async def background_app(self) -> None:
        """Background app"""
        await self.loop.run_in_executor(None, lambda: self.driver.background_app(-1))

    async def close(self) -> None:
        """Close the Appium driver connection"""
        if self.driver and hasattr(self.driver, "quit"):
            try:
                await self.loop.run_in_executor(None, lambda: self.driver.quit())
            finally:
                self.driver = None
