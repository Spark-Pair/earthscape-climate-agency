from time import perf_counter

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from . import database


def _build_working_frame(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["Year"] = pd.to_numeric(work["Year"], errors="coerce")
    work["Month"] = pd.to_numeric(work["Month"], errors="coerce")
    work["Temperature"] = pd.to_numeric(work["Temperature"], errors="coerce")
    work["Rainfall"] = pd.to_numeric(work["Rainfall"], errors="coerce")
    work["CO2"] = pd.to_numeric(work["CO2"], errors="coerce")
    work = work.dropna(subset=["Year", "Month", "Temperature", "Rainfall", "CO2"])
    work["Year"] = work["Year"].astype(int)
    work["Month"] = work["Month"].astype(int)
    work["date_key"] = work["Year"].astype(str) + "-" + work["Month"].astype(str).str.zfill(2)
    return work


def detect_anomalies(
    df: pd.DataFrame,
    temp_thresh: float = 2.0,
    rain_thresh: float = 2.0,
    co2_thresh: float = 2.0,
) -> pd.DataFrame:
    work = _build_working_frame(df)
    if work.empty:
        return work

    for col in ["Temperature", "Rainfall", "CO2"]:
        std = work[col].std(ddof=0)
        if std == 0:
            work[f"{col}_z"] = 0.0
        else:
            work[f"{col}_z"] = (work[col] - work[col].mean()) / std

    mask = (
        work["Temperature_z"].abs() > temp_thresh
    ) | (work["Rainfall_z"].abs() > rain_thresh) | (work["CO2_z"].abs() > co2_thresh)
    return work[mask].copy()


def render_dashboard(df: pd.DataFrame, dataset_name: str, user_id: int) -> None:
    start = perf_counter()
    st.subheader("Climate Dashboard")
    st.caption(f"Active dataset: {dataset_name}")

    work = _build_working_frame(df)
    if work.empty:
        st.warning("No valid rows available for dashboard metrics.")
        return

    year_min = int(work["Year"].min())
    year_max = int(work["Year"].max())
    year_range = st.slider(
        "Year range",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
    )

    filtered = work[(work["Year"] >= year_range[0]) & (work["Year"] <= year_range[1])].copy()
    if filtered.empty:
        st.warning("No data available in selected year range.")
        return

    tab_preview, tab_kpi, tab_yearly, tab_graphs, tab_anomaly = st.tabs(
        ["Preview", "KPIs", "Yearly Aggregation", "Graphs", "Anomalies & Alerts"]
    )

    with tab_preview:
        st.dataframe(filtered, use_container_width=True, height=420)
        st.caption(f"Rows: {len(filtered)}")

    with tab_kpi:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg Temperature", f"{filtered['Temperature'].mean():.2f}")
        c2.metric("Max Temperature", f"{filtered['Temperature'].max():.2f}")
        c3.metric("Avg Rainfall", f"{filtered['Rainfall'].mean():.2f}")
        c4.metric("Avg CO2", f"{filtered['CO2'].mean():.2f}")

    with tab_yearly:
        yearly = (
            filtered.groupby("Year", as_index=False)[["Temperature", "Rainfall", "CO2"]]
            .mean()
            .sort_values("Year")
        )
        st.dataframe(yearly, use_container_width=True)

    with tab_graphs:
        trend = (
            filtered.groupby(["Year", "Month"], as_index=False)
            [["Temperature", "Rainfall", "CO2"]]
            .mean()
            .sort_values(["Year", "Month"])
        )
        trend["date_key"] = trend["Year"].astype(str) + "-" + trend["Month"].astype(str).str.zfill(2)

        fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
        sns.lineplot(data=trend, x="date_key", y="Temperature", ax=axes[0], color="#e76f51")
        axes[0].set_title("Temperature Trend")
        sns.lineplot(data=trend, x="date_key", y="Rainfall", ax=axes[1], color="#2a9d8f")
        axes[1].set_title("Rainfall Trend")
        sns.lineplot(data=trend, x="date_key", y="CO2", ax=axes[2], color="#264653")
        axes[2].set_title("CO2 Trend")

        for ax in axes:
            ax.tick_params(axis="x", rotation=45)
            ax.grid(alpha=0.2)

        plt.tight_layout()
        st.pyplot(fig)

    with tab_anomaly:
        c1, c2 = st.columns(2)
        with c1:
            temp_thresh = st.slider(
                "Temperature anomaly threshold (z-score)", 1.0, 4.0, 2.0, 0.1
            )
        with c2:
            rain_thresh = st.slider(
                "Rainfall anomaly threshold (z-score)", 1.0, 4.0, 2.0, 0.1
            )

        # Keep CO2 threshold fixed unless explicitly required separately.
        co2_thresh = 2.0
        anomalies = detect_anomalies(
            filtered,
            temp_thresh=temp_thresh,
            rain_thresh=rain_thresh,
            co2_thresh=co2_thresh,
        )
        if anomalies.empty:
            st.success("No anomalies detected at current threshold.")
        else:
            st.warning(f"Detected {len(anomalies)} anomaly rows.")
            st.dataframe(
                anomalies[
                    [
                        "Year",
                        "Month",
                        "Temperature",
                        "Rainfall",
                        "CO2",
                        "Temperature_z",
                        "Rainfall_z",
                        "CO2_z",
                    ]
                ],
                use_container_width=True,
            )

            temp_alerts = anomalies[anomalies["Temperature_z"].abs() > temp_thresh]
            rain_alerts = anomalies[anomalies["Rainfall_z"].abs() > rain_thresh]
            co2_alerts = anomalies[anomalies["CO2_z"].abs() > co2_thresh]
            st.info(
                f"Alerts: Temperature={len(temp_alerts)}, Rainfall={len(rain_alerts)}, CO2={len(co2_alerts)}"
            )

        st.divider()
        st.markdown("### Disaster Risk Alerts")
        r1, r2 = st.columns(2)
        with r1:
            heatwave_temp_threshold = st.number_input(
                "Heatwave temperature threshold",
                min_value=-50.0,
                max_value=100.0,
                value=36.0,
                step=0.5,
            )
        with r2:
            flood_rain_threshold = st.number_input(
                "Flood rainfall threshold",
                min_value=0.0,
                max_value=1000.0,
                value=30.0,
                step=0.5,
            )

        heatwave_records = filtered[filtered["Temperature"] > heatwave_temp_threshold].copy()
        flood_records = filtered[filtered["Rainfall"] > flood_rain_threshold].copy()

        if heatwave_records.empty and flood_records.empty:
            st.success("No disaster risk alerts at the current thresholds.")
        else:
            if not heatwave_records.empty:
                st.warning(
                    f"Heatwave risk detected: {len(heatwave_records)} record(s) with Temperature > {heatwave_temp_threshold:.1f}"
                )
            if not flood_records.empty:
                st.warning(
                    f"Flood risk detected: {len(flood_records)} record(s) with Rainfall > {flood_rain_threshold:.1f}"
                )

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("#### Heatwave Affected Records")
            if heatwave_records.empty:
                st.info("No heatwave-affected records.")
            else:
                st.dataframe(
                    heatwave_records[["Year", "Month", "Temperature", "Rainfall", "CO2"]],
                    use_container_width=True,
                )
        with c4:
            st.markdown("#### Flood Affected Records")
            if flood_records.empty:
                st.info("No flood-affected records.")
            else:
                st.dataframe(
                    flood_records[["Year", "Month", "Temperature", "Rainfall", "CO2"]],
                    use_container_width=True,
                )

    elapsed_ms = (perf_counter() - start) * 1000
    database.log_performance(user_id, "generate_dashboard", elapsed_ms)
