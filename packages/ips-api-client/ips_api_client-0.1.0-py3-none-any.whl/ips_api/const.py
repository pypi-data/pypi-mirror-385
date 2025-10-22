"""Constants for IPS Controllers API."""

BASE_URL = "https://monitor.ipscontrollers.com"

# Endpoints
LOGIN_URL = f"{BASE_URL}/Login.aspx"
MY_DEVICES_URL = f"{BASE_URL}/MyDevices.aspx"
DEVICE_DETAIL_URL = f"{BASE_URL}/DeviceDetail.aspx"
LOGOUT_URL = f"{BASE_URL}/Logout.aspx"

# Default settings
DEFAULT_TIMEOUT = 30
DEFAULT_POLL_INTERVAL = 900  # 15 minutes

# Status indicators (from image filenames)
STATUS_NORMAL = "normal"
STATUS_ALERT = "alert"
STATUS_WARNING = "warning"
STATUS_OFFLINE = "offline"

STATUS_ICONS = {
    "icon_green_light.png": STATUS_NORMAL,
    "icon_red_light.png": STATUS_ALERT,
    "icon_yellow_light.png": STATUS_WARNING,
}
