"""
tests/test_auth.py – Tests for authentication helpers
"""
import pytest
from app.security.auth import (
    hash_password,
    verify_password,
    is_common_password,
    create_session_token,
    decode_session_token,
    generate_recovery_code,
)


class TestPasswordHashing:

    def test_hash_and_verify(self):
        plain = "securepassword123"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correctpassword1")
        assert not verify_password("wrongpassword123", hashed)

    def test_hash_is_not_plaintext(self):
        plain = "mypassword123"
        hashed = hash_password(plain)
        assert plain not in hashed

    def test_different_hashes_for_same_password(self):
        plain = "samepassword123"
        h1 = hash_password(plain)
        h2 = hash_password(plain)
        # Argon2 uses random salts so hashes differ
        assert h1 != h2

    def test_empty_password_can_be_hashed(self):
        # Empty passwords are allowed at hashing level; validation is elsewhere
        hashed = hash_password("")
        assert verify_password("", hashed)


class TestCommonPasswords:

    def test_common_password_detected(self):
        assert is_common_password("password")
        assert is_common_password("12345678")
        assert is_common_password("admin123")

    def test_strong_password_not_common(self):
        assert not is_common_password("r0uT3r#S3cur3!")
        assert not is_common_password("XyZ987AbC!@#unique")

    def test_case_insensitive(self):
        assert is_common_password("PASSWORD")
        assert is_common_password("Admin123")


class TestSessionTokens:

    def test_create_and_decode(self):
        user_id = "test-user-123"
        token = create_session_token(user_id)
        decoded = decode_session_token(token, max_age=300)
        assert decoded == user_id

    def test_tampered_token_fails(self):
        token = create_session_token("user-456")
        tampered = token[:-5] + "XXXXX"
        decoded = decode_session_token(tampered, max_age=300)
        assert decoded is None

    def test_expired_token_fails(self):
        token = create_session_token("user-789")
        # Use max_age=0 to force expiry
        decoded = decode_session_token(token, max_age=0)
        assert decoded is None


class TestRecoveryCode:

    def test_generates_plain_and_hash(self):
        plain, hashed = generate_recovery_code()
        assert len(plain) > 0
        assert len(hashed) > 0
        assert plain != hashed

    def test_plain_verifies_against_hash(self):
        plain, hashed = generate_recovery_code()
        assert verify_password(plain, hashed)

    def test_different_codes_each_time(self):
        plain1, _ = generate_recovery_code()
        plain2, _ = generate_recovery_code()
        assert plain1 != plain2
