"""Main IPS Controllers API client."""

import logging
from typing import Dict, List, Optional

import aiohttp

from .const import (
    BASE_URL,
    DEFAULT_TIMEOUT,
    DEVICE_DETAIL_URL,
    LOGIN_URL,
    LOGOUT_URL,
    MY_DEVICES_URL,
)
from .exceptions import AuthenticationError, ControllerNotFoundError, SessionExpiredError
from .models import PoolController, PoolReading
from .parser import (
    extract_viewstate_tokens,
    parse_controllers_list,
    parse_device_detail,
)

_LOGGER = logging.getLogger(__name__)


class IPSClient:
    """Client for IPS Controllers monitoring system."""

    def __init__(
        self,
        username: str,
        password: str,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Initialize the IPS client.

        Args:
            username: IPS account email
            password: IPS account password
            session: Optional aiohttp session (will create one if not provided)
            timeout: Request timeout in seconds
        """
        self.username = username
        self.password = password
        self._session = session
        self._owned_session = session is None
        self._timeout = timeout
        self._authenticated = False

    async def __aenter__(self):
        """Async context manager entry."""
        if self._owned_session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the client session."""
        if self._owned_session and self._session:
            await self._session.close()
            self._session = None

    async def _get_viewstate_tokens(self) -> Dict[str, str]:
        """Get ViewState tokens from login page.

        Returns:
            Dictionary with ViewState tokens
        """
        async with self._session.get(LOGIN_URL, timeout=self._timeout) as response:
            response.raise_for_status()
            html = await response.text()
            return extract_viewstate_tokens(html)

    async def login(self) -> bool:
        """Login to IPS Controllers.

        Returns:
            True if login successful

        Raises:
            AuthenticationError: If login fails
        """
        _LOGGER.debug("Logging in to IPS Controllers")

        # Get ViewState tokens
        tokens = await self._get_viewstate_tokens()

        if not all(tokens.values()):
            raise AuthenticationError("Failed to extract ViewState tokens")

        # Prepare login form
        form_data = {
            '__VIEWSTATE': tokens['__VIEWSTATE'],
            '__VIEWSTATEGENERATOR': tokens['__VIEWSTATEGENERATOR'],
            '__EVENTVALIDATION': tokens['__EVENTVALIDATION'],
            'txtLoginName': self.username,
            'txtLoginPassword': self.password,
            'imgbtnLogin.x': '40',
            'imgbtnLogin.y': '32',
        }

        # Submit login
        async with self._session.post(
            LOGIN_URL,
            data=form_data,
            allow_redirects=True,
            timeout=self._timeout,
        ) as response:
            response.raise_for_status()
            final_url = str(response.url)

            # Check if redirected away from login page
            if 'Login.aspx' in final_url:
                _LOGGER.error("Login failed - still on login page")
                raise AuthenticationError("Invalid username or password")

            _LOGGER.info("Successfully logged in to IPS Controllers")
            self._authenticated = True
            return True

    async def logout(self):
        """Logout from IPS Controllers."""
        if not self._authenticated:
            return

        try:
            async with self._session.get(LOGOUT_URL, timeout=self._timeout) as response:
                response.raise_for_status()
                _LOGGER.info("Logged out from IPS Controllers")
        except Exception as e:
            _LOGGER.warning(f"Error during logout: {e}")
        finally:
            self._authenticated = False

    async def _ensure_authenticated(self):
        """Ensure we're authenticated, login if needed."""
        if not self._authenticated:
            await self.login()

    async def _check_session_expired(self, html: str) -> bool:
        """Check if session has expired by looking for login form.

        Args:
            html: Response HTML

        Returns:
            True if session expired
        """
        # If we see login form elements, session expired
        return 'txtLoginName' in html or 'txtLoginPassword' in html

    async def get_controllers(self) -> List[PoolController]:
        """Get list of all controllers.

        Returns:
            List of PoolController objects

        Raises:
            SessionExpiredError: If session has expired
        """
        await self._ensure_authenticated()

        _LOGGER.debug("Fetching controllers list")

        async with self._session.get(MY_DEVICES_URL, timeout=self._timeout) as response:
            response.raise_for_status()
            html = await response.text()

            # Check if session expired
            if await self._check_session_expired(html):
                self._authenticated = False
                raise SessionExpiredError("Session has expired")

            controllers = parse_controllers_list(html)
            _LOGGER.info(f"Found {len(controllers)} controller(s)")

            return controllers

    async def get_controller_detail(self, controller_id: str) -> PoolReading:
        """Get detailed readings for a specific controller.

        Args:
            controller_id: Controller ID

        Returns:
            PoolReading with detailed information

        Raises:
            SessionExpiredError: If session has expired
            ControllerNotFoundError: If controller not found
        """
        await self._ensure_authenticated()

        _LOGGER.debug(f"Fetching details for controller {controller_id}")

        url = f"{DEVICE_DETAIL_URL}?Controller={controller_id}"

        async with self._session.get(url, timeout=self._timeout) as response:
            if response.status == 404:
                raise ControllerNotFoundError(f"Controller {controller_id} not found")

            response.raise_for_status()
            html = await response.text()

            # Check if session expired
            if await self._check_session_expired(html):
                self._authenticated = False
                raise SessionExpiredError("Session has expired")

            reading = parse_device_detail(html)
            _LOGGER.debug(f"Retrieved reading: pH={reading.ph}, ORP={reading.orp}")

            return reading

    async def get_all_readings(self) -> Dict[str, PoolReading]:
        """Get detailed readings for all controllers.

        Returns:
            Dictionary mapping controller_id to PoolReading
        """
        controllers = await self.get_controllers()

        readings = {}
        for controller in controllers:
            try:
                reading = await self.get_controller_detail(controller.controller_id)
                readings[controller.controller_id] = reading
            except Exception as e:
                _LOGGER.warning(
                    f"Failed to get reading for controller {controller.name}: {e}"
                )

        return readings
