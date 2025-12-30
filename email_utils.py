import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
import os

def send_email(subject: str, body: str, to_email: str, attachment_path: str = None) -> None:
    """
    Send an email using Gmail's SMTP server with an optional attachment.
    """
    from_email = os.getenv('EMAIL_USERNAME')
    email_password = os.getenv('EMAIL_PASSWORD')

    if not from_email or not email_password:
        raise ValueError("Missing email credentials in environment variables")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # If there is an attachment, add it to the email
    if attachment_path:
        try:
            # Open the file in binary mode and attach it
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
                msg.attach(part)
        except Exception as e:
            print(f"Failed to attach file: {e}")

    try:
        # Connect to Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, email_password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
