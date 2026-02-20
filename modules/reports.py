from time import perf_counter

import pandas as pd
import streamlit as st

from . import database
from .dashboard import detect_anomalies


def render_reports_page(df: pd.DataFrame, dataset_name: str, user_id: int) -> None:
    st.subheader("Reports")
    st.caption(f"Dataset: {dataset_name}")

    report_df = df.copy()
    for col in ["Year", "Month", "Temperature", "Rainfall", "CO2", "Humidity", "WindSpeed"]:
        report_df[col] = pd.to_numeric(report_df[col], errors="coerce")
    report_df = report_df.dropna(
        subset=["Year", "Month", "Temperature", "Rainfall", "CO2", "Humidity", "WindSpeed"]
    )
    report_df = report_df[(report_df["Month"] >= 1) & (report_df["Month"] <= 12)]

    if report_df.empty:
        st.warning("No clean rows available for report generation.")
        return

    aggregate_report = (
        report_df.groupby(["Year", "Month"], as_index=False)[
            ["Temperature", "Rainfall", "CO2", "Humidity", "WindSpeed"]
        ]
        .mean()
        .sort_values(["Year", "Month"])
    )
    anomalies = detect_anomalies(report_df, temp_thresh=2.0, rain_thresh=2.0, co2_thresh=2.0)

    summary_lines = [
        f"Dataset: {dataset_name}",
        f"Total rows: {len(report_df)}",
        f"Year range: {int(report_df['Year'].min())} - {int(report_df['Year'].max())}",
        f"Avg Temperature: {report_df['Temperature'].mean():.2f}",
        f"Max Temperature: {report_df['Temperature'].max():.2f}",
        f"Avg Rainfall: {report_df['Rainfall'].mean():.2f}",
        f"Avg CO2: {report_df['CO2'].mean():.2f}",
        f"Avg Humidity: {report_df['Humidity'].mean():.2f}",
        f"Avg WindSpeed: {report_df['WindSpeed'].mean():.2f}",
        f"Anomalies detected: {len(anomalies)}",
    ]
    summary_text = "\n".join(summary_lines)

    st.markdown("### Summary Report")
    st.code(summary_text)
    st.markdown("### Year-Month Aggregated Report")
    st.dataframe(aggregate_report, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Prepare CSV Export", use_container_width=True):
            start = perf_counter()
            csv_bytes = aggregate_report.to_csv(index=False).encode("utf-8")
            elapsed_ms = (perf_counter() - start) * 1000
            database.log_performance(user_id, "export_report", elapsed_ms)
            st.download_button(
                label="Download CSV Report",
                data=csv_bytes,
                file_name=f"{dataset_name}_report.csv",
                mime="text/csv",
            )

    with c2:
        if st.button("Prepare Summary Export", use_container_width=True):
            start = perf_counter()
            summary_bytes = summary_text.encode("utf-8")
            elapsed_ms = (perf_counter() - start) * 1000
            database.log_performance(user_id, "export_report", elapsed_ms)
            st.download_button(
                label="Download Summary Report",
                data=summary_bytes,
                file_name=f"{dataset_name}_summary.txt",
                mime="text/plain",
            )
