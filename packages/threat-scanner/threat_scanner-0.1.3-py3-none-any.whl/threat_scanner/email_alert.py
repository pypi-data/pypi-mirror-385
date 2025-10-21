import os
import sys
from .utils import get_threat_level_color

# Import lazily
_SendGridAPIClient = None
_Mail = None

def _import_sendgrid():
    global _SendGridAPIClient, _Mail
    if _SendGridAPIClient is None or _Mail is None:
        try:
            from sendgrid import SendGridAPIClient as _sg
            from sendgrid.helpers.mail import Mail as _m
            _SendGridAPIClient = _sg
            _Mail = _m
        except ImportError:
            raise ImportError("sendgrid is required for email alerts. Please install it: pip install sendgrid")
    return _SendGridAPIClient, _Mail

def send_threat_email(
    api_key: str,
    to_email: str,
    from_email: str,
    video_ref: str, # Path or GCS URI
    threat_label: str,
    confidence: float
):
    """Sends a formatted threat alert email using SendGrid."""
    SendGridAPIClient, Mail = _import_sendgrid()

    if not api_key:
        print("Error: SendGrid API key is missing.", file=sys.stderr)
        return False
    if not to_email:
         print("Error: Recipient email address is missing.", file=sys.stderr)
         return False
    if not from_email:
         print("Error: Sender email address is missing.", file=sys.stderr)
         return False

    confidence_percent = confidence * 100
    color = get_threat_level_color(confidence)

    subject = f"Threat Detection Alert: {threat_label.capitalize()}"

    body = f"""
    <html>
    <body>
        <h2>Threat Detection Alert</h2>
        <p>Dear User,</p>
        <p>A potential threat has been detected during video analysis.</p>
        <hr>
        <p><strong>Video Source:</strong> {video_ref}</p>
        <p><strong>Detected Threat:</strong> {threat_label.capitalize()}</p>
        <p><strong>Confidence Level:</strong> <strong style="color:{color};">{confidence_percent:.2f}%</strong></p>
        <hr>
        <p>Please review the source video for verification.</p>
        <p><em>This is an automated alert from the Threat Scanner system.</em></p>
    </body>
    </html>
    """

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=body
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"Alert email sent to {to_email}. Status Code: {response.status_code}")
        return response.status_code in [200, 202] # 202 is Accepted
    except ImportError as e:
         print(f"Error: {e}", file=sys.stderr)
         return False
    except Exception as e:
        print(f"Error sending email via SendGrid: {e}", file=sys.stderr)
        # Check if the error response from SendGrid is available
        if hasattr(e, 'body'):
             print(f"SendGrid Error Body: {e.body}", file=sys.stderr)
        return False