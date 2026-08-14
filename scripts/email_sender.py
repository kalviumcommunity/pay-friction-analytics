# scripts/email_sender.py
import smtplib
import os
from email.mime.text import MIMEText

# Optional: Load dotenv if installed (pip install python-dotenv) to read .env file locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def send_report(report_text, recipient):
    """
    Sends the generated report via email using smtplib.
    Implements non-blocking error handling to prevent application crashes.
    """
    # Task 5: Read from environment variables securely
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASSWORD")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    
    # Guard clause if environment variables are missing
    if not sender or not password:
        print("⚠️ WARNING: Email credentials not configured in environment variables. Skipping email delivery.")
        return False

    # Construct the Email structure
    msg = MIMEText(report_text)
    msg["Subject"] = "Action Required: Weekly Analytics Report"
    msg["From"] = sender
    msg["To"] = recipient

    # Task 4: Non-Blocking Error Handling
    try:
        print(f"Attempting to connect to {smtp_server}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"✅ SUCCESS: Email report sent to {recipient}")
        return True
        
    except Exception as e:
        # We catch the error, log it to the console, and return False.
        # We DO NOT use 'raise e', which would crash the Streamlit app.
        print(f"❌ ERROR: Email delivery failed. Details: {str(e)}")
        return False

# Built-in test block to verify the non-blocking error handler
if __name__ == "__main__":
    print("Testing email sender (expecting intentional failure if .env is not set up):")
    success = send_report("Test report", "test@example.com")
    print(f"Function returned: {success}")