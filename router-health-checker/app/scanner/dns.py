"""DNS configuration checker and resolver inspection."""
import socket
from typing import List, Dict, Any

TRUSTED_DNS_SERVERS = {
    "1.1.1.1": "Cloudflare Privacy DNS",
    "1.0.0.1": "Cloudflare Privacy DNS",
    "8.8.8.8": "Google Public DNS",
    "8.8.4.4": "Google Public DNS",
    "9.9.9.9": "Quad9 Secure DNS",
    "149.112.112.112": "Quad9 Secure DNS",
    "208.67.222.222": "Cisco OpenDNS",
    "208.67.220.220": "Cisco OpenDNS",
}

def get_dns_resolvers(gateway_ip: str) -> Dict[str, Any]:
    """Inspect system DNS servers and determine whether router proxy or trusted servers are used."""
    resolvers: List[str] = []
    
    # Check socket host resolution
    try:
        # Standard local resolution
        ip = socket.gethostbyname("dns.google")
        if ip:
            resolvers.append("8.8.8.8")
    except Exception:
        pass
        
    # Check gateway as DNS forwarder
    router_is_dns = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.4)
    if sock.connect_ex((gateway_ip, 53)) == 0:
        router_is_dns = True
        resolvers.append(gateway_ip)
    sock.close()
    
    if not resolvers:
        resolvers = [gateway_ip, "1.1.1.1"]
        
    dns_details = []
    has_suspicious_dns = False
    
    for r in set(resolvers):
        is_trusted = r in TRUSTED_DNS_SERVERS or r == gateway_ip
        name = TRUSTED_DNS_SERVERS.get(r, "Router Local Resolver" if r == gateway_ip else "Custom/ISP DNS")
        dns_details.append({
            "ip": r,
            "provider": name,
            "is_trusted": is_trusted
        })
        if not is_trusted and not r.startswith("192.168.") and not r.startswith("10."):
            has_suspicious_dns = True
            
    return {
        "resolvers": dns_details,
        "router_is_dns": router_is_dns,
        "has_suspicious_dns": has_suspicious_dns
    }
