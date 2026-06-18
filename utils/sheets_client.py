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


def sheets_storage_label() -> str:
    return "Google 試算表" if use_sheets() else "本機檔案"


def test_sheets_connection() -> tuple[bool, str]:
    if not use_sheets():
        return False, "Secrets 裡找不到 gcp_service_account（區塊名稱必須完全一致）"
    try:
        ws = get_worksheet("answers")
        return True, f"連線成功，作答分頁：{ws.title}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


DEPLOY_TAG = "sheets-v1"


def show_storage_status(widget_key: str = "default") -> None:
    """在頁面主區塊顯示儲存模式（st.navigation 會蓋掉 app.py 側欄自訂內容）。"""
    import streamlit as st

    st.caption(f"程式版本：{DEPLOY_TAG}")

    if use_sheets():
        st.info(f"資料儲存：{sheets_storage_label()}")
    else:
        st.warning(
            "資料儲存：本機檔案（試算表不會更新）。"
            "請在 Streamlit Cloud Secrets 設定 [gcp_service_account]，並 Reboot app。"
        )
    with st.expander("試算表連線測試"):
        if st.button("測試連線", key=f"test_sheets_{widget_key}"):
            ok, msg = test_sheets_connection()
            if ok:
                st.success(msg)
            else:
                st.error(msg)


def get_streamlit_session_id() -> str:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        if ctx and ctx.session_id:
            return str(ctx.session_id)
    except Exception:
        pass
    return ""


def _get_client():
    import gspread
    import streamlit as st
    from google.oauth2.service_account import Credentials

    creds_info = _creds_info_from_secrets()
    private_key = creds_info.get("private_key", "")
    if isinstance(private_key, str) and "\\n" in private_key:
        creds_info["private_key"] = private_key.replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_worksheet(sheet_key: str):
    import gspread

    if sheet_key not in _TAB_ALIASES:
        raise ValueError(f"未知的 sheet_key: {sheet_key}")

    client = _get_client()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    for title in _TAB_ALIASES[sheet_key]:
        try:
            return spreadsheet.worksheet(title)
        except gspread.WorksheetNotFound:
            continue

    index = {"answers": 0, "users": 1}[sheet_key]
    return spreadsheet.get_worksheet(index)


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
