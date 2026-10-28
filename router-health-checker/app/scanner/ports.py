"""Socket-based non-intrusive port scanner with timeout and concurrency."""
import socket
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List

TARGET_PORTS = [
    {"port": 21, "service": "FTP", "risk": "medium", "description": "Unencrypted File Transfer"},
    {"port": 22, "service": "SSH", "risk": "low", "description": "Encrypted Remote Administration"},
    {"port": 23, "service": "Telnet", "risk": "high", "description": "Unencrypted Remote Administration (Dangerous)"},
    {"port": 53, "service": "DNS", "risk": "low", "description": "Local Domain Name Resolution"},
    {"port": 80, "service": "HTTP", "risk": "medium", "description": "Plain Web Admin Interface"},
    {"port": 443, "service": "HTTPS", "risk": "low", "description": "Encrypted Web Admin Interface"},
    {"port": 1900, "service": "UPnP", "risk": "medium", "description": "Universal Plug and Play (Auto Port Forwarding)"},
    {"port": 7547, "service": "TR-069", "risk": "high", "description": "CWMP Remote ISP Management"},
    {"port": 8080, "service": "HTTP-Alt", "risk": "medium", "description": "Secondary Web Interface"},
]

def check_single_port(ip: str, port_info: Dict[str, Any], timeout: float = 0.5) -> Dict[str, Any]:
    port = port_info["port"]
    is_open = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        res = sock.connect_ex((ip, port))
        if res == 0:
            is_open = True
    except Exception:
        is_open = False
    finally:
        sock.close()
        
    return {
        "port": port,
        "service": port_info["service"],
        "is_open": is_open,
        "risk": port_info["risk"],
        "description": port_info["description"]
    }

def scan_ports(ip: str, timeout: float = 0.5) -> List[Dict[str, Any]]:
    """Scan strictly the bounded list of 9 ports using a thread pool."""
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(check_single_port, ip, p, timeout) for p in TARGET_PORTS]
        for f in futures:
            try:
                results.append(f.result())
            except Exception:
                pass
    return sorted(results, key=lambda x: x["port"])
