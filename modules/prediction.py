from time import perf_counter

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from . import database
from .utils import show_toast


TARGET = "Temperature"


def render_prediction_page(df: pd.DataFrame, user_id: int) -> None:
    start = perf_counter()
    st.subheader("ML Prediction")
    st.caption("Model: Linear Regression trained on yearly average temperature")

    data = df.copy()
    for col in ["Year", TARGET]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=["Year", TARGET])

    yearly = (
        data.groupby("Year", as_index=False)[[TARGET]]
        .mean()
        .sort_values("Year")
    )

    if len(yearly) < 2:
        st.warning("Not enough yearly data to train model. Need at least 2 years.")
        return

    X = yearly[["Year"]]
    y = yearly[TARGET]

    model = LinearRegression()
    model.fit(X, y)

    fit_preds = model.predict(X)

    st.markdown("### Training Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("MAE", f"{mean_absolute_error(y, fit_preds):.3f}")
    c2.metric("RMSE", f"{np.sqrt(mean_squared_error(y, fit_preds)):.3f}")
    c3.metric("R2", f"{r2_score(y, fit_preds):.3f}")
    st.dataframe(yearly, use_container_width=True)

    st.markdown("### Predict Future Temperature")
    next_default = int(yearly["Year"].max()) + 1
    with st.form("predict_form"):
        year = st.number_input("Future Year", min_value=1900, max_value=3000, value=next_default)
        submit = st.form_submit_button("Predict")

    if submit:
        pred = model.predict([[year]])[0]
        st.success(f"Predicted average temperature for {int(year)}: {pred:.2f}")
        show_toast(f"Prediction generated for {int(year)}.", "success")

    elapsed_ms = (perf_counter() - start) * 1000
    database.log_performance(user_id, "generate_prediction", elapsed_ms)
