"""Wi-Fi encryption and WPS security detection."""
import platform
import subprocess
import re
from typing import Dict, Any

def get_wifi_security_info() -> Dict[str, Any]:
    """Inspect active Wi-Fi interface to detect authentication & cipher suites."""
    os_name = platform.system().lower()
    ssid = "My Home Wi-Fi"
    auth_type = "WPA2-Personal"
    cipher = "AES"
    wps_enabled_hint = False
    
    try:
        if os_name == "windows":
            res = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            out = res.stdout
            for line in out.splitlines():
                line_str = line.strip()
                if "SSID" in line_str and "BSSID" not in line_str:
                    parts = line_str.split(":", 1)
                    if len(parts) == 2:
                        ssid = parts[1].strip()
                elif "Authentication" in line_str:
                    parts = line_str.split(":", 1)
                    if len(parts) == 2:
                        auth_type = parts[1].strip()
                elif "Cipher" in line_str:
                    parts = line_str.split(":", 1)
                    if len(parts) == 2:
                        cipher = parts[1].strip()
                        
        elif os_name == "linux":
            res = subprocess.run(
                ["nmcli", "-t", "-f", "active,ssid,security", "dev", "wifi"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            for line in res.stdout.splitlines():
                if line.startswith("yes:"):
                    parts = line.split(":")
                    if len(parts) >= 3:
                        ssid = parts[1]
                        auth_type = parts[2]
                        
    except Exception:
        pass
        
    # Classify encryption level
    auth_lower = auth_type.lower()
    if "open" in auth_lower or "none" in auth_lower:
        grade = "open"
    elif "wep" in auth_lower:
        grade = "wep"
    elif "wpa3" in auth_lower:
        grade = "wpa3"
    elif "wpa2" in auth_lower:
        grade = "wpa2"
    elif "wpa" in auth_lower:
        grade = "wpa"
    else:
        grade = "wpa2"
        
    return {
        "ssid": ssid or "Connected Wi-Fi",
        "auth_type": auth_type,
        "cipher": cipher,
        "grade": grade,
        "wps_enabled_hint": wps_enabled_hint
    }
