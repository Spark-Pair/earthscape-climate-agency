from io import StringIO
from time import perf_counter

import pandas as pd
import streamlit as st

from . import database
from .utils import REQUIRED_COLUMNS, card, show_toast


NUMERIC_COLUMNS = ["Temperature", "Rainfall", "CO2"]


def clean_and_validate_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame | None, list[str]]:
    errors: list[str] = []

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
        return None, errors

    cleaned = df[REQUIRED_COLUMNS].copy()
    cleaned = cleaned.drop_duplicates()

    cleaned["Year"] = pd.to_numeric(cleaned["Year"], errors="coerce")
    cleaned["Month"] = pd.to_numeric(cleaned["Month"], errors="coerce")

    for col in NUMERIC_COLUMNS:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    cleaned = cleaned.dropna(subset=["Year", "Month"])
    cleaned = cleaned[(cleaned["Month"] >= 1) & (cleaned["Month"] <= 12)]

    for col in NUMERIC_COLUMNS:
        if cleaned[col].isna().all():
            errors.append(f"Column '{col}' has no valid numeric values.")
            return None, errors
        cleaned[col] = cleaned[col].fillna(cleaned[col].mean())

    cleaned["Year"] = cleaned["Year"].astype(int)
    cleaned["Month"] = cleaned["Month"].astype(int)

    if cleaned.empty:
        errors.append("Dataset is empty after cleaning.")

    return cleaned, errors


def render_admin_upload_and_save(user: dict) -> None:
    card(
        "Upload Dataset",
        "📤",
        "<p class='section-muted'>Upload a CSV, validate fields, clean values, then save or assign.</p>",
    )

    uploader_key = f"upload_csv_{st.session_state.upload_uploader_key}"
    uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"], key=uploader_key)

    if not uploaded_file:
        return

    start = perf_counter()
    raw_text = uploaded_file.getvalue().decode("utf-8", errors="replace")

    try:
        raw_df = pd.read_csv(StringIO(raw_text))
    except Exception as ex:
        st.error(f"Failed to parse CSV: {ex}")
        return

    upload_token = f"{uploaded_file.name}:{len(raw_text)}"
    if st.session_state.get("upload_form_token") != upload_token:
        st.session_state["upload_form_token"] = upload_token
        st.session_state["dataset_name_input"] = uploaded_file.name
        st.session_state["assign_multiselect"] = []

    cleaned_df, errors = clean_and_validate_dataset(raw_df)
    if errors:
        for err in errors:
            st.error(err)
        return

    elapsed_ms = (perf_counter() - start) * 1000
    database.log_performance(user["id"], "upload_dataset", elapsed_ms)

    st.success("Dataset uploaded and cleaned successfully.")
    show_toast("Dataset uploaded and cleaned successfully.", "success")
    st.dataframe(cleaned_df.head(50), use_container_width=True)

    st.session_state.active_df = cleaned_df
    st.session_state.active_dataset_id = None
    st.session_state.active_dataset_name = uploaded_file.name
    st.session_state.active_dataset_source = "upload"
    st.session_state.last_upload_csv_text = cleaned_df.to_csv(index=False)
    st.session_state.last_upload_dataset_name = uploaded_file.name

    dataset_name = st.text_input(
        "Dataset name", value=uploaded_file.name, key="dataset_name_input"
    )
    analysts = database.list_analysts()
    analyst_options = {f"{row['username']} (id:{row['id']})": row["id"] for row in analysts}

    selected_labels = st.multiselect(
        "Assign to analysts (for Save & Assign)",
        options=list(analyst_options.keys()),
        key="assign_multiselect",
    )

    if st.button("Save Dataset", use_container_width=True):
        if not dataset_name.strip():
            st.error("Dataset name is required.")
        elif not st.session_state.last_upload_csv_text:
            st.error("No uploaded dataset found in session.")
        else:
            dataset_id = database.insert_dataset(
                dataset_name.strip(), user["id"], st.session_state.last_upload_csv_text
            )
            selected_ids = [analyst_options[label] for label in selected_labels]
            if selected_ids:
                database.grant_dataset_access_bulk(dataset_id, selected_ids, user["id"])

            st.session_state.active_dataset_id = dataset_id
            st.session_state.active_dataset_name = dataset_name.strip()
            st.session_state.active_dataset_source = "database"

            if selected_ids:
                st.success(
                    f"Dataset saved and assigned to {len(selected_ids)} analyst(s). ID: {dataset_id}"
                )
                show_toast(
                    f"Dataset saved and assigned to {len(selected_ids)} analyst(s).",
                    "success",
                )
            else:
                st.success(f"Dataset saved (ID: {dataset_id}).")
                show_toast("Dataset saved successfully.", "success")

            # Hide upload detail controls after save because dataset is already open.
            st.session_state.upload_uploader_key += 1
            st.session_state.upload_form_token = None
            st.session_state.pop("dataset_name_input", None)
            st.session_state.pop("assign_multiselect", None)
            st.rerun()


