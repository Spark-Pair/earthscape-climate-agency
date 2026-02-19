import hashlib
from time import perf_counter

import streamlit as st

from . import database
from .utils import show_toast

try:
    import bcrypt
except Exception:
    bcrypt = None


def hash_password(password: str) -> str:
    if bcrypt:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return "bcrypt$" + hashed.decode("utf-8")
    return "sha256$" + hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    if stored_hash.startswith("bcrypt$") and bcrypt:
        raw = stored_hash.split("$", 1)[1].encode("utf-8")
        return bcrypt.checkpw(password.encode("utf-8"), raw)

    if stored_hash.startswith("sha256$"):
        expected = stored_hash.split("$", 1)[1]
        actual = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return expected == actual

    # Legacy fallback
    return stored_hash == hashlib.sha256(password.encode("utf-8")).hexdigest()


def ensure_default_admin() -> None:
    if database.user_count(role="admin") == 0:
        database.create_user(
            "admin",
            hash_password("admin123"),
            "admin",
            fullname="System Administrator",
            is_active=1,
        )


def login(username: str, password: str) -> bool:
    start = perf_counter()
    user = database.get_user_by_username(username)
    ok = bool(
        user and int(user["is_active"]) == 1 and verify_password(password, user["password_hash"])
    )

    if ok:
        st.session_state.logged_in = True
        st.session_state.user = {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "fullname": user["fullname"],
        }
        # Backward compatibility for legacy single-file app state keys.
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]

    elapsed_ms = (perf_counter() - start) * 1000
    database.log_performance(user["id"] if ok else None, "login", elapsed_ms)
    return ok


def logout() -> None:
    for key in [
        "logged_in",
        "user",
        "active_df",
        "active_dataset_id",
        "active_dataset_name",
        "active_dataset_source",
        "last_upload_csv_text",
        "last_upload_dataset_name",
    ]:
        st.session_state[key] = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.logged_in = False


def render_login_form() -> None:
    top_spacer, content, side_spacer = st.columns([1.2, 2, 1.2])
    with content:
        st.markdown(
            """
            <div class='login-card'>
                <div class='login-logo'>
                    🌍
                </div>
                <div>
                    <h2 class='login-title'>Welcome Back</h2>
                    <p class='login-sub'>Sign in to continue to EarthScape Studio</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                user = database.get_user_by_username(username.strip())
                if user and int(user["is_active"]) == 0:
                    st.error("Your account is deactivated. Contact admin.")
                elif login(username.strip(), password):
                    st.success("Login successful")
                    show_toast("Login successful", "success")
                    st.rerun()
                else:
                    st.error("Invalid credentials")


def render_create_analyst_form() -> None:
    st.subheader("Add User")
    with st.form("create_analyst_form", clear_on_submit=True):
        fullname = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        st.caption("New users are created as analysts.")
        submitted = st.form_submit_button("Create User")

        if submitted:
            username = username.strip()
            if not username or not password:
                st.error("Username and password are required.")
                return
            if database.get_user_by_username(username):
                st.error("Username already exists.")
                return
            database.create_user(
                username,
                hash_password(password),
                "analyst",
                fullname=fullname.strip(),
                is_active=1,
            )
            st.success(f"User '{username}' created.")
            show_toast(f"User '{username}' created.", "success")


def login_page() -> None:
    """
    Legacy compatibility wrapper expected by app.py.
    """
    database.init_db()
    ensure_default_admin()
    render_login_form()


def logout_button() -> None:
    """
    Legacy compatibility wrapper expected by app.py.
    """
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()
