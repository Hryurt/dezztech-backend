"""Business email policy validation.

Only business emails are allowed for registration. Common personal email providers are blocked.
"""

BLOCKED_EMAIL_DOMAINS: set[str] = {
    # Google
    "gmail.com",
    "googlemail.com",
    # Microsoft
    "hotmail.com",
    "hotmail.co.uk",
    "hotmail.fr",
    "hotmail.de",
    "live.com",
    "live.co.uk",
    "msn.com",
    "outlook.com",
    "outlook.co.uk",
    # Yahoo
    "yahoo.com",
    "yahoo.co.uk",
    "yahoo.com.tr",
    "yahoo.fr",
    "yahoo.de",
    "ymail.com",
    "rocketmail.com",
    # Yandex
    "yandex.com",
    "yandex.ru",
    "yandex.com.tr",
    # Apple
    "icloud.com",
    "me.com",
    "mac.com",
    # Others
    "aol.com",
    "mail.com",
    "zoho.com",
    "protonmail.com",
    "proton.me",
    "tutanota.com",
    "gmx.com",
    "gmx.de",
    "web.de",
    "mail.ru",
    "inbox.com",
}

EMAIL_POLICY_ERROR_MESSAGE = "Please use a business email address. Personal email providers are not allowed."


def validate_business_email(email: str) -> None:
    """Validate that the email is a business email, not a personal provider.

    Args:
        email: Email address to validate

    Raises:
        ValueError: If email domain is in the blocked list
    """
    domain = email.rsplit("@", 1)[-1].lower()
    if domain in BLOCKED_EMAIL_DOMAINS:
        raise ValueError(EMAIL_POLICY_ERROR_MESSAGE)
