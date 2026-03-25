# EarthScape Climate Agency - eProject Report

**Project Title**: Big Data - EarthScape Climate Agency

**Team**
- Muhammad Hassan Raza (Student1482631)
- Syed Furqan Ahmed (Student1478217)
- Shayan Kamran (Student1486131)
- Mubashir Ahmed (Student1491431)
- Muhammad Zauraiz (Student1478974)
- Syed Ayan Ali (Student1480301)
- Muhammad Muzammil Mughal (Student1476131)
- Faiz Ahmed (Student1482107)
- Hafiz Muhammad Jazlan Ibrahim (Student1482115)
- Saghar Hassan (Student1487306)

**Project Dates**
- Start: 06-Mar-2026
- End: 06-Apr-2026

**Document Index**
- Acknowledgements
- eProject Synopsis
- eProject Analysis
- eProject Design
- DFDs (see `deliverables/DFD.md`)
- Flowcharts (see `deliverables/FLOWCHARTS.md`)
- Process Diagrams (see `deliverables/PROCESS_DIAGRAMS.md`)
- Database Design / Structure (see `deliverables/DB_DESIGN.md`)
- Screenshots (see `deliverables/SCREENSHOTS.md`)
- Source Code with Comments
- User Guide (see `deliverables/USER_GUIDE.md`)
- Developer Guide (see `deliverables/DEVELOPER_GUIDE.md`)
- Module Descriptions (see `deliverables/MODULE_DESCRIPTIONS.md`)
- Test Data (see `deliverables/TEST_DATA.md`)
- Installation Instructions (see `deliverables/INSTALLATION.md`)
- Assumptions (see `deliverables/ASSUMPTIONS.md`)

**Acknowledgements**
We acknowledge the guidance of the eProjects team and our mentors for their feedback and direction throughout this project. We also acknowledge Aptech for providing the eProject specification and learning framework.

**eProject Synopsis**
EarthScape Climate Agency is a data analytics application for climate monitoring. It supports uploading climate datasets, cleaning and validating data, producing dashboards, detecting anomalies, generating predictions, and exporting reports. The system also includes feedback/support workflows and performance logging to track operational health.

**eProject Analysis**
Problem statement: Climate change generates large and varied datasets that require consistent cleaning, analysis, and monitoring to enable timely decisions and risk awareness. The goal is to provide a unified platform to ingest data, analyze trends, surface anomalies, and generate actionable summaries.

Key requirements addressed:
- Authentication and authorization with roles.
- Dataset ingestion and validation.
- Analytical dashboards and visualizations.
- Basic predictive analytics.
- Alerts and support feedback.
- Performance monitoring.

Planned or documented for big-data scope:
- Hadoop/HDFS storage and distributed processing architecture.
- Streaming pipeline integration.
- Security and compliance controls.
- Backup and reliability planning.

**eProject Design**
Architecture overview:
- Streamlit UI for user experience.
- SQLite for local persistence (users, datasets, alerts, feedback, logs).
- Pandas for dataset preparation and analytics.
- scikit-learn for ML prediction.

Data flow:
- Admin uploads a dataset.
- System cleans and stores dataset in DB.
- Analysts open assigned datasets.
- Dashboard renders analytics and anomaly detection.
- Reports export structured summaries.

**DFDs**
See `deliverables/DFD.md`.

**Flowcharts**
See `deliverables/FLOWCHARTS.md`.

**Process Diagrams**
See `deliverables/PROCESS_DIAGRAMS.md`.

**Database Design / Structure**
See `deliverables/DB_DESIGN.md`.

**Screenshots**
See `deliverables/SCREENSHOTS.md`.

**Source Code with Comments**
The codebase is organized by modules with clear responsibilities:
- `main.py` for app routing and layout.
- `modules/auth.py` for authentication.
- `modules/dataset_manager.py` for upload, validation, and assignment.
- `modules/dashboard.py` for analytics and anomaly detection.
- `modules/prediction.py` for ML prediction.
- `modules/reports.py` for report generation.
- `modules/feedback.py` for feedback/support.
- `modules/performance.py` for performance monitoring.
- `modules/database.py` for SQLite operations.
- `modules/team_page.py` and `modules/team_data.py` for team info.

**User Guide**
See `deliverables/USER_GUIDE.md`.

**Developer Guide**
See `deliverables/DEVELOPER_GUIDE.md`.

**Module Descriptions**
See `deliverables/MODULE_DESCRIPTIONS.md`.

**Test Data**
See `deliverables/TEST_DATA.md`.

**Installation Instructions**
See `deliverables/INSTALLATION.md`.

**Assumptions**
See `deliverables/ASSUMPTIONS.md`.

**Future Enhancements**
- Integrate HDFS/Hadoop and MapReduce jobs for true big data processing.
- Add streaming ingestion for near real-time sensor feeds.
- Implement encryption at rest and in transit for data security.
- Add alert routing via email/SMS/notification services.
- Add automated backups and uptime monitoring.

**Conclusion**
EarthScape Climate Agency provides a working climate analytics system with core features for data ingestion, analysis, prediction, and reporting. The current implementation aligns with the primary functional requirements and includes a documented plan to reach full big data compliance as described in the specification.
