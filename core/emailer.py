import yagmail
import json
import os
from dotenv import load_dotenv
from logging_config import logger

load_dotenv()

USER_FILE = "resource/user.json"
NOTE_FILE = 'resource/notes.json'
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def load_base_info():
    with open(NOTE_FILE, "r", encoding="utf-8") as f:
        notes = json.load(f)

    with open(USER_FILE, "r", encoding="utf-8") as f:
        user = json.load(f)

    today_note = notes[-1] #latest note
    receiver=user['email']

    summary_url = "http://localhost:8501/View_Daily_Notes"

    return today_note, receiver, summary_url

def send_reading_reminder():

    note, receiver, _=load_base_info()

    book = note["book"]
    start_page, end_page = note["pages"]
    summary = note["summary"]
    question1 = note["questions"][0]
    question2 = note["questions"][1]
    date = note["date"]

    body = f"""
📖 Reading Reminder for {date}

Hello!

Today, you're scheduled to read {book}, pages {start_page} to {end_page}.

📝 Summary:
{summary}

💭 Questions to consider as you read:
1. {question1}
2. {question2}

Enjoy your reading and reflect deeply!
"""

    subject = f"📚 Reading Reminder: {book} ({start_page}-{end_page})"

    yag = yagmail.SMTP(user=SENDER_EMAIL, password=APP_PASSWORD)
    yag.send(to=receiver, subject=subject, contents=body)
    logger.info(f"Sending reading reminder to {receiver} for book: {book}")

def send_summary_reminder():

    note, receiver, summary_link=load_base_info()

    book = note["book"]
    start_page, end_page = note["pages"]
    date = note["date"]

    body = f"""
📌 Summary Reminder for {date}

Hi!

You've just read {book}, pages {start_page} to {end_page} today.

Please take a moment to reflect and fill out your summary at the link below:

👉 [Click here to complete your summary]({summary_link})

Your reflection helps reinforce your learning. Thank you!

"""

    subject = f"📝 Summary Reminder: {book} ({start_page}-{end_page})"

    yag = yagmail.SMTP(user=SENDER_EMAIL, password=APP_PASSWORD)
    yag.send(to=receiver, subject=subject, contents=body)
    logger.info(f"Summary reminder sent to {receiver} for book: {book}")


if __name__=='__main__':
    send_reading_reminder()
    send_summary_reminder()
