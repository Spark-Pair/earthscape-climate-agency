import pandas as pd
import streamlit as st

from . import database


def render_performance_page(user: dict) -> None:
    st.subheader("Performance Monitoring")

    rows = database.list_performance_logs(limit=2000)
    if not rows:
        st.info("No performance logs yet.")
        return

    df = pd.DataFrame(
        [
            {
                "id": r["id"],
                "username": r["username"] if r["username"] else "anonymous",
                "action_name": r["action_name"],
                "timestamp": r["timestamp"],
                "execution_time_ms": round(r["execution_time_ms"], 3),
            }
            for r in rows
        ]
    )

    if user["role"] != "admin":
        df = df[df["username"] == user["username"]]

    if df.empty:
        st.info("No performance logs available for this user.")
        return

    st.markdown("### Summary")
    avg_df = (
        df.groupby("action_name", as_index=False)["execution_time_ms"]
        .mean()
        .rename(columns={"execution_time_ms": "avg_execution_time_ms"})
        .sort_values("avg_execution_time_ms", ascending=False)
    )
    avg_df["avg_execution_time_ms"] = avg_df["avg_execution_time_ms"].round(3)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Logged Actions", len(df))
    with c2:
        st.metric("Overall Avg Time (ms)", f"{df['execution_time_ms'].mean():.3f}")

    st.markdown("### Average Execution Time Per Action")
    st.dataframe(avg_df, width="stretch")

    st.markdown("### Charts")
    chart_df = avg_df.set_index("action_name")[["avg_execution_time_ms"]]
    st.bar_chart(chart_df, width="stretch")

    trend_df = df.copy()
    trend_df["timestamp"] = pd.to_datetime(trend_df["timestamp"], errors="coerce")
    trend_df = trend_df.dropna(subset=["timestamp"]).sort_values("timestamp")
    if not trend_df.empty:
        st.line_chart(
            trend_df.set_index("timestamp")[["execution_time_ms"]],
            width="stretch",
        )

    st.markdown("### Performance Logs")
    st.dataframe(df, width="stretch")
