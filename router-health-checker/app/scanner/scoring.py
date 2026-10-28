"""Security scoring engine out of 100."""
from typing import Dict, Any, Tuple

def calculate_router_score(
    wifi_grade: str,
    admin_info: Dict[str, Any],
    open_ports: list,
    dns_info: Dict[str, Any],
    wps_enabled: bool = False
) -> Tuple[int, str, Dict[str, Any]]:
    """
    Compute transparent security score from 100 with clear weights.
    Returns (score, verdict_string, deductions_dict).
    """
    score = 100
    deductions = {}
    
    # 1. Wi-Fi Security
    if wifi_grade == "open":
        score -= 25
        deductions["open_wifi"] = 25
    elif wifi_grade == "wep":
        score -= 20
        deductions["wep_wifi"] = 20
    elif wifi_grade in ["wpa", "wpa2"]:
        # Standard good security
        pass
    elif wifi_grade == "wpa3":
        # Best current standard
        pass

    # 2. Admin Credentials
    if admin_info.get("default_login_detected", False):
        score -= 25
        deductions["default_admin_password"] = 25
        
    # 3. Plain HTTP Only Admin
    if admin_info.get("is_plain_http_only", False):
        score -= 10
        deductions["admin_http_only"] = 10

    # 4. Dangerous Ports
    open_port_numbers = [p["port"] for p in open_ports if p.get("is_open", False)]
    
    if 23 in open_port_numbers:  # Telnet
        score -= 20
        deductions["telnet_open"] = 20
        
    if 1900 in open_port_numbers:  # UPnP
        score -= 5
        deductions["upnp_open"] = 5
        
    if 7547 in open_port_numbers:  # TR-069
        score -= 5
        deductions["tr069_open"] = 5

    # 5. WPS
    if wps_enabled or wifi_grade == "wep":
        score -= 10
        deductions["wps_enabled"] = 10

    # 6. DNS
    if dns_info.get("has_suspicious_dns", False):
        score -= 10
        deductions["suspicious_dns"] = 10

    # Clamp 0 - 100
    final_score = max(0, min(100, score))
    
    # Verdict determination
    if final_score >= 90:
        verdict = "excellent"
    elif final_score >= 75:
        verdict = "good"
    elif final_score >= 50:
        verdict = "fair"
    else:
        verdict = "risky"
        
    return final_score, verdict, deductions
