import csv
import difflib
import os

from utils.sheets_client import get_worksheet, use_sheets
from utils.taxonomy import parse_year_parts

ANSWERS_FILE = "data/answers.csv"
ANSWERS_FIELDS = [
    "field",
    "subject",
    "teacher",
    "year",
    "score",
    "grade",
    "answer_text",
    "upload_time",
    "uploader_id",
]
MIN_ANSWER_CHARS = 300
MIN_ANSWER_HINT = "依誠信原則合理的字數"
SIMILAR_ANSWER_RATIO = 0.85
GRADE_OPTIONS = ["A", "B", "C", "F", "N/A"]


def normalize_meta(ans: dict) -> tuple[str, str, str, str]:
    field = (ans.get("field", "") or "").strip()
    subject = (ans.get("subject", "") or "").strip()
    teacher = (ans.get("teacher", "") or "").strip()
    year = (ans.get("year", "") or "").strip()
    if not field and subject and not teacher and not year:
        field = subject
        subject = ""
    return field, subject, teacher, year


def normalize_score(ans: dict) -> str:
    return str(ans.get("score", "") or "").strip()


def normalize_grade(ans: dict) -> str:
    return (ans.get("grade", "") or "").strip()


def to_new_row(ans: dict) -> dict:
    field, subject, teacher, year = normalize_meta(ans)
    return {
        "field": field,
        "subject": subject,
        "teacher": teacher,
        "year": year,
        "score": normalize_score(ans),
        "grade": normalize_grade(ans),
        "answer_text": ans.get("answer_text", ""),
        "upload_time": ans.get("upload_time", ""),
        "uploader_id": ans.get("uploader_id", ""),
    }


def load_answers() -> list[dict]:
    if use_sheets():
        return _load_answers_from_sheet()
    return _load_answers_from_file()


def _load_answers_from_file() -> list[dict]:
    if not os.path.exists(ANSWERS_FILE):
        return []
    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        return [to_new_row(ans) for ans in csv.DictReader(f)]


def _normalize_sheet_record(row: dict) -> dict:
    """相容試算表標題列拼字（answear_text / uploade_time）。"""
    out = dict(row)
    for old_key, new_key in (
        ("answear_text", "answer_text"),
        ("uploade_time", "upload_time"),
    ):
        if old_key in out and not str(out.get(new_key, "")).strip():
            out[new_key] = out[old_key]
    return out


def _load_answers_from_sheet() -> list[dict]:
    ws = get_worksheet("answers")
    records = ws.get_all_records()
    return [to_new_row(_normalize_sheet_record(ans)) for ans in records]


def save_answers(rows: list[dict]) -> None:
    if use_sheets():
        _save_answers_to_sheet(rows)
    else:
        _save_answers_to_file(rows)


def _save_answers_to_file(rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(ANSWERS_FILE), exist_ok=True)
    with open(ANSWERS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ANSWERS_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _save_answers_to_sheet(rows: list[dict]) -> None:
    ws = get_worksheet("answers")
    sheet_rows = [ANSWERS_FIELDS]
    for row in rows:
        normalized = to_new_row(row)
        sheet_rows.append([normalized[field] for field in ANSWERS_FIELDS])
    ws.clear()
    ws.update(
        range_name="A1",
        values=sheet_rows if len(sheet_rows) > 1 else [ANSWERS_FIELDS],
        value_input_option="RAW",
    )


def row_identity(ans: dict) -> tuple[str, str, str, str, str]:
    row = to_new_row(ans)
    return (
        row["field"],
        row["subject"],
        row["teacher"],
        row["year"],
        row["answer_text"].strip(),
    )


def combo_identity(ans: dict) -> tuple[str, str, str, str, str, str]:
    row = to_new_row(ans)
    return (
        row["field"],
        row["subject"],
        row["teacher"],
        row["year"],
        row["score"],
        row["grade"],
    )


def user_has_combo_upload(
    user_id: str,
    field: str,
    subject: str,
    teacher: str,
    year: str,
    score: str,
    grade: str,
    answers: list[dict],
) -> bool:
    target = (field, subject, teacher, year, score, grade)
    return any(
        ans.get("uploader_id") == user_id and combo_identity(ans) == target
        for ans in answers
    )


def answer_similarity(text_a: str, text_b: str) -> float:
    return difflib.SequenceMatcher(None, text_a, text_b).ratio()


def find_similar_user_upload(
    user_id: str,
    answer_text: str,
    answers: list[dict],
    threshold: float = SIMILAR_ANSWER_RATIO,
) -> dict | None:
    normalized = answer_text.strip()
    if not normalized:
        return None
    for ans in answers:
        if ans.get("uploader_id") != user_id:
            continue
        existing = ans.get("answer_text", "").strip()
        if not existing:
            continue
        if answer_similarity(normalized, existing) >= threshold:
            return ans
    return None


def make_unlock_id(ans: dict) -> str:
    row = to_new_row(ans)
    return (
        f"{row['field']}::{row['subject']}::{row['teacher']}::{row['year']}"
        f"::{row['score']}::{row['grade']}::{row['upload_time']}"
    )


def unlock_id_candidates(ans: dict) -> set[str]:
    upload_time = ans.get("upload_time", "")
    candidates = {make_unlock_id(ans)}
    subject_raw = ans.get("subject", "").strip()
    if subject_raw:
        candidates.add(f"{subject_raw}::{upload_time}")
    field, _, _, _ = normalize_meta(ans)
    if field:
        candidates.add(f"{field}::{upload_time}")
    row = to_new_row(ans)
    if row["field"] and row["year"]:
        candidates.add(
            f"{row['field']}::{row['subject']}::{row['teacher']}::{row['year']}"
            f"::{upload_time}"
        )
    return candidates


def is_unlocked(ans: dict, unlocked: list) -> bool:
    return bool(unlock_id_candidates(ans) & set(unlocked))


def format_label(ans: dict) -> str:
    field, subject, teacher, year = normalize_meta(ans)
    parts = [p for p in (field, subject, teacher) if p]
    if year:
        ay, sem, exam = parse_year_parts(year)
        if sem and exam:
            parts.append(f"{ay}學年{sem}{exam}")
        else:
            parts.append(year)
    score = normalize_score(ans)
    grade = normalize_grade(ans)
    if score:
        parts.append(f"{score}分")
    if grade:
        parts.append(f"等第{grade}")
    return "｜".join(parts) if parts else "未分類"


def find_answer_by_unlock_id(unlock_id: str, answers: list[dict]) -> dict | None:
    for ans in answers:
        if unlock_id in unlock_id_candidates(ans):
            return ans
    return None
