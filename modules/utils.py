from io import StringIO
import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = ["Year", "Month", "Temperature", "Rainfall", "CO2"]


def render_global_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --primary: #121212;
                --secondary: #1f1f1f;
                --accent: #000000;
                --bg: #0f0f10;
                --card: #1a1a1c;
                --card-soft: #242426;
                --border: #3a3a3f;
                --text: #f3f3f4;
                --muted: #b8b8bc;
            }

            .stAppHeader {
                border-bottom: 1px solid var(--border);
                background: transparent !important;
            }

            .stApp {
                background: var(--bg);
                color: var(--text);
            }

            [data-testid="stSidebar"] {
                background: var(--bg);
                border-right: 1px solid #2a2a2e;
                padding-top: 0.5rem;
            }
            [data-testid="stSidebar"] * { color: var(--text); }

            .profile-card, .app-header {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 12px;
            }
            .role-badge {
                display: inline-block;
                background: #090909;
                color: #f1f1f1;
                border: 1px solid #3a3a3f;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 600;
                padding: 2px 10px;
                margin-top: 6px;
            }

            .app-card {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 16px 18px;
                box-shadow: 0 8px 18px rgba(2, 24, 31, 0.18);
                margin-bottom: 14px;
            }
            .app-card h4 {
                margin: 0 0 8px 0;
                color: #ffffff;
                font-weight: 700;
            }
            .app-card p, .app-card div {
                color: var(--muted);
            }

            .stButton > button {
                border-radius: 12px !important;
                border: 1px solid var(--border) !important;
                background: var(--card-soft) !important;
                color: #ffffff !important;
                font-weight: 600 !important;
                height: 2.65rem;
            }
            [data-testid="stSidebar"] .stButton > button {
                background: var(--card-soft) !important;
                color: #ffffff !important;
                border: 1px solid var(--border) !important;
                font-weight: 600 !important;
            }

            [data-testid="stSidebar"] .stButton > button:hover {
                background: #303034 !important;
                border-color: #58585f !important;
            }
            .stButton > button:hover {
                background: #303034 !important;
                border-color: #58585f !important;
                color: #ffffff !important;
            }

            .stTextInput > div > div,
            .stTextArea > div > div,
            .stSelectbox > div > div,
            .stNumberInput > div > div,
            .stFileUploader > div,
            .stMultiSelect > div > div {
                border-radius: 12px !important;
                border-color: var(--border) !important;
                background: #1e1e21 !important;
                color: #ffffff !important;
            }
            .stFileUploader section {
                border-radius: 16px !important;
            }
            div[data-testid="stVerticalBlock"]:has(div[data-testid="stForm"]){
                border-radius: 16px !important;
            }
            div[data-testid="stForm"] {
                border-radius: 8px !important;
            }
            .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] * {
                color: #ffffff !important;
            }
            label, .stMarkdown, .stCaption, .stText, p, h1, h2, h3, h4 {
                color: var(--text) !important;
            }
            [data-testid="stFileUploaderDropzone"] {
                background: #1e1e21 !important;
                border: 1px solid var(--border) !important;
            }

            .status-active, .status-inactive {
                display: inline-block;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 700;
                padding: 3px 10px;
                border: 1px solid;
            }
            .status-active {
                color: #ffffff;
                border-color: #3a3a3a;
                background: #000000;
            }
            .status-inactive {
                color: #ffe3e6;
                border-color: #f0a2ab;
                background: #8f2f3a;
            }

            .table-wrap {
                border: 1px solid var(--border);
                border-radius: 14px;
                overflow: hidden;
                background: #1a1a1c;
            }
            .table-wrap table {
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            }
            .table-wrap th {
                text-align: left;
                background: #222225;
                color: #f5f5f6;
                padding: 10px;
                border-bottom: 1px solid var(--border);
            }
            .table-wrap td {
                padding: 10px;
                border-bottom: 1px solid #2b2b30;
                color: #ebebed;
            }
            .table-wrap tr:last-child td { border-bottom: none; }

            div[data-baseweb="tab-list"] {
                gap: 8px;
                background: #1a1a1d;
                padding: 8px 10px;
                border-radius: 12px;
                justify-content: flex-start;
                overflow-x: auto;
            }
            div[data-baseweb="tab-list"] button {
                border-radius: 10px !important;
                height: 2.4rem;
                border: none !important;
                color: #ceced1 !important;
                background: #242426 !important;
                font-weight: 600 !important;
                flex: 0 0 auto !important;
                padding: 0 16px !important;
                margin-right: 2px;
            }
            div[data-baseweb="tab-list"] button[aria-selected="true"] {
                background: #35353a !important;
                color: #ffffff !important;
            }

            div[data-testid="stMetric"] {
                background: #1e1e21;
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 10px;
            }
            div[data-testid="stMetric"] * {
                color: #ffffff !important;
            }

            .logout-card {
                max-width: 560px;
                margin: 40px auto;
                text-align: center;
            }

            .mt-4 { margin-top: 16px !important; }
            .section-muted { margin: 0; color: var(--muted) !important; }
            .dataset-title { margin: 0; color: var(--text) !important; font-weight: 700; }
            .dataset-meta { margin: 6px 0 0 0; color: var(--muted) !important; }
            .logout-title { margin: 8px 0; color: var(--text) !important; }
            .logout-text { margin: 0; color: var(--muted) !important; }
            .login-card {
                display: flex;
                align-items: center;
                gap: 20px;
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 22px;
                box-shadow: 0 8px 18px rgba(0, 0, 0, 0.25);
                margin: 26px 0;
            }
            .login-logo {
                height: 5.4rem;
                aspect-ratio: 1 / 1;
                border-radius: 14px;
                background: var(--card-soft);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 26px;
            }
            .login-title { margin: 0; color: var(--text) !important; }
            .login-sub { margin: 0; color: var(--muted) !important; }
            .team-member-card { margin-bottom: 10px; }
            .chips-wrap {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            .link-chip {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 10px;
                border-radius: 999px;
                border: 1px solid var(--border);
                background: var(--card-soft);
                color: var(--text) !important;
                text-decoration: none !important;
                font-size: 12px;
            }
            .link-chip:hover {
                background: #303034;
                border-color: #58585f;
            }
            .chip-arrow {
                font-weight: 700;
                opacity: .9;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, icon: str, content_html: str) -> None:
    st.markdown(
        f"""
        <div class="app-card">
            <h4>{icon} {title}</h4>
            <div>{content_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_banner() -> None:
    st.markdown(
        """
        <div style='
            background: #18181b;
            border: 1px solid #3a3a3f;
            padding: 18px 20px;
            border-radius: 16px;
            color: white;
            margin-bottom: 14px;
            box-shadow: 0 12px 22px rgba(0, 0, 0, 0.35);
        '>
            <h2 style='margin: 0;'>EarthScape Climate Agency</h2>
            <p style='margin: 6px 0 0 0; opacity: 0.95;'>Climate analytics, monitoring & prediction</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    defaults = {
        "logged_in": False,
        "user": None,
        "active_df": None,
        "active_dataset_id": None,
        "active_dataset_name": None,
        "active_dataset_source": None,
        "last_upload_csv_text": None,
        "last_upload_dataset_name": None,
        "current_page": "Datasets",
        "logout_confirm": False,
        "show_add_user": False,
        "upload_uploader_key": 0,
        "upload_form_token": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def csv_text_to_df(csv_text: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(csv_text))


def df_to_csv_text(df: pd.DataFrame) -> str:
    return df.to_csv(index=False)


def rows_to_dataframe(rows: list, columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame([dict(r) for r in rows])


def show_toast(message: str, level: str = "info") -> None:
    icon_map = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }
    st.toast(message, icon=icon_map.get(level, "ℹ️"))
