"""HTML parsing utilities for IPS Controllers."""

import re
from datetime import datetime
from html.parser import HTMLParser
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from .const import STATUS_ICONS, STATUS_OFFLINE
from .exceptions import ParseError
from .models import PoolController, PoolReading


class ViewStateParser(HTMLParser):
    """Parse ASP.NET ViewState tokens from HTML."""

    def __init__(self):
        super().__init__()
        self.viewstate = None
        self.viewstate_generator = None
        self.event_validation = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'input':
            input_id = attrs_dict.get('id', '')
            input_value = attrs_dict.get('value', '')

            if input_id == '__VIEWSTATE':
                self.viewstate = input_value
            elif input_id == '__VIEWSTATEGENERATOR':
                self.viewstate_generator = input_value
            elif input_id == '__EVENTVALIDATION':
                self.event_validation = input_value


def extract_viewstate_tokens(html: str) -> Dict[str, str]:
    """Extract ASP.NET ViewState tokens from HTML.

    Args:
        html: HTML content

    Returns:
        Dictionary with __VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION
    """
    parser = ViewStateParser()
    parser.feed(html)

    return {
        '__VIEWSTATE': parser.viewstate,
        '__VIEWSTATEGENERATOR': parser.viewstate_generator,
        '__EVENTVALIDATION': parser.event_validation,
    }


def parse_datetime(date_str: str) -> Optional[datetime]:
    """Parse datetime from IPS format.

    Args:
        date_str: Date string like "10/21/2025 11:20:21 AM"

    Returns:
        datetime object or None if parsing fails
    """
    if not date_str or not date_str.strip():
        return None

    try:
        return datetime.strptime(date_str.strip(), "%m/%d/%Y %I:%M:%S %p")
    except ValueError:
        try:
            # Try without seconds
            return datetime.strptime(date_str.strip(), "%m/%d/%Y %I:%M %p")
        except ValueError:
            return None


def parse_float(value: str) -> Optional[float]:
    """Parse float value, handling empty strings.

    Args:
        value: String value

    Returns:
        Float or None
    """
    if not value or not value.strip():
        return None

    try:
        return float(value.strip())
    except ValueError:
        return None


def parse_int(value: str) -> Optional[int]:
    """Parse int value, handling empty strings.

    Args:
        value: String value

    Returns:
        Int or None
    """
    if not value or not value.strip():
        return None

    try:
        return int(value.strip())
    except ValueError:
        return None


def extract_status_from_icon(img_src: str) -> str:
    """Extract status from icon filename.

    Args:
        img_src: Image source path

    Returns:
        Status code
    """
    for icon_name, status in STATUS_ICONS.items():
        if icon_name in img_src:
            return status
    return STATUS_OFFLINE


def parse_controllers_list(html: str) -> List[PoolController]:
    """Parse list of controllers from MyDevices.aspx.

    Args:
        html: HTML content from MyDevices.aspx

    Returns:
        List of PoolController objects
    """
    soup = BeautifulSoup(html, 'html.parser')
    controllers = []

    # Find all device links
    device_links = soup.find_all('a', href=re.compile(r'DeviceDetail\.aspx\?Controller='))

    for link in device_links:
        try:
            # Extract controller ID from URL
            href = link.get('href', '')
            match = re.search(r'Controller=([^&]+)', href)
            if not match:
                continue

            controller_id = match.group(1)
            name = link.get_text(strip=True)

            # Find the parent container to get associated data
            parent = link.find_parent('td')
            if not parent:
                parent = link.find_parent('div')

            if not parent:
                continue

            # Look for status icon (sibling or nearby)
            status_img = parent.find_next('img', src=re.compile(r'icon_.*_light\.png'))
            status = STATUS_OFFLINE
            if status_img:
                status = extract_status_from_icon(status_img.get('src', ''))

            # Look for data spans - they have specific IDs
            # Pattern: dlLocations_ctl00_dlDevices_ctl01_lblDevicepH
            parent_container = link.find_parent('tr') or link.find_parent(['table', 'div'], recursive=True)

            ph_span = None
            orp_span = None
            ppm_span = None
            temp_span = None
            checked_span = None
            alert_span = None

            if parent_container:
                # Find all spans in the container
                spans = parent_container.find_all('span')
                for span in spans:
                    span_id = span.get('id', '')
                    if 'lblDevicepH' in span_id:
                        ph_span = span
                    elif 'lblDeviceORP' in span_id:
                        orp_span = span
                    elif 'lblPPM' in span_id:
                        ppm_span = span
                    elif 'lblTemp' in span_id:
                        temp_span = span
                    elif 'lblDeviceChecked' in span_id:
                        checked_span = span
                    elif 'lblAlertReading' in span_id:
                        alert_span = span

            # Parse values
            reading = PoolReading(
                ph=parse_float(ph_span.get_text() if ph_span else ''),
                orp=parse_int(orp_span.get_text() if orp_span else ''),
                ppm=parse_float(ppm_span.get_text() if ppm_span else ''),
                temperature=parse_float(temp_span.get_text() if temp_span else ''),
            )

            last_reading_time = parse_datetime(checked_span.get_text() if checked_span else '')
            last_alert_time = parse_datetime(alert_span.get_text() if alert_span else '')

            controller = PoolController(
                controller_id=controller_id,
                name=name,
                status=status,
                current_reading=reading,
                last_reading_time=last_reading_time,
                last_alert_time=last_alert_time,
            )

            controllers.append(controller)

        except Exception as e:
            # Skip controllers that fail to parse
            continue

    if not controllers:
        raise ParseError("No controllers found in HTML")

    return controllers


def parse_device_detail(html: str) -> PoolReading:
    """Parse detailed readings from DeviceDetail.aspx.

    Args:
        html: HTML content from DeviceDetail.aspx

    Returns:
        PoolReading object with detailed information
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Find specific labeled elements
    ph_elem = soup.find('span', id='lblphNum')
    orp_elem = soup.find('span', id='lblOrpNum')
    temp_elem = soup.find('span', id='lblTempValue')
    ph_state_elem = soup.find('span', id='lblpHState')
    ph_setpoint_elem = soup.find('span', id='lblphSetpoint')
    timestamp_elem = soup.find('span', id='lblLastReading')

    # Extract pH setpoint from text like "Setpoint: 7.3"
    ph_setpoint = None
    if ph_setpoint_elem:
        setpoint_text = ph_setpoint_elem.get_text()
        match = re.search(r'([0-9.]+)', setpoint_text)
        if match:
            ph_setpoint = parse_float(match.group(1))

    reading = PoolReading(
        ph=parse_float(ph_elem.get_text() if ph_elem else ''),
        orp=parse_int(orp_elem.get_text() if orp_elem else ''),
        temperature=parse_float(temp_elem.get_text() if temp_elem else ''),
        ph_state=ph_state_elem.get_text(strip=True) if ph_state_elem else None,
        ph_setpoint=ph_setpoint,
        timestamp=parse_datetime(timestamp_elem.get_text() if timestamp_elem else ''),
    )

    return reading
