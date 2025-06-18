import os.path
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import openai
from openai import OpenAI
from transformers import pipeline

# ---- CONFIGURATION ----
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
GMAIL_USER = 'email@gmail.com'                               #Email to be sent to
GMAIL_PASS = 'password'                                      #alt password, obtained from https://myaccount.google.com/apppasswords
OPENAI_API_KEY = 'sk-...'                                    # api key obtained from https://platform.openai.com/account/api-keys

# ---- EMAIL ----
def send_email_schedule(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        server.quit()
        print("✅ Email sent!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# ---- AI SUMMARY ----

def summarize_schedule(text):
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print("❌ Summarization error:", e)
        return "Summary not available."


# ---- CALENDAR FETCH ----
def get_today_events():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow()
    start = now.isoformat() + 'Z'
    end = (now + datetime.timedelta(days=1)).isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary', timeMin=start,
                                          timeMax=end, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    schedule_lines = []

    if not events:
        schedule_lines.append("No events found.")
    else:
        for event in events:
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            schedule_lines.append(f"- {start_time} → {summary}")

    schedule_text = "\n".join(schedule_lines)
    ai_summary = summarize_schedule(schedule_text)

    full_email = f"🗓️ Raw Schedule:\n\n{schedule_text}\n\n🤖 AI Summary:\n\n{ai_summary}"
    send_email_schedule(GMAIL_USER, "📅 Your Daily Calendar Summary", full_email)

if __name__ == '__main__':
    get_today_events()
