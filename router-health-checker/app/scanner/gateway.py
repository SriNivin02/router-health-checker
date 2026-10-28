"""Default gateway IP auto-detection and private IP safety verification."""
import ipaddress
import platform
import subprocess
import re
from typing import Optional

def is_private_ip(ip_str: str) -> bool:
    """Verify strictly that the target IP belongs to an RFC 1918 private or link-local range."""
    try:
        ip = ipaddress.ip_address(ip_str.strip())
        if ip.is_loopback:
            return False
        return ip.is_private or ip.is_link_local
    except ValueError:
        return False

def validate_target(target: str) -> tuple[bool, str]:
    cleaned = target.strip()
    try:
        ip = ipaddress.ip_address(cleaned)
    except ValueError:
        return False, "INVALID_IP_FORMAT"

    if ip.is_loopback or not (ip.is_private or ip.is_link_local):
        return False, "IP_NOT_PRIVATE"

    return True, ""


def get_default_gateway() -> str:
    """Cross-platform default gateway IP auto-discovery using safe subprocess without shell=True."""
    os_type = platform.system().lower()
    gateway_ip: Optional[str] = None
    
    try:
        if os_type == "windows":
            # Run route print 0.0.0.0
            proc = subprocess.run(
                ["route", "print", "0.0.0.0"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            for line in proc.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
                    candidate = parts[2]
                    if is_private_ip(candidate):
                        gateway_ip = candidate
                        break
            
            # Alternative: ipconfig
            if not gateway_ip:
                proc2 = subprocess.run(
                    ["ipconfig"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    check=False
                )
                for line in proc2.stdout.splitlines():
                    if "Default Gateway" in line or "default gateway" in line.lower():
                        match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                        if match and is_private_ip(match.group(1)):
                            gateway_ip = match.group(1)
                            break
                            
        elif os_type == "linux":
            proc = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            for line in proc.stdout.splitlines():
                parts = line.strip().split()
                if "via" in parts:
                    idx = parts.index("via")
                    if idx + 1 < len(parts):
                        candidate = parts[idx + 1]
                        if is_private_ip(candidate):
                            gateway_ip = candidate
                            break
                            
        elif os_type == "darwin":  # macOS
            proc = subprocess.run(
                ["netstat", "-rn", "-f", "inet"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            for line in proc.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2 and parts[0] == "default":
                    candidate = parts[1]
                    if is_private_ip(candidate):
                        gateway_ip = candidate
                        break
    except Exception:
        pass
    
    # Safe default fallback if router gateway cannot be parsed
    if not gateway_ip or not is_private_ip(gateway_ip):
        gateway_ip = "192.168.1.1"
        
    return gateway_ip
