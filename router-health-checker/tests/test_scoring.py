"""Tests for the transparent scoring algorithm and remediation logic."""
from app.scanner.scoring import calculate_router_score
from app.scanner.fixes import generate_remediation_fixes

def test_perfect_score():
    score, verdict, deductions = calculate_router_score(
        wifi_grade="wpa3",
        admin_info={"default_login_detected": False, "is_plain_http_only": False},
        open_ports=[{"port": 443, "is_open": True}],
        dns_info={"has_suspicious_dns": False},
        wps_enabled=False
    )
    assert score == 100
    assert verdict == "excellent"
    assert len(deductions) == 0

def test_critical_deductions():
    # Test open wifi (-25), telnet (-20), default admin (-25)
    score, verdict, deductions = calculate_router_score(
        wifi_grade="open",
        admin_info={"default_login_detected": True, "is_plain_http_only": True},
        open_ports=[{"port": 23, "is_open": True}],
        dns_info={"has_suspicious_dns": True},
        wps_enabled=True
    )
    # Deductions: open_wifi 25, default_admin 25, admin_http 10, telnet 20, wps 10, dns 10 = 100
    assert score == 0
    assert verdict == "risky"
    assert "telnet_open" in deductions
    assert "open_wifi" in deductions

def test_top_3_fixes_sorting():
    deductions = {
        "upnp_open": 5,
        "default_admin_password": 25,
        "wps_enabled": 10,
        "telnet_open": 20
    }
    top_3, all_fixes = generate_remediation_fixes(deductions)
    assert len(top_3) == 3
    # Sorted descending by gain
    assert top_3[0].gain >= top_3[1].gain >= top_3[2].gain
    assert top_3[0].id == "FIX_CHANGE_ADMIN_PASSWORD"
