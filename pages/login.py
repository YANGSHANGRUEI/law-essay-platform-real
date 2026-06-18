import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import hashlib
import streamlit as st

from utils.session import restore_login, save_login, clear_login
from utils.sheets_client import show_storage_status
from utils.users_store import load_users, save_users


st.title("登入／註冊")
show_storage_status("login")

restore_login(st)

users = load_users()

if st.session_state.get("logged_in") and st.session_state.get("username"):
    username_logged = st.session_state["username"]
    balance = users[username_logged]["tokens"]
    st.info(f"你已登入，代號：{st.session_state['user_id']}")
    st.metric("我的代幣", balance)
    if st.button("登出"):
        clear_login(st)
        st.rerun()

else:
    st.write(f"目前已註冊 {len(users)} 個帳號")
    tab_login, tab_register = st.tabs(["登入", "註冊"])

    with tab_login:
        login_username = st.text_input("帳號", key="login_username")
        login_password = st.text_input("密碼", type="password", key="login_password")

        if st.button("登入", key="login_submit"):
            hashed = hashlib.sha256(login_password.encode("utf-8")).hexdigest()
            if login_username not in users:
                st.error("帳號或密碼錯誤")
            elif hashed != users[login_username]["password_hash"]:
                st.error("帳號或密碼錯誤")
            else:
                st.success("登入成功！")
                user_id = hashlib.sha256(login_username.encode("utf-8")).hexdigest()[:12]
                save_login(st, login_username, user_id)
                st.rerun()

    with tab_register:
        reg_username = st.text_input("請輸入帳號", key="register_username")
        reg_password = st.text_input("請輸入密碼", type="password", key="register_password")

        if st.button("註冊", key="register_submit"):
            if reg_username == "":
                st.warning("請輸入帳號")
            elif reg_password == "":
                st.warning("請輸入密碼")
            elif reg_username in users:
                st.warning("此帳號已存在")
            else:
                hashed = hashlib.sha256(reg_password.encode("utf-8")).hexdigest()
                users[reg_username] = {
                    "password_hash": hashed,
                    "tokens": 3,
                    "unlocked": [],
                }
                save_users(users)
                user_id = hashlib.sha256(reg_username.encode("utf-8")).hexdigest()[:12]
                save_login(st, reg_username, user_id)
                st.success(
                    f"帳號「{reg_username}」註冊成功！先給你三代幣體驗壹下，"
                    "可以拿去解別人的作答看看"
                )
                st.rerun()
