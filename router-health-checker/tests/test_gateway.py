"""
tests/test_gateway.py – Tests for IP validation
"""
import pytest
from app.scanner.gateway import is_private_ip, validate_target


class TestIsPrivateIp:

    def test_192_168_range(self):
        assert is_private_ip("192.168.1.1")
        assert is_private_ip("192.168.0.1")
        assert is_private_ip("192.168.255.255")

    def test_10_range(self):
        assert is_private_ip("10.0.0.1")
        assert is_private_ip("10.255.255.255")

    def test_172_range(self):
        assert is_private_ip("172.16.0.1")
        assert is_private_ip("172.31.255.255")

    def test_link_local(self):
        assert is_private_ip("169.254.1.1")

    def test_public_ip_rejected(self):
        assert not is_private_ip("8.8.8.8")
        assert not is_private_ip("1.1.1.1")
        assert not is_private_ip("93.184.216.34")

    def test_loopback_not_private_range(self):
        # loopback is not in our defined private ranges
        assert not is_private_ip("127.0.0.1")

    def test_invalid_format(self):
        assert not is_private_ip("not-an-ip")
        assert not is_private_ip("256.256.256.256")


class TestValidateTarget:

    def test_valid_private_ip(self):
        ok, err = validate_target("192.168.1.1")
        assert ok
        assert err == ""

    def test_public_ip_rejected(self):
        ok, err = validate_target("8.8.8.8")
        assert not ok
        assert err == "IP_NOT_PRIVATE"

    def test_invalid_format(self):
        ok, err = validate_target("not-an-ip")
        assert not ok
        assert err == "INVALID_IP_FORMAT"

    def test_hostname_rejected(self):
        ok, err = validate_target("router.local")
        assert not ok

    def test_cidr_rejected(self):
        ok, err = validate_target("192.168.1.0/24")
        assert not ok

    def test_whitespace_stripped(self):
        ok, err = validate_target("  192.168.1.1  ")
        assert ok
