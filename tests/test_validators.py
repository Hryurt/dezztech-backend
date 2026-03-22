"""Unit tests for validators (no DB needed)."""

import pytest

from src.core.security.email_policy import validate_business_email
from src.core.security.password_policy import validate_password_strength


class TestEmailPolicy:
    """Test business email restriction."""

    def test_gmail_blocked(self):
        with pytest.raises(ValueError):
            validate_business_email("user@gmail.com")

    def test_hotmail_blocked(self):
        with pytest.raises(ValueError):
            validate_business_email("user@hotmail.com")

    def test_yahoo_blocked(self):
        with pytest.raises(ValueError):
            validate_business_email("user@yahoo.com")

    def test_outlook_blocked(self):
        with pytest.raises(ValueError):
            validate_business_email("user@outlook.com")

    def test_yandex_blocked(self):
        with pytest.raises(ValueError):
            validate_business_email("user@yandex.com")

    def test_icloud_blocked(self):
        with pytest.raises(ValueError):
            validate_business_email("user@icloud.com")

    def test_protonmail_blocked(self):
        with pytest.raises(ValueError):
            validate_business_email("user@protonmail.com")

    def test_business_email_allowed(self):
        validate_business_email("user@dezztech.com")

    def test_custom_domain_allowed(self):
        validate_business_email("admin@mycompany.com.tr")

    def test_case_insensitive(self):
        with pytest.raises(ValueError):
            validate_business_email("user@GMAIL.COM")


class TestPasswordPolicy:
    """Test password strength validation."""

    def test_valid_password(self):
        validate_password_strength("Test1234!")

    def test_too_short(self):
        with pytest.raises(ValueError):
            validate_password_strength("Te1!")

    def test_no_uppercase(self):
        with pytest.raises(ValueError):
            validate_password_strength("test1234!")

    def test_no_lowercase(self):
        with pytest.raises(ValueError):
            validate_password_strength("TEST1234!")

    def test_no_digit(self):
        with pytest.raises(ValueError):
            validate_password_strength("TestTest!")

    def test_no_special_char(self):
        with pytest.raises(ValueError):
            validate_password_strength("Test12345")
