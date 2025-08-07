
from datetime import datetime
import json
import requests
import time
import os
from dotenv import load_dotenv
from logging_config import logger

API_URL = 'https://openrouter.ai/api/v1/chat/completions'
load_dotenv()
API_KEY = os.getenv("API_KEY")

def evaluate_answers(note_entry: dict, max_retries: int = 5, delay_seconds: int = 1) -> str:

    questions = note_entry.get("questions", [])
    answers = note_entry.get("answers", [])
    summary = note_entry.get("summary", "")

    # Combine questions and answers
    qa_pairs = "\n".join(
        f"Q{i+1}: {q}\nA{i+1}: {a}"
        for i, (q, a) in enumerate(zip(questions, answers))
    )

    prompt = f"""You are a helpful educational assistant. I will give you a set of reflection questions, the user's answers, and a summary of the reading material for today. Please help me with the following:

1. Evaluate the quality and relevance of the user's answers. Are they thoughtful and connected to the topic?
2. Based on the summary and the answers, assess whether the user has engaged meaningfully with the content.
3. Finally, give a recommendation: should the user proceed to the next section of the reading plan, or should they revisit today's material for deeper understanding?

--- 
Questions and Answers:
{qa_pairs}

Summary of today's content:  
{summary}

---

Please respond with:
- Evaluation of each answer
- Overall engagement assessment
- Recommendation: "Advance" or "Review Again"
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "z-ai/glm-4.5-air:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    attempt = 0
    logger.info(
    f"Starting LLM evaluation for book: {note_entry.get('book', 'unknown')} "
    f"on date: {note_entry.get('date', datetime.today().strftime('%Y-%m-%d'))}"
)
    while attempt < max_retries:
        try:
            response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.warning(f"[Attempt {attempt+1}] API Error {response.status_code}: {response.text}")
        except Exception as e:
            logger.exception(f"[Attempt {attempt+1}] Exception occurred during LLM evaluation: {e}")

        attempt += 1
        time.sleep(delay_seconds)

    raise Exception(f"Failed after {max_retries} retries.")


if __name__=='__main__':
    with open("notes.json", "r", encoding="utf-8") as f:
        notes = json.load(f)

    try:
        result = evaluate_answers(notes[-1])
        print(result)
    except Exception as e:
        print("Evaluation failed:", e)
