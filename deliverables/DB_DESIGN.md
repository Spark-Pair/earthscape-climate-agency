# Database Design / Structure

**Database**: SQLite (`earthscape.db`)

**Tables**

1. `users`
- `id` INTEGER PK
- `username` TEXT UNIQUE
- `password_hash` TEXT
- `role` TEXT (admin, analyst)
- `fullname` TEXT
- `is_active` INTEGER
- `created_at` TEXT

2. `datasets`
- `id` INTEGER PK
- `dataset_name` TEXT
- `uploaded_by` INTEGER FK -> users.id
- `upload_time` TEXT
- `raw_csv_text` TEXT

3. `dataset_access`
- `id` INTEGER PK
- `dataset_id` INTEGER FK -> datasets.id
- `user_id` INTEGER FK -> users.id
- `granted_by` INTEGER FK -> users.id
- `granted_at` TEXT

4. `feedback`
- `id` INTEGER PK
- `user_id` INTEGER FK -> users.id
- `subject` TEXT
- `message` TEXT
- `created_at` TEXT
- `status` TEXT (open, closed)

5. `performance_logs`
- `id` INTEGER PK
- `user_id` INTEGER FK -> users.id
- `action_name` TEXT
- `timestamp` TEXT
- `execution_time_ms` REAL

6. `alerts`
- `id` INTEGER PK
- `dataset_id` INTEGER FK -> datasets.id
- `dataset_name` TEXT
- `user_id` INTEGER FK -> users.id
- `created_at` TEXT
- `summary_text` TEXT
- Threshold columns for anomaly and risk settings
- Counts for anomaly, heatwave, flood

**Relationships**
- One user can upload many datasets.
- One dataset can be assigned to many analysts (via `dataset_access`).
- One user can create many feedback entries and alerts.
- Performance logs track actions per user.

**Notes**
- Alerts are stored as snapshots for reporting and review.
- Raw CSV text is preserved for reproducibility and re-cleaning.
