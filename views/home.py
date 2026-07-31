import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from utils.session import clear_login

st.title("法律申論題交流平台")
st.markdown("歡迎使用法律申論題交流平台，這裡的運作模式是上傳自己的作答換取代幣以解鎖他人作答，希望可以促進法律系同學的交流學習。")
st.success("已登入")
st.markdown("請用左側 **功能** 選單進入上傳、瀏覽或個人頁面。")

if st.button("登出"):
    clear_login(st)
    st.rerun()
