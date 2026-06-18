import json
import os

from utils.sheets_client import get_worksheet, parse_unlocked, use_sheets

USERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "users.json"
)
USERS_COLUMNS = ["username", "password_hash", "tokens", "unlocked"]


def load_users() -> dict:
    if use_sheets():
        return _load_users_from_sheet()
    return _load_users_from_file()


def save_users(users: dict) -> None:
    if use_sheets():
        _save_users_to_sheet(users)
    else:
        _save_users_to_file(users)


def _load_users_from_file() -> dict:
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_users_to_file(users: dict) -> None:
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def _load_users_from_sheet() -> dict:
    ws = get_worksheet("users")
    records = ws.get_all_records()
    users: dict = {}
    for row in records:
        username = str(row.get("username", "")).strip()
        if not username:
            continue
        users[username] = {
            "password_hash": str(row.get("password_hash", "")),
            "tokens": int(row.get("tokens", 0) or 0),
            "unlocked": parse_unlocked(row.get("unlocked", "[]")),
        }
    return users


def _save_users_to_sheet(users: dict) -> None:
    ws = get_worksheet("users")
    rows = [USERS_COLUMNS]
    for username, data in users.items():
        rows.append(
            [
                username,
                data.get("password_hash", ""),
                data.get("tokens", 0),
                json.dumps(data.get("unlocked", []), ensure_ascii=False),
            ]
        )
    ws.clear()
    ws.update(
        range_name="A1",
        values=rows if len(rows) > 1 else [USERS_COLUMNS],
        value_input_option="RAW",
    )
