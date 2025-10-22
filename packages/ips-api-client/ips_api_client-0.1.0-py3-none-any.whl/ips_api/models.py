"""Data models for IPS Controllers."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PoolReading:
    """Pool chemistry reading."""

    ph: Optional[float] = None
    orp: Optional[int] = None  # Oxidation-Reduction Potential in mV
    temperature: Optional[float] = None
    ppm: Optional[float] = None  # Parts per million (chlorine)
    timestamp: Optional[datetime] = None

    # Additional details (from detail page)
    ph_state: Optional[str] = None
    ph_setpoint: Optional[float] = None


@dataclass
class PoolController:
    """Pool controller device."""

    controller_id: str
    name: str
    status: str  # normal, alert, warning, offline
    current_reading: Optional[PoolReading] = None
    last_reading_time: Optional[datetime] = None
    last_alert_time: Optional[datetime] = None


@dataclass
class ControllerStatus:
    """Overall status information."""

    is_online: bool
    status_code: str  # normal, alert, warning, offline
    status_message: Optional[str] = None
