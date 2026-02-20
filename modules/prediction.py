from time import perf_counter

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from . import database
from .utils import show_toast


FEATURE_COLUMNS = ["Year", "Month", "Rainfall", "CO2", "Humidity", "WindSpeed"]
TARGET = "Temperature"
MODEL_MIN_ROWS = 2


def _dataset_signature(df: pd.DataFrame) -> tuple:
    if df is None or df.empty:
        return (0, 0, None, None)
    numeric_year = pd.to_numeric(df.get("Year"), errors="coerce")
    return (
        int(len(df)),
        int(len(df.columns)),
        int(numeric_year.min()) if numeric_year.notna().any() else None,
        int(numeric_year.max()) if numeric_year.notna().any() else None,
    )


def _prepare_prediction_frame(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    for col in FEATURE_COLUMNS + [TARGET]:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    work = work.dropna(subset=FEATURE_COLUMNS + [TARGET])
    work = work[(work["Month"] >= 1) & (work["Month"] <= 12)]
    return work


def train_and_store_model(df: pd.DataFrame, user_id: int | None = None, force: bool = False) -> bool:
    if df is None or df.empty:
        st.session_state.model = None
        st.session_state.model_metrics = None
        st.session_state.model_feature_defaults = None
        st.session_state.model_dataset_signature = None
        return False

    signature = _dataset_signature(df)
    if not force and st.session_state.get("model") is not None:
        if st.session_state.get("model_dataset_signature") == signature:
            return True

    start = perf_counter()
    work = _prepare_prediction_frame(df)

    if len(work) < MODEL_MIN_ROWS:
        st.session_state.model = None
        st.session_state.model_metrics = None
        st.session_state.model_feature_defaults = None
        st.session_state.model_dataset_signature = signature
        return False

    X = work[FEATURE_COLUMNS]
    y = work[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred) if len(y_test) > 1 else None

    st.session_state.model = model
    st.session_state.model_metrics = {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": None if r2 is None else float(r2),
        "rows": int(len(work)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }
    st.session_state.model_feature_defaults = {
        "Year": int(work["Year"].median()),
        "Month": int(work["Month"].median()),
        "Rainfall": float(work["Rainfall"].median()),
        "CO2": float(work["CO2"].median()),
        "Humidity": float(work["Humidity"].median()),
        "WindSpeed": float(work["WindSpeed"].median()),
    }
    st.session_state.model_dataset_signature = signature

    elapsed_ms = (perf_counter() - start) * 1000
    database.log_performance(user_id, "train_prediction_model", elapsed_ms)
    return True


def render_prediction_page(df: pd.DataFrame, user_id: int) -> None:
    st.subheader("ML Prediction")
    st.caption(
        "Model: Linear Regression trained once per loaded dataset using Year, Month, Rainfall, CO2, Humidity, WindSpeed."
    )

    ready = train_and_store_model(df, user_id=user_id, force=False)
    if not ready or st.session_state.get("model") is None:
        st.warning("Not enough clean data to train model. Need at least 2 valid rows.")
        return

    metrics = st.session_state.get("model_metrics") or {}
    defaults = st.session_state.get("model_feature_defaults") or {}

    st.markdown("### Model Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("MAE", f"{metrics.get('mae', 0.0):.3f}")
    c2.metric("RMSE", f"{metrics.get('rmse', 0.0):.3f}")
    r2_val = metrics.get("r2")
    c3.metric("R2", "N/A" if r2_val is None else f"{r2_val:.3f}")

    st.caption(
        f"Training rows: {metrics.get('train_rows', 0)} | Test rows: {metrics.get('test_rows', 0)}"
    )

    st.markdown("### Predict Temperature")
    with st.form("predict_form_multivariate"):
        f1, f2, f3 = st.columns(3)
        with f1:
            year = st.number_input(
                "Year",
                min_value=1900,
                max_value=3000,
                value=int(defaults.get("Year", 2026)),
                step=1,
            )
            month = st.number_input(
                "Month",
                min_value=1,
                max_value=12,
                value=int(defaults.get("Month", 1)),
                step=1,
            )
        with f2:
            rainfall = st.number_input(
                "Rainfall",
                value=float(defaults.get("Rainfall", 0.0)),
                step=0.1,
            )
            co2 = st.number_input(
                "CO2",
                value=float(defaults.get("CO2", 400.0)),
                step=0.1,
            )
        with f3:
            humidity = st.number_input(
                "Humidity",
                value=float(defaults.get("Humidity", 55.0)),
                step=0.1,
            )
            wind_speed = st.number_input(
                "WindSpeed",
                value=float(defaults.get("WindSpeed", 10.0)),
                step=0.1,
            )

        submit = st.form_submit_button("Predict Temperature", width="stretch")

    if submit:
        start = perf_counter()
        input_df = pd.DataFrame(
            [
                {
                    "Year": float(year),
                    "Month": float(month),
                    "Rainfall": float(rainfall),
                    "CO2": float(co2),
                    "Humidity": float(humidity),
                    "WindSpeed": float(wind_speed),
                }
            ]
        )
        pred_temp = float(st.session_state.model.predict(input_df[FEATURE_COLUMNS])[0])

        st.success(f"Predicted Temperature: {pred_temp:.2f}")
        show_toast("Prediction generated successfully.", "success")

        elapsed_ms = (perf_counter() - start) * 1000
        database.log_performance(user_id, "generate_prediction", elapsed_ms)
