"""Read-only admin page reachability and optional default credential test."""
import requests
from typing import Dict, Any, List

COMMON_DEFAULT_CREDENTIALS = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "1234"),
]

def check_admin_page(gateway_ip: str, test_defaults: bool = False) -> Dict[str, Any]:
    """Test router web administration interface status and encryption."""
    http_url = f"http://{gateway_ip}"
    https_url = f"https://{gateway_ip}"
    
    http_accessible = False
    https_accessible = False
    server_header = "Unknown"
    default_login_detected = False
    
    # 1. Test HTTP
    try:
        r_http = requests.get(http_url, timeout=1.2, allow_redirects=True, verify=False)
        if r_http.status_code in [200, 401, 403]:
            http_accessible = True
            server_header = r_http.headers.get("Server", server_header)
    except Exception:
        http_accessible = False
        
    # 2. Test HTTPS
    try:
        r_https = requests.get(https_url, timeout=1.2, allow_redirects=True, verify=False)
        if r_https.status_code in [200, 401, 403]:
            https_accessible = True
            if server_header == "Unknown":
                server_header = r_https.headers.get("Server", server_header)
    except Exception:
        https_accessible = False
        
    # 3. Optional opt-in check for default credentials (strictly read-only and non-intrusive)
    if test_defaults and (http_accessible or https_accessible):
        target_url = https_url if https_accessible else http_url
        for u, p in COMMON_DEFAULT_CREDENTIALS:
            try:
                auth_resp = requests.get(target_url, auth=(u, p), timeout=1.0, verify=False)
                # If HTTP 200 returned after basic auth request
                if auth_resp.status_code == 200 and ("logout" in auth_resp.text.lower() or "setup" in auth_resp.text.lower() or "wizard" in auth_resp.text.lower()):
                    default_login_detected = True
                    break
            except Exception:
                pass
                
    return {
        "http_accessible": http_accessible,
        "https_accessible": https_accessible,
        "is_plain_http_only": http_accessible and not https_accessible,
        "server_header": server_header[:40],
        "default_login_detected": default_login_detected
    }
