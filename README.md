# 📅 calendar_assistant

A smart assistant that reads your Google Calendar, summarizes your daily schedule using an offline AI model, and emails it to you.

---

## 🚀 Features

- 🔒 Authenticates with your Google Calendar
- 🗓️ Fetches all events for today
- 🤖 Summarizes them locally with Hugging Face's BART model (no API key needed)
- 📧 Sends the result to your Gmail via SMTP
- 💻 No cloud AI billing, works completely free after setup

---

## 🛠 Requirements

Install required libraries:

```bash
pip install -r requirements.txt
