def restore_login(st):
    if st.session_state.get("logged_in"):
        return


def save_login(st, username, user_id):
    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = user_id


def clear_login(st):
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
