import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from utils.answers_store import find_answer_by_unlock_id, format_label, load_answers
from utils.session import restore_login
from utils.sheets_client import show_storage_status
from utils.users_store import load_users

st.title("個人頁面")

restore_login(st)

if not st.session_state.get("logged_in"):
    st.warning("請先登入")
    st.stop()

show_storage_status("profile")

users = load_users()
answers = load_answers()

username = st.session_state["username"]
balance = users[username]["tokens"]
user_id = st.session_state["user_id"]
upload_count = sum(1 for ans in answers if ans.get("uploader_id") == user_id)
unlocked_count = len(users[username].get("unlocked", []))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("我的代幣", balance)
with col2:
    st.metric("上傳筆數", upload_count)
with col3:
    st.metric("已解鎖", unlocked_count)

st.subheader("已解鎖清單")
unlocked_ids = users[username].get("unlocked", [])
if not unlocked_ids:
    st.caption("尚無解鎖紀錄")
else:
    for unlock_id in unlocked_ids:
        ans = find_answer_by_unlock_id(unlock_id, answers)
        if ans:
            st.write(f"- {format_label(ans)}")
        else:
            st.write(f"- {unlock_id}（找不到對應作答）")