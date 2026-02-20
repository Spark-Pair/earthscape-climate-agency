import pandas as pd
import streamlit as st

from modules import auth
from modules import dashboard
from modules import database
from modules import dataset_manager
from modules import feedback
from modules import performance
from modules import prediction
from modules import reports
from modules import team_page
from modules.utils import card, init_session_state, render_banner, render_global_styles, show_toast


st.set_page_config(page_title="EarthScape Climate Agency", layout="wide")


def _active_dataset_ready() -> bool:
    return st.session_state.active_df is not None


def _render_dataset_required_notice() -> None:
    st.info("Load or upload a dataset first from Datasets page.")


def render_active_dataset_banner() -> None:
    name = st.session_state.get("active_dataset_name")
    source = st.session_state.get("active_dataset_source")
    if name:
        st.markdown(
            f"""
            <div class='app-card' style='padding:10px 14px;'>
                <p class='section-muted'>
                    <b>Opened Dataset:</b> {name}
                    &nbsp;|&nbsp;
                    <b>Source:</b> {source or "unknown"}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class='app-card' style='padding:10px 14px;'>
                <p class='section-muted'><b>Opened Dataset:</b> None</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar_navigation(user: dict) -> str:
    active_name = st.session_state.get("active_dataset_name")
    active_source = st.session_state.get("active_dataset_source")

    # ---------- APP TITLE ----------
    st.sidebar.markdown(
        """
        <div class="app-header">
            <div class="app-title">🌍 ES Climate Agency</div>
            <div class="app-subtitle">Climate analytics, monitoring & prediction</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("<div style='font-size:12px;opacity:.85;margin:8px 0;'>MENU</div>", unsafe_allow_html=True)

    if user["role"] == "admin":
        if st.sidebar.button("Users", key="nav_users", width="stretch"):
            st.session_state.current_page = "Users"

    if st.sidebar.button("Datasets", key="nav_datasets", width="stretch"):
        st.session_state.current_page = "Datasets"

    if st.sidebar.button("Team", key="nav_team", width="stretch"):
        st.session_state.current_page = "Team"

    if st.sidebar.button("Logout", key="nav_logout", width="stretch"):
        st.session_state.current_page = "Logout"

    st.sidebar.markdown(
        f"""
        <div class="dataset-open-card">
            <div class="dataset-open-title">OPENED DATASET</div>
            <div class="dataset-open-name">{active_name or "None selected"}</div>
            <div class="dataset-open-meta">Source: {active_source or "-"}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        f"""
        <div class="profile-card absolute-bottom">
            <div class="profile-top">
                <div class="profile-avatar">
                    {user['username'][0].upper()}
                </div>
                <div class="profile-info">
                    <div class="profile-name">
                        {user.get('fullname') or user['username']}
                    </div>
                    <div class="profile-username">
                        @{user['username']}
                    </div>
                </div>
            </div>
            <div class="profile-bottom">
                <span class="role-badge">{user['role'].upper()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------- CUSTOM CSS ----------
    st.sidebar.markdown("""
    <style>
        .app-header {
            margin-bottom: 20px;
        }
        .app-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .app-subtitle {
            font-size: 12px;
            opacity: 0.7;
        }
        .menu-label {
            font-size: 12px;
            opacity: 0.6;
            margin: 15px 0 5px 0;
            letter-spacing: 1px;
        }

        .dataset-open-card {
            margin: 10px 0 14px 0;
            padding: 10px 12px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: linear-gradient(145deg, var(--card), rgba(255,255,255,0.02));
        }
        .dataset-open-title {
            font-size: 11px;
            letter-spacing: .7px;
            opacity: .75;
            margin-bottom: 4px;
        }
        .dataset-open-name {
            font-size: 13px;
            font-weight: 600;
            line-height: 1.3;
            word-break: break-word;
        }
        .dataset-open-meta {
            margin-top: 5px;
            font-size: 11px;
            opacity: .7;
        }
                        
        /* Profile Card Container */
        .profile-card {
            position: fixed;
            bottom: 20px;
            width: 250px;

            background: linear-gradient(145deg, var(--card), rgba(255,255,255,0.03));
            border: 1px solid var(--border);
            border-radius: 16px;

            padding: 16px;
            backdrop-filter: blur(10px);

            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
            transition: all 0.25s ease;
        }

        .profile-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.35);
        }

        /* Top layout */
        .profile-top {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        /* Avatar circle */
        .profile-avatar {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: linear-gradient(145deg, #26262a, #1d1d20);
            border: 1px solid #3a3a3f;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 18px;
            color: white;
        }

        /* Name + username */
        .profile-name {
            font-weight: 600;
            font-size: 14px;
        }

        .profile-username {
            font-size: 12px;
            opacity: 0.6;
        }

        /* Bottom section */
        .profile-bottom {
            margin-top: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Role badge */
        .role-badge {
            font-size: 10px;
            padding: 4px 10px;
            border-radius: 20px;
            background: #090909;
            color: #f1f1f1;
            border: 1px solid #3a3a3f;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
                        
        .logout-btn button {
            background-color: #ff4b4b !important;
            color: white !important;
            border-radius: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    return st.session_state.current_page


def render_users_page(user: dict) -> None:
    if user["role"] != "admin":
        st.error("Access denied.")
        return

    card("Users", "👥", "<p class='section-muted'>Manage user accounts and access states.</p>")

    if st.session_state.show_add_user:
        with st.container(border=True):
            auth.render_create_analyst_form()
        c1, c2, c3 = st.columns([1, 1, 2], vertical_alignment="center")
        with c1:
            if st.button("← Back", width="stretch"):
                st.session_state.show_add_user = False
                st.rerun()
        return

    top_left, top_mid, top_right = st.columns([2, 1, 1], vertical_alignment="bottom")
    with top_left:
        search = st.text_input("Search users", placeholder="Search by username, fullname, or role")
    with top_mid:
        if st.button("Add User", width="stretch"):
            st.session_state.show_add_user = True
            st.rerun()
    with top_right:
        st.write("")

    rows = database.list_users()
    if not rows:
        st.info("No users found.")
        return

    filtered_rows = []
    q = (search or "").strip().lower()
    for r in rows:
        if not q:
            filtered_rows.append(r)
            continue
        hay = f"{r['username']} {r['fullname']} {r['role']}".lower()
        if q in hay:
            filtered_rows.append(r)

    table_html = [
        "<div class='table-wrap'><table><thead><tr>",
        "<th>Username</th><th>Password</th><th>Full Name</th><th>Role</th><th>Status</th><th>Created</th>",
        "</tr></thead><tbody>",
    ]
    for r in filtered_rows:
        badge = (
            "<span class='status-active'>ACTIVE</span>"
            if int(r["is_active"]) == 1
            else "<span class='status-inactive'>INACTIVE</span>"
        )
        table_html.append(
            f"<tr><td>{r['username']}</td><td>******</td><td>{r['fullname'] or '-'}</td><td>{r['role']}</td><td>{badge}</td><td>{r['created_at']}</td></tr>"
        )
    table_html.append("</tbody></table></div>")

    st.markdown("".join(table_html), unsafe_allow_html=True)

    st.markdown("<div class='app-card mt-4'><h4>🔄 Account Status</h4></div>", unsafe_allow_html=True)
    manageable_rows = [r for r in rows if r["id"] != user["id"]]
    if not manageable_rows:
        st.info("No other users available for activation/deactivation.")
        return

    user_options = {f"{r['username']} ({r['role']})": r for r in manageable_rows}
    selected = st.selectbox("Select user", options=list(user_options.keys()))
    selected_user = user_options[selected]

    if int(selected_user["is_active"]) == 1:
        if st.button("Deactivate", width="stretch"):
            if selected_user["id"] == user["id"]:
                st.error("You cannot deactivate your own account.")
                return
            database.set_user_active(selected_user["id"], 0)
            st.success(f"{selected_user['username']} is inactive.")
            show_toast(f"{selected_user['username']} deactivated.", "success")
            st.rerun()
    else:
        if st.button("Activate", width="stretch"):
            database.set_user_active(selected_user["id"], 1)
            st.success(f"{selected_user['username']} is active.")
            show_toast(f"{selected_user['username']} activated.", "success")
            st.rerun()


def render_datasets_page(user: dict) -> None:
    card("Datasets", "🗂️", "<p class='section-muted'>Upload, open, analyze, predict and export from one workspace.</p>")

    if user["role"] == "admin":
        render_tabs = st.tabs(["Upload & Assign", "Saved Datasets", "Analytics Workspace", "Access Matrix"])

        with render_tabs[0]:
            dataset_manager.render_admin_upload_and_save(user)

        with render_tabs[1]:
            dataset_manager.render_assigned_dataset_selector(user)

        with render_tabs[2]:
            tab_dash, tab_pred, tab_rep, tab_feed, tab_perf = st.tabs(
                ["Dashboard", "Prediction", "Reports", "Feedback", "Performance"]
            )

            with tab_dash:
                if _active_dataset_ready():
                    dashboard.render_dashboard(
                        st.session_state.active_df,
                        st.session_state.active_dataset_name or "Active Dataset",
                        user["id"],
                    )
                else:
                    _render_dataset_required_notice()

            with tab_pred:
                if _active_dataset_ready():
                    prediction.render_prediction_page(st.session_state.active_df, user["id"])
                else:
                    _render_dataset_required_notice()

            with tab_rep:
                if _active_dataset_ready():
                    reports.render_reports_page(
                        st.session_state.active_df,
                        st.session_state.active_dataset_name or "active_dataset",
                        user["id"],
                    )
                else:
                    _render_dataset_required_notice()

            with tab_feed:
                feedback.render_feedback_page(user)

            with tab_perf:
                performance.render_performance_page(user)

        with render_tabs[3]:
            dataset_manager.render_dataset_access_overview(user)

    else:
        render_tabs = st.tabs(["Saved Datasets", "Analytics Workspace"])

        with render_tabs[0]:
            dataset_manager.render_assigned_dataset_selector(user)

        with render_tabs[1]:
            tab_dash, tab_pred, tab_rep, tab_feed, tab_perf = st.tabs(
                ["Dashboard", "Prediction", "Reports", "Feedback", "Performance"]
            )

            with tab_dash:
                if _active_dataset_ready():
                    dashboard.render_dashboard(
                        st.session_state.active_df,
                        st.session_state.active_dataset_name or "Active Dataset",
                        user["id"],
                    )
                else:
                    _render_dataset_required_notice()

            with tab_pred:
                if _active_dataset_ready():
                    prediction.render_prediction_page(st.session_state.active_df, user["id"])
                else:
                    _render_dataset_required_notice()

            with tab_rep:
                if _active_dataset_ready():
                    reports.render_reports_page(
                        st.session_state.active_df,
                        st.session_state.active_dataset_name or "active_dataset",
                        user["id"],
                    )
                else:
                    _render_dataset_required_notice()

            with tab_feed:
                feedback.render_feedback_page(user)

            with tab_perf:
                performance.render_performance_page(user)


def render_logout_page() -> None:
    st.markdown(
        """
        <div class='app-card logout-card'>
            <div style='font-size:44px;'>⚠️</div>
            <h3 class='logout-title'>Confirm Logout</h3>
            <p class='logout-text'>Are you sure you want to end your current session?</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    space1, c1, c2, space2, = st.columns([1, 1, 1, 1], vertical_alignment="center")
    with c1:
        if st.button("Logout Now", width="stretch"):
            auth.logout()
            st.success("Logged out.")
            show_toast("Logged out successfully.", "success")
            st.rerun()
    with c2:
        if st.button("Cancel", width="stretch"):
            st.session_state.current_page = "Datasets"
            st.rerun()


def app() -> None:
    init_session_state()
    database.init_db()
    auth.ensure_default_admin()
    render_global_styles()

    # LOGIN PAGE ONLY
    if not st.session_state.logged_in:
        auth.render_login_form()
        return

    # DASHBOARD UI ONLY (after login)
    # render_banner()
    # render_active_dataset_banner()

    user = st.session_state.user
    page = render_sidebar_navigation(user)

    if page == "Users":
        render_users_page(user)
    elif page == "Team":
        team_page.render_team_page()
    elif page == "Logout":
        render_logout_page()
    else:
        render_datasets_page(user)


if __name__ == "__main__":
    app()
