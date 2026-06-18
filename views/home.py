import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from utils.session import clear_login
from utils.sheets_client import show_storage_status

st.title("法律申論題交流平台")
show_storage_status("home")
st.markdown("恭喜註冊成功，這是一個匿名的法律申論題交流平台，使用者上傳自己的作答換取代幣，並用代幣去解鎖別人的作答，以達到互相交流學習的效果。本站為完全匿名，解鎖他人作答時不會看到上傳的帳號名，資料庫只存使用者帳號和雜湊過的密碼，而且輸入限制電腦字體（可拍照給AI轉電腦文字）。總而言之，從作答追蹤到本人極為困難，就算資料庫被駭也是。先給你三代幣體驗一下，可以拿去解別人的作答看看，目前有兩份，刑總跟債總。")

st.success(f"已登入（代號：{st.session_state.get('user_id', '—')}）")
st.markdown("請用左側 **功能** 選單進入上傳、瀏覽或個人頁面。")

if st.button("登出"):
    clear_login(st)
    st.rerun()
