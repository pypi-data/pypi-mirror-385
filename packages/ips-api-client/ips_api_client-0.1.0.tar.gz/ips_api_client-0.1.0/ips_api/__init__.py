"""IPS Controllers API Client Library."""

__version__ = "0.1.0"

from .client import IPSClient
from .models import PoolController, PoolReading, ControllerStatus
from .exceptions import (
    IPSError,
    AuthenticationError,
    SessionExpiredError,
    ControllerNotFoundError,
)

__all__ = [
    "IPSClient",
    "PoolController",
    "PoolReading",
    "ControllerStatus",
    "IPSError",
    "AuthenticationError",
    "SessionExpiredError",
    "ControllerNotFoundError",
]
