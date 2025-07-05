import os
import pickle
import base64
from datetime import datetime
from email.mime.text import MIMEText

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# ── CONFIGURATION ─────────────────────────────────────
SPREADSHEET_TITLE = "Special Days Sheet"      # Google Sheet title (not tab name)
GMAIL_CREDENTIALS = "credentials.json"        # Gmail OAuth2 credentials
SHEET_CREDENTIALS = "credentials_sheet.json"  # Google Sheets service account
TOKEN_FILE        = "token.pickle"            # Gmail token (auto-generated)

RECIPIENTS = [
    "kumaramitthakur563@gmail.com",
    "thakur.ghanshyam058@gmail.com",
    "sudhakumari9473@gmail.com",
    "amitvlogs9473@gamil.com"
]

GMAIL_SCOPES  = ["https://www.googleapis.com/auth/gmail.send"]
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
# ──────────────────────────────────────────────────────


# ── Load events from Google Sheets ────────────────────
def load_events():
    credentials = Credentials.from_service_account_file(
        SHEET_CREDENTIALS, scopes=SHEETS_SCOPES
    )
    client = gspread.authorize(credentials)

    try:
        SPREADSHEET_ID = "1iL3No0TCz1A72sj23yFspLHlfPplxu9q1kQLeNM4vIU"
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if "Date" not in df.columns or "Occasion" not in df.columns:
            raise ValueError("Sheet must have 'Date' and 'Occasion' columns.")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        return df
    except Exception as e:
        print(f"❌ Failed to load Google Sheet: {e}")
        return pd.DataFrame()


# ── Authenticate Gmail API ────────────────────────────
def authenticate_gmail():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS, GMAIL_SCOPES)
            creds = flow.run_local_server(port=8765, open_browser=True)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


# ── Send email via Gmail API ──────────────────────────
def send_email(service, recipient, subject, body):
    message = MIMEText(body)
    message['to'] = recipient
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()


# ── MAIN EXECUTION ────────────────────────────────────
def main():
    df = load_events()
    if df.empty:
        print("No data to process.")
        return

    today = datetime.today().date()
    events_today = df[df['Date'] == today]

    if events_today.empty:
        print(f"No events for today ({today}).")
        return

    service = authenticate_gmail()

    for _, row in events_today.iterrows():
        occasion = row["Occasion"]
        subject = f"Reminder: {occasion}"
        body = (
            f"Hello,\n\n"
            f"This is a reminder that today ({today}) is {occasion}.\n\n"
            f"Best regards,\nYour Name"
        )

        for recipient in RECIPIENTS:
            try:
                send_email(service, recipient, subject, body)
                print(f"✓ Email sent to {recipient} for '{occasion}'.")
            except Exception as e:
                print(f"✗ Failed to send email to {recipient}. Error: {e}")


if __name__ == "__main__":
    main()
