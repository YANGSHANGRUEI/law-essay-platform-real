import json
import os
from datetime import datetime

QUESTIONS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "questions.json"
)


def combo_key(field: str, subject: str, teacher: str, year: str) -> str:
    return f"{field}::{subject}::{teacher}::{year}"


def load_questions() -> dict:
    if not os.path.exists(QUESTIONS_FILE):
        return {}
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_question(field: str, subject: str, teacher: str, year: str) -> dict | None:
    questions = load_questions()
    return questions.get(combo_key(field, subject, teacher, year))


def save_question(
    field: str,
    subject: str,
    teacher: str,
    year: str,
    question_text: str,
    uploader_id: str,
) -> None:
    questions = load_questions()
    questions[combo_key(field, subject, teacher, year)] = {
        "question_text": question_text,
        "upload_time": datetime.now().isoformat(),
        "uploader_id": uploader_id,
    }
    os.makedirs(os.path.dirname(QUESTIONS_FILE), exist_ok=True)
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
