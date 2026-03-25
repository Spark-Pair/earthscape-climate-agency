# Data Flow Diagrams (DFDs)

**DFD Level 0 (Context Diagram)**

External Entities
- Admin
- Analyst
- eProjects Team

System
- EarthScape Climate Agency

Data Stores
- D1: Users
- D2: Datasets
- D3: Feedback
- D4: Performance Logs
- D5: Alerts

Flows
- Admin -> System: Login, Upload Dataset, Assign Access, Manage Users
- Analyst -> System: Login, Open Dataset, Run Analysis, Submit Feedback
- System -> Admin/Analyst: Dashboards, Reports, Predictions, Alerts
- System -> D1/D2/D3/D4/D5: Persist user, dataset, feedback, logs, alerts
- System -> eProjects Team: Report, Source Code, Demo Video

**DFD Level 1 (Main Processes)**

Process 1.0 Authentication
- Inputs: Username, Password
- Outputs: Session, Role
- Data Store: D1 Users

Process 2.0 Dataset Management
- Inputs: CSV Upload
- Outputs: Clean Dataset, Assignments
- Data Store: D2 Datasets

Process 3.0 Analytics
- Inputs: Dataset
- Outputs: KPIs, Trends, Anomalies
- Data Store: D5 Alerts (snapshot logs)

Process 4.0 Prediction
- Inputs: Dataset, User Inputs
- Outputs: Temperature Prediction

Process 5.0 Reporting
- Inputs: Dataset, Alerts
- Outputs: Summary Report, CSV Export

Process 6.0 Feedback Support
- Inputs: Feedback Form
- Outputs: Ticket Status
- Data Store: D3 Feedback

Process 7.0 Performance Monitoring
- Inputs: Action Timings
- Outputs: Performance Charts
- Data Store: D4 Performance Logs
