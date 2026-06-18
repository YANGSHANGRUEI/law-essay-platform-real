"""Google Sheets 後端（部署用）。需在 Streamlit Secrets 設定 gcp_service_account。"""

import json

# answers 與 users 同一試算表、不同分頁
SPREADSHEET_ID = "1lasUgPoaDM5O909Cu87EOCcazm3DU7QShuGwjXuS8gM"

_TAB_ALIASES = {
    "answers": ["answers", "工作表1", "Sheet1"],
    "users": ["users", "工作表2", "Sheet2"],
}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def use_sheets() -> bool:
    try:
        import streamlit as st

        return "gcp_service_account" in st.secrets
    except Exception:
        return False


def _creds_info_from_secrets() -> dict:
    import streamlit as st

    raw = st.secrets["gcp_service_account"]
    if isinstance(raw, str):
        return json.loads(raw)
    return dict(raw)


def get_streamlit_session_id() -> str:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        if ctx and ctx.session_id:
            return str(ctx.session_id)
    except Exception:
        pass
    return ""


def _normalize_private_key(key: str) -> str:
    """修正 Secrets 貼上時 private_key 換行跑掉的常見情況。"""
    key = (key or "").strip()
    if not key:
        return key
    if "\\n" in key:
        key = key.replace("\\n", "\n")
    if "BEGIN PRIVATE KEY" not in key:
        return key
    # 三引號貼上但只剩一行
    if key.count("\n") < 2:
        body = key
        body = body.replace("-----BEGIN PRIVATE KEY-----", "")
        body = body.replace("-----END PRIVATE KEY-----", "")
        body = "".join(body.split())
        chunks = [body[i : i + 64] for i in range(0, len(body), 64)]
        key = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(chunks) + "\n-----END PRIVATE KEY-----\n"
    else:
        key = key.replace("-----BEGIN PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----\n")
        key = key.replace("-----END PRIVATE KEY-----", "\n-----END PRIVATE KEY-----\n")
        key = "\n".join(line.strip() for line in key.splitlines() if line.strip())
        if not key.endswith("\n"):
            key += "\n"
    return key


def _get_client():
    import gspread
    from google.oauth2.service_account import Credentials

    creds_info = _creds_info_from_secrets()
    creds_info["private_key"] = _normalize_private_key(creds_info.get("private_key", ""))
    try:
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    except ValueError as e:
        raise ValueError(
            "gcp_service_account 的 private_key 格式錯誤。"
            "請在 Streamlit Secrets 用三引號 \"\"\" 多行貼上金鑰（見 secrets.toml.example）。"
        ) from e
    return gspread.authorize(creds)


def _service_account_email() -> str:
    try:
        return str(_creds_info_from_secrets().get("client_email", "")).strip()
    except Exception:
        return ""


def _open_spreadsheet(client):
    import gspread

    try:
        return client.open_by_key(SPREADSHEET_ID)
    except gspread.exceptions.APIError as e:
        status = getattr(e.response, "status_code", None)
        email = _service_account_email()
        if status in (403, 404):
            raise PermissionError(
                f"無法開啟 Google 試算表（HTTP {status}）。"
                f"請把試算表共用給 Service Account「{email}」，權限選編輯者。"
            ) from e
        raise


def get_worksheet(sheet_key: str):
    import gspread

    if sheet_key not in _TAB_ALIASES:
        raise ValueError(f"未知的 sheet_key: {sheet_key}")

    client = _get_client()
    spreadsheet = _open_spreadsheet(client)
    for title in _TAB_ALIASES[sheet_key]:
        try:
            return spreadsheet.worksheet(title)
        except gspread.WorksheetNotFound:
            continue

    index = {"answers": 0, "users": 1}[sheet_key]
    return spreadsheet.get_worksheet(index)


def _sheet_api_retry(func, *, stale_fallback=None):
    """429 時短暫重試；仍失敗且有过期快取則用快取。"""
    import time

    import gspread

    last_error = None
    for wait_sec in (0, 2, 4):
        if wait_sec:
            time.sleep(wait_sec)
        try:
            return func()
        except gspread.exceptions.APIError as e:
            last_error = e
            status = getattr(e.response, "status_code", None)
            if status == 429 and stale_fallback is not None:
                return stale_fallback
            if status != 429:
                raise
    raise last_error


def parse_unlocked(value) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    text = str(value).strip()
    if not text:
        return []
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []
