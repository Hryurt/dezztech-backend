"""Email service using SendGrid.

In development environment, emails are logged instead of sent.
"""

from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


async def send_email(*, to_email: str, subject: str, html_content: str) -> None:
    """Send an email via SendGrid. Logs instead in development.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML body content
    """
    if settings.ENVIRONMENT == "development":
        logger.info(
            f"[DEV] Email not sent. To: {to_email} | Subject: {subject}"
        )
        logger.debug(f"[DEV] Email body:\n{html_content}")
        return

    if not settings.SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not configured, skipping email send")
        return

    import sendgrid
    from sendgrid.helpers.mail import Content, Email, Mail, To

    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    from_email = Email(settings.SENDGRID_FROM_EMAIL)
    to = To(to_email)
    content = Content("text/html", html_content)
    mail = Mail(from_email, to, subject, content)

    response = sg.client.mail.send.post(request_body=mail.get())
    logger.info(
        f"Email sent to {to_email} | Status: {response.status_code}"
    )


async def send_company_invitation_email(
    *,
    to_email: str,
    company_name: str,
    inviter_name: str,
    role: str,
    invite_token: str,
) -> None:
    """Send a company invitation email.

    Args:
        to_email: Invited user's email
        company_name: Name of the company
        inviter_name: Name of the person who sent the invite
        role: Role being assigned
        invite_token: Token for accepting the invitation
    """
    accept_url = f"{settings.FRONTEND_URL}/invite/accept?token={invite_token}"

    html_content = f"""
    <h2>Company Invitation</h2>
    <p><strong>{inviter_name}</strong> has invited you to join
    <strong>{company_name}</strong> as <strong>{role}</strong>.</p>
    <p><a href="{accept_url}">Click here to accept the invitation</a></p>
    <p>This invitation expires in 7 days.</p>
    <p>If you did not expect this invitation, you can safely ignore this email.</p>
    """

    await send_email(
        to_email=to_email,
        subject=f"You've been invited to {company_name} on Dezztech",
        html_content=html_content,
    )
