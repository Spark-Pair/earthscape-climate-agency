import html
import streamlit as st

from .team_data import TEAM_MEMBERS


def _chip(label: str, value: str) -> str:
    if label.lower() == "email":
        href = f"mailto:{value}"
    else:
        href = value

    safe_label = html.escape(label)
    return (
        f"<a class='link-chip' href='{href}' target='_blank'>"
        f"{safe_label} <span class='chip-arrow'>↗</span></a>"
    )


def render_team_page() -> None:
    st.subheader("Built By")
    st.caption("Core team behind `EarthScape Climate Agency`")

    cols = st.columns(2)
    for idx, member in enumerate(TEAM_MEMBERS):
        name = html.escape(member.get("name", "Unknown"))
        details = []
        for key, value in member.items():
            if key == "name" or not value:
                continue
            details.append(_chip(key.capitalize(), str(value)))

        details_html = "".join(details) if details else "<span class='section-muted'>No details added.</span>"
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div class='app-card team-member-card'>
                    <h4 style='margin-bottom:10px;'>{name}</h4>
                    <div class='chips-wrap'>
                        {details_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
