import json
import os
import fitz  # PyMuPDF
import requests
import re
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from logging_config import logger

BOOK_DIR = "resource/book_dir"
COVER_DIR = "resource/covers"
METADATA_DIR = "resource/metadata"
USER_FILE = "resource/user.json"
NOTE_FILE = 'resource/notes.json'

API_URL = 'https://openrouter.ai/api/v1/chat/completions'
load_dotenv()
API_KEY = os.getenv("API_KEY")


def load_pages(task_data):
    
    current_chapter_plan = task_data['current_chapter_plan']
    current_page = task_data['current_page']
    metadata = task_data['metadata']

    chapter_idx, plan_idx = current_chapter_plan
    chapter = metadata[chapter_idx]
    page_count = chapter['page_per_day'][plan_idx]

    start_page = current_page
    end_page = start_page + page_count - 1  # inclusive
    return (start_page,end_page)

def load_text(current_book, pages):
    
    start_page,end_page=pages[0],pages[1]
    book_path = os.path.join(BOOK_DIR, f"{current_book}.pdf")

    doc = fitz.open(book_path)
    text = ''
    for i in range(start_page - 1, end_page):  # 0-based indexing
        if i < len(doc):
            text += doc[i].get_text()
    return text.strip()

def ask_llm(text, max_retries=5):
    logger.info("Starting LLM call to generate questions and summary...")  

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # --- First round: Question Generation ---
    prompt_q = (
        "Please read the following text and extract two core questions.\n"
        "The format must be strictly as follows:\n"
        "1. [First question]\n"
        "2. [Second question]\n\n"
        "Do not include any explanation or additional content.\n\n"
        f"Text:\n{text}"
    )
    payload_q = {
        "model": "z-ai/glm-4.5-air:free",
        "messages": [
            {"role": "user", "content": prompt_q}
        ]
    }

    for _ in range(max_retries):
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload_q))
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            questions = re.findall(r"\d\.\s*(.+)", content)
            if len(questions) >= 2:
                break
        time.sleep(1)
    else:
        logger.warning("Question generation failed after max retries.")
        return None, None  # Exceeded max retries

    # --- Second round: Summary Generation ---
    prompt_s = (
        "Please read the following text and provide a concise summary.\n"
        "Limit the summary to no more than three sentences.\n"
        "Do not include any extra explanation or formatting—only return the summary itself.\n\n"
        f"Text:\n{text}"
    )
    payload_s = {
        "model": "z-ai/glm-4.5-air:free",
        "messages": [
            {"role": "user", "content": prompt_s}
        ]
    }

    for _ in range(max_retries):
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload_s))
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content'].strip()
            if summary:
                break
        time.sleep(1)
    else:
        logger.warning("Summary generation failed after max retries.")
        return questions[:2], None  # Question succeeded but summary failed

    return questions[:2], summary


def save_to_note(book_name, pages, questions, summary):
    today = datetime.today().strftime('%Y-%m-%d')
    questions.append('what did you learn today?')
    note_data = {
        "date": today,
        "book": book_name,
        "pages": pages,
        "questions": questions,
        "answers": ["", "", ""],
        "summary": summary,
        "evaluation":""
    }

    try:
        with open(NOTE_FILE, 'r', encoding='utf-8') as f:
            all_notes = json.load(f)
    except FileNotFoundError:
        all_notes = []

    all_notes.append(note_data)

    with open(NOTE_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_notes, f, ensure_ascii=False, indent=2)


def llm_pre_read():

    with open(USER_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
    current_book = user_data.get("current_book", None)

    metadata_path = os.path.join(METADATA_DIR, f"{current_book}.json")
    

    with open(metadata_path, 'r', encoding='utf-8') as f:
        task_data=json.load(f)

    asked=task_data.get('has_asked_llm', True)
    if not asked:
        logger.info(f"LLM not yet called for today's plan. Starting LLM generation for book: {current_book}")
        pages=load_pages(task_data)
        text=load_text(current_book, pages)
        questions, summary=ask_llm(text)
        logger.info(f"Generated questions: {questions}")
        logger.info(f"Generated summary: {summary}")

        save_to_note(current_book, pages, questions, summary)
        task_data['has_asked_llm'] = True
        task_data['has_advanced'] = False
        logger.info(f"Updated task file: {metadata_path}")

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    llm_pre_read()
