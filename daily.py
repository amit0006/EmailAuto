import os
import pickle
import base64
from datetime import datetime
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# ── CONFIG ────────────────────────────────────────────
GMAIL_CREDENTIALS = "credentials.json"
TOKEN_FILE        = "token.pickle"

# ✅ 1.  Missing constant added
GMAIL_SCOPES      = ["https://www.googleapis.com/auth/gmail.send"]

RECIPIENTS = [
    "kumaramitthakur563@gmail.com",
    "thakur.ghanshyam058@gmail.com",
    "sudhakumari9473@gmail.com",
    "amitvlogs9473@gmail.com",
]
# ──────────────────────────────────────────────────────


def authenticate_gmail():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS, GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=8765, open_browser=True)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def send_email(service, recipient, subject, body):
    msg = MIMEText(body)
    msg["to"] = recipient
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


def main():
    subject = "Wishing You a Peaceful and Joyful Day ❤️"
    body = (
        "Dear Family,\n\n"
        "Good morning!\nI just wanted to start the day by sending you my love and warm wishes.\n\n"
        "May today bring peace to your heart, smiles to your face, and strength to your spirit.\n Always grateful to have such a beautiful family by my side.\n\n"
        "Take care of yourself and stay happy.\nLove you all! 💖\n\n"
        "With lots of love,\nAmit Kumar Thakur"
    )

    service = authenticate_gmail()

    # ✅ 2.  Send to each recipient individually (or join the list)
    for rcpt in RECIPIENTS:
        send_email(service, rcpt, subject, body)
        print(f"✓ Sent to {rcpt}")


if __name__ == "__main__":
    main()
