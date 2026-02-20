import pandas as pd
import streamlit as st

from . import database
from .utils import show_toast


SUBJECT_OPTIONS = [
    "General Question",
    "Data Issue",
    "Dashboard Bug",
    "Prediction Issue",
    "Feature Request",
]


def render_feedback_page(user: dict) -> None:
    st.subheader("Feedback / Support")

    with st.form("feedback_form", clear_on_submit=True):
        subject = st.selectbox("Subject", SUBJECT_OPTIONS)
        message = st.text_area("Message", height=150)
        submit = st.form_submit_button("Submit Feedback")

        if submit:
            if not message.strip():
                st.error("Message is required.")
            else:
                database.insert_feedback(user["id"], subject, message.strip())
                st.success("Feedback submitted.")
                show_toast("Feedback submitted.", "success")

    st.markdown("### Feedback History")

    if user["role"] == "admin":
        rows = database.list_all_feedback()
        if not rows:
            st.info("No feedback entries yet.")
            return

        for row in rows:
            with st.expander(
                f"#{row['id']} | {row['subject']} | {row['username']} | {row['status']} | {row['created_at']}"
            ):
                st.write(row["message"])
                new_status = st.selectbox(
                    "Update status",
                    ["open", "closed"],
                    index=0 if row["status"] == "open" else 1,
                    key=f"status_{row['id']}",
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Save Status", key=f"save_{row['id']}"):
                        database.update_feedback_status(row["id"], new_status)
                        st.success("Status updated.")
                        show_toast("Feedback status updated.", "success")
                        st.rerun()
                with c2:
                    if st.button("Delete Feedback", key=f"delete_feedback_{row['id']}"):
                        database.delete_feedback(row["id"])
                        st.success("Feedback deleted.")
                        show_toast("Feedback deleted.", "success")
                        st.rerun()
    else:
        rows = database.list_feedback_for_user(user["id"])
        if not rows:
            st.info("You have not submitted feedback yet.")
            return

        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "id": r["id"],
                        "subject": r["subject"],
                        "message": r["message"],
                        "created_at": r["created_at"],
                        "status": r["status"],
                    }
                    for r in rows
                ]
            ),
            width="stretch",
        )
