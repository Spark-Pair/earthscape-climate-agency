# Developer Guide

**Project Structure**
- `main.py`: App routing and layout.
- `modules/`: Feature modules.
- `datasets/`: Sample CSV datasets.
- `deliverables/`: Report and documentation package.

**Key Modules**
- `modules/auth.py`: Authentication and session logic.
- `modules/database.py`: SQLite schema and queries.
- `modules/dataset_manager.py`: Upload, clean, and assign datasets.
- `modules/dashboard.py`: KPIs, trends, anomalies, alerts snapshots.
- `modules/prediction.py`: ML training and inference.
- `modules/reports.py`: Report generation and exports.
- `modules/feedback.py`: Support messages.
- `modules/performance.py`: Performance logs and charts.

**Run Locally**
1. Create virtual environment.
2. Install dependencies from `requirements.txt`.
3. Start app with `streamlit run main.py`.

**Database**
- SQLite file: `earthscape.db`.
- Tables created on first run.

**Adding New Analytics**
- Add functions in `modules/dashboard.py`.
- Add data transforms in `modules/dataset_manager.py`.
- Log performance via `database.log_performance`.

**Adding New Alerts**
- Update anomaly logic in `modules/dashboard.py`.
- Store snapshots with `database.insert_alert_snapshot`.
- Display history in `modules/reports.py`.

**Big Data Extension Plan**
- Replace `raw_csv_text` storage with HDFS paths.
- Implement MapReduce or Spark jobs for aggregation.
- Add streaming ingestion service and message queues.
