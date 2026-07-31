import base64
import hashlib
import hmac
import json
import time
from typing import Optional

from utils.users_store import load_users

_AUTH_QUERY_KEY = "auth"
_TOKEN_TTL_SEC = 60 * 60 * 24 * 7  # 7 days


def _signing_secret(st) -> str:
    # Prefer explicit app secret; fall back to other configured secrets in dev.
    return (
        st.secrets.get("APP_SESSION_SECRET")
        or st.secrets.get("OPENAI_API_KEY")
        or "dev-insecure-session-secret"
    )


def _make_token(st, username: str, user_id: str) -> str:
    payload = {
        "u": username,
        "id": user_id,
        "exp": int(time.time()) + _TOKEN_TTL_SEC,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("ascii")
    sig = hmac.new(
        _signing_secret(st).encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return f"{payload_b64}.{sig}"


def _read_query_auth(st) -> str:
    raw = st.query_params.get(_AUTH_QUERY_KEY)
    if isinstance(raw, list):
        return str(raw[0]) if raw else ""
    return str(raw or "")


def _set_query_auth(st, token: str) -> None:
    st.query_params[_AUTH_QUERY_KEY] = token


def _clear_query_auth(st) -> None:
    try:
        st.query_params.pop(_AUTH_QUERY_KEY)
    except Exception:
        # Some Streamlit versions expose query params as a limited mapping.
        st.query_params[_AUTH_QUERY_KEY] = ""


def _parse_token(st, token: str) -> Optional[dict]:
    try:
        payload_b64, sig = token.split(".", 1)
        expected = hmac.new(
            _signing_secret(st).encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("ascii")))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        username = str(payload.get("u", "")).strip()
        user_id = str(payload.get("id", "")).strip()
        if not username or not user_id:
            return None
        return {"username": username, "user_id": user_id}
    except Exception:
        return None


def restore_login(st):
    if st.session_state.get("logged_in"):
        return

    token = _read_query_auth(st)
    if not token:
        return

    parsed = _parse_token(st, token)
    if not parsed:
        _clear_query_auth(st)
        return

    users = load_users()
    username = parsed["username"]
    if username not in users:
        _clear_query_auth(st)
        return

    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = parsed["user_id"]


def save_login(st, username, user_id):
    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = user_id
    _set_query_auth(st, _make_token(st, username, user_id))


def clear_login(st):
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    _clear_query_auth(st)
