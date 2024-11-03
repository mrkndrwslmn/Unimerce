import smtplib
from email.message import EmailMessage

def send_email(subject, recipient, body, sender="your_email@gmail.com", password="your_password"):
    """Send an email using SMTP."""
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
