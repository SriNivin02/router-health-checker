"""Top 3 fixes and prioritized remediation generator."""
from typing import List, Dict, Any
from app.db.models import FixItem

ALL_POSSIBLE_FIXES: Dict[str, Dict[str, Any]] = {
    "default_admin_password": {
        "id": "FIX_CHANGE_ADMIN_PASSWORD",
        "title_code": "f1t",
        "desc_code": "f1d",
        "gain": 25,
        "estimated_time": "2 min",
        "svg_icon": "🔑",
        "steps_code": [
            "FIX_STEP_OPEN_GATEWAY",
            "FIX_STEP_GOTO_ADMINISTRATION",
            "FIX_STEP_CHOOSE_STRONG_PASSWORD",
            "FIX_STEP_SAVE_AND_RELOGIN"
        ]
    },
    "telnet_open": {
        "id": "FIX_DISABLE_TELNET",
        "title_code": "f3t",
        "desc_code": "f3d",
        "gain": 20,
        "estimated_time": "1 min",
        "svg_icon": "🚪",
        "steps_code": [
            "FIX_STEP_OPEN_ROUTER_SERVICES",
            "FIX_STEP_FIND_TELNET_OPTION",
            "FIX_STEP_UNCHECK_TELNET_SAVE"
        ]
    },
    "open_wifi": {
        "id": "FIX_ENABLE_WIFI_ENCRYPTION",
        "title_code": "cWifi",
        "desc_code": "fWifiD",
        "gain": 25,
        "estimated_time": "3 min",
        "svg_icon": "📶",
        "steps_code": [
            "FIX_STEP_OPEN_WIRELESS_SETTINGS",
            "FIX_STEP_SELECT_WPA2_OR_WPA3",
            "FIX_STEP_ENTER_STRONG_PASSPHRASE"
        ]
    },
    "wep_wifi": {
        "id": "FIX_UPGRADE_FROM_WEP",
        "title_code": "cWifi",
        "desc_code": "fWepD",
        "gain": 20,
        "estimated_time": "3 min",
        "svg_icon": "📶",
        "steps_code": [
            "FIX_STEP_OPEN_WIRELESS_SECURITY",
            "FIX_STEP_SWITCH_TO_WPA2_AES",
            "FIX_STEP_SAVE_AND_RECONNECT"
        ]
    },
    "wps_enabled": {
        "id": "FIX_TURN_OFF_WPS",
        "title_code": "f2t",
        "desc_code": "f2d",
        "gain": 10,
        "estimated_time": "2 min",
        "svg_icon": "🔓",
        "steps_code": [
            "FIX_STEP_OPEN_WIFI_ADVANCED",
            "FIX_STEP_FIND_WPS_PIN_TOGGLE",
            "FIX_STEP_DISABLE_WPS"
        ]
    },
    "admin_http_only": {
        "id": "FIX_ENABLE_HTTPS_ADMIN",
        "title_code": "cAdmin",
        "desc_code": "fHttpOnlyD",
        "gain": 10,
        "estimated_time": "2 min",
        "svg_icon": "🔒",
        "steps_code": [
            "FIX_STEP_SYSTEM_MANAGEMENT",
            "FIX_STEP_ENABLE_HTTPS_ONLY",
            "FIX_STEP_APPLY_SETTINGS"
        ]
    },
    "upnp_open": {
        "id": "FIX_DISABLE_UPNP",
        "title_code": "cPorts",
        "desc_code": "fUpnpD",
        "gain": 5,
        "estimated_time": "1 min",
        "svg_icon": "⚙️",
        "steps_code": [
            "FIX_STEP_ROUTER_ADVANCED_NAT",
            "FIX_STEP_TURN_OFF_UPNP",
            "FIX_STEP_SAVE_SETTINGS"
        ]
    },
    "tr069_open": {
        "id": "FIX_DISABLE_TR069",
        "title_code": "cPorts",
        "desc_code": "fTr069D",
        "gain": 5,
        "estimated_time": "2 min",
        "svg_icon": "📡",
        "steps_code": [
            "FIX_STEP_ROUTER_CWMP_SETTINGS",
            "FIX_STEP_DISABLE_REMOTE_MANAGEMENT",
            "FIX_STEP_SAVE_SETTINGS"
        ]
    },
    "suspicious_dns": {
        "id": "FIX_SET_TRUSTED_DNS",
        "title_code": "dns",
        "desc_code": "fDnsD",
        "gain": 10,
        "estimated_time": "2 min",
        "svg_icon": "🌍",
        "steps_code": [
            "FIX_STEP_NETWORK_DNS_SETTINGS",
            "FIX_STEP_ENTER_1111_OR_8888",
            "FIX_STEP_SAVE_AND_FLUSH"
        ]
    }
}

def generate_remediation_fixes(deductions: Dict[str, int]) -> tuple[List[FixItem], List[FixItem]]:
    """Generates remediation items sorted by points gain, returning (top_3, all_fixes)."""
    fixes_list: List[FixItem] = []
    
    # If deductions exist, map them
    for key in deductions:
        if key in ALL_POSSIBLE_FIXES:
            item = ALL_POSSIBLE_FIXES[key]
            fixes_list.append(FixItem(
                id=item["id"],
                title_code=item["title_code"],
                desc_code=item["desc_code"],
                gain=item["gain"],
                estimated_time=item["estimated_time"],
                svg_icon=item["svg_icon"],
                steps_code=item["steps_code"]
            ))
            
    # If deductions is empty (perfect score), provide proactive best practices
    if not fixes_list:
        fixes_list = [
            FixItem(
                id="FIX_CHANGE_ADMIN_PASSWORD",
                title_code="f1t",
                desc_code="f1d",
                gain=5,
                estimated_time="2 min",
                svg_icon="🔑",
                steps_code=["FIX_STEP_CHOOSE_STRONG_PASSWORD"]
            ),
            FixItem(
                id="FIX_TURN_OFF_WPS",
                title_code="f2t",
                desc_code="f2d",
                gain=5,
                estimated_time="1 min",
                svg_icon="🔓",
                steps_code=["FIX_STEP_DISABLE_WPS"]
            ),
            FixItem(
                id="FIX_CHECK_FIRMWARE",
                title_code="cFw",
                desc_code="fFwD",
                gain=5,
                estimated_time="5 min",
                svg_icon="🧩",
                steps_code=["FIX_STEP_CHECK_FIRMWARE_UPDATE"]
            ),
        ]
        
    # Sort descending by gain
    fixes_list.sort(key=lambda x: x.gain, reverse=True)
    top_3 = fixes_list[:3]
    return top_3, fixes_list