def render_dataset_access_overview(admin_user: dict) -> None:
    card(
        "Dataset Access Overview",
        "🔐",
        "<p class='section-muted'>See analysts assigned to each dataset.</p>",
    )
    datasets = database.list_datasets_for_admin()
    if not datasets:
        st.info("No datasets uploaded yet.")
        return

    for ds in datasets:
        with st.expander(
            f"[{ds['id']}] {ds['dataset_name']} | Uploaded by {ds['uploaded_by_username']} | Assigned: {ds['assigned_users']}"
        ):
            access_rows = database.list_dataset_access(ds["id"])
            if not access_rows:
                st.caption("No analyst assigned.")
            else:
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "analyst": row["analyst_username"],
                                "granted_by": row["granted_by_username"],
                                "granted_at": row["granted_at"],
                            }
                            for row in access_rows
                        ]
                    ),
                    use_container_width=True,
                )

            st.markdown("#### Assign Later")
            analysts = database.list_analysts()
            assigned_user_ids = {row["user_id"] for row in access_rows}
            assignable_analysts = [a for a in analysts if a["id"] not in assigned_user_ids]
            if not assignable_analysts:
                st.caption("All analysts are already assigned to this dataset.")
            else:
                analyst_options = {
                    f"{a['username']} (id:{a['id']})": a["id"] for a in assignable_analysts
                }
                assign_labels = st.multiselect(
                    "Select analysts",
                    options=list(analyst_options.keys()),
                    key=f"assign_later_{ds['id']}",
                )
                if st.button("Assign Selected Analysts", key=f"assign_later_btn_{ds['id']}"):
                    selected_ids = [analyst_options[label] for label in assign_labels]
                    if not selected_ids:
                        st.warning("Select at least one analyst.")
                        show_toast("Select at least one analyst.", "warning")
                    else:
                        database.grant_dataset_access_bulk(ds["id"], selected_ids, admin_user["id"])
                        st.success(f"Assigned to {len(selected_ids)} analyst(s).")
                        show_toast(f"Assigned to {len(selected_ids)} analyst(s).", "success")
                        st.rerun()

            st.markdown("#### Take Back Access")
            if access_rows:
                revoke_options = {
                    f"{row['analyst_username']} (id:{row['user_id']})": row["user_id"]
                    for row in access_rows
                }
                revoke_label = st.selectbox(
                    "Select analyst to remove",
                    options=list(revoke_options.keys()),
                    key=f"revoke_select_{ds['id']}",
                )
                if st.button("Remove Access", key=f"revoke_btn_{ds['id']}"):
                    database.revoke_dataset_access(ds["id"], revoke_options[revoke_label])
                    st.success("Access removed.")
                    show_toast("Access removed from analyst.", "success")
                    st.rerun()
            else:
                st.caption("No analyst access to remove.")


def render_assigned_dataset_selector(user: dict) -> None:
    st.subheader("Saved / Assigned Datasets")

    datasets = database.list_datasets_for_user(user["id"], user["role"])
    if not datasets:
        st.info("No datasets assigned yet.")
        return

    admin_counts = {}
    if user["role"] == "admin":
        admin_counts = {d["id"]: d["assigned_users"] for d in database.list_datasets_for_admin()}

    for row in datasets:
        assigned_count = admin_counts.get(row["id"], "-")
        st.markdown(
            f"""
            <div class="app-card">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
                    <div>
                        <h4 class="dataset-title">📁 {row['dataset_name']}</h4>
                        <p class="dataset-meta">
                            ID: <b>{row['id']}</b> &nbsp;|&nbsp; Uploaded by: <b>{row['uploaded_by_username']}</b> &nbsp;|&nbsp; Assigned: <b>{assigned_count}</b>
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if user["role"] == "admin":
            c1, c2 = st.columns(2)
            with c1:
                open_clicked = st.button(
                    "Open Dataset",
                    key=f"open_dataset_{row['id']}",
                    use_container_width=True,
                )
            with c2:
                delete_clicked = st.button(
                    "Delete Dataset",
                    key=f"delete_dataset_{row['id']}",
                    use_container_width=True,
                )
        else:
            open_clicked = st.button(
                "Open Dataset",
                key=f"open_dataset_{row['id']}",
                use_container_width=True,
            )
            delete_clicked = False

        if open_clicked:
            start = perf_counter()
            full_row = database.get_dataset_by_id(row["id"])
            if not full_row:
                st.error("Dataset not found.")
                return

            df = pd.read_csv(StringIO(full_row["raw_csv_text"]))
            elapsed_ms = (perf_counter() - start) * 1000
            database.log_performance(user["id"], "load_dataset_from_db", elapsed_ms)

            st.session_state.active_df = df
            st.session_state.active_dataset_id = full_row["id"]
            st.session_state.active_dataset_name = full_row["dataset_name"]
            st.session_state.active_dataset_source = "database"
            st.success(f"Loaded dataset: {full_row['dataset_name']}")
            show_toast(f"Loaded dataset: {full_row['dataset_name']}", "success")
            st.rerun()

        if delete_clicked:
            database.delete_dataset(row["id"])
            if st.session_state.active_dataset_id == row["id"]:
                st.session_state.active_df = None
                st.session_state.active_dataset_id = None
                st.session_state.active_dataset_name = None
                st.session_state.active_dataset_source = None
            st.success("Dataset deleted.")
            show_toast("Dataset deleted.", "success")
            st.rerun()
