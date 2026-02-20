# EarthScape Climate Agency - Feature Guide

## What this app is for

EarthScape Climate Agency helps teams upload, manage, and analyze climate datasets.

It allows users to:
- upload and clean climate data
- analyze trends and KPIs
- detect anomalies and disaster-risk alerts
- predict temperature using ML under custom conditions
- export reports
- submit support feedback
- monitor app performance timings

## Who can use it

There are 2 roles:
- Admin
- Analyst

## What Admin can do

### 1) User Management
Location: `Users` page (sidebar)
- See all users
- Add new users (analysts)
- Activate/deactivate users
- View user status

### 2) Dataset Management
Location: `Datasets` page -> `Upload & Assign`, `Saved Datasets`, `Access Matrix`
- Upload CSV datasets
- Auto-clean and validate data
- Save datasets to database
- Assign dataset access to one or more analysts
- Assign later or take back access
- Delete saved datasets
- View dataset access mapping

### 3) Analytics and Reports
Location: `Datasets` page -> `Analytics Workspace`
- Dashboard with preview, KPIs, trends, anomaly and risk alerts
- ML prediction using multivariate linear regression
- Export CSV report and summary report

### 4) Feedback and Monitoring
Location: `Datasets` page -> `Analytics Workspace` tabs
- View all feedback
- Update feedback status / delete feedback
- View performance logs and averages

## What Analyst can do

### 1) Assigned Datasets Only
Location: `Datasets` page -> `Saved Datasets`
- See only datasets assigned to them
- Open assigned dataset

### 2) Analysis Features
Location: `Datasets` page -> `Analytics Workspace`
- Use dashboard and visual analytics
- Run prediction
- Generate/export reports
- Submit feedback
- View own performance logs

## Main pages and where to find features

### Sidebar Pages
- `Users` (Admin only)
- `Datasets` (Admin + Analyst)
- `Team`
- `Logout`

### Datasets Page Tabs
For Admin:
- `Upload & Assign`
- `Saved Datasets`
- `Analytics Workspace`
- `Access Matrix`

For Analyst:
- `Saved Datasets`
- `Analytics Workspace`

### Analytics Workspace Tabs
- `Dashboard`
- `Prediction`
- `Reports`
- `Feedback`
- `Performance`

## Dataset rules (required columns)

When uploading CSV, these columns must exist:
- `Year`
- `Month`
- `Temperature`
- `Rainfall`
- `CO2`
- `Humidity`
- `WindSpeed`

The app cleans data by:
- removing duplicates
- converting numeric values safely
- dropping invalid year/month
- enforcing month in range `1-12`
- filling missing numeric values with mean

## Dashboard and anomaly logic

- Year range filter
- KPIs: Avg/Max Temperature, Avg Rainfall, Avg CO2, Avg Humidity, Avg WindSpeed
- Trend charts for Temperature, Rainfall, CO2, Humidity, WindSpeed
- Z-score anomaly detection (temperature/rainfall thresholds configurable)
- Disaster risk alerts:
  - Heatwave risk: `Temperature > threshold`
  - Flood risk: `Rainfall > threshold`

## Prediction module (current)

Model: Linear Regression

Training data:
- Features `X`: `Year`, `Month`, `Rainfall`, `CO2`, `Humidity`, `WindSpeed`
- Target `y`: `Temperature`

Behavior:
- model is trained once when dataset is loaded
- model is stored in session state
- prediction does not retrain model each click
- metrics shown using train/test split:
  - MAE
  - RMSE
  - R2

## Security and access behavior

- User remains logged in until logout.
- Deactivated users cannot log in.
- Analyst access is restricted to assigned datasets.
- Admin has full management visibility.

## Default credentials

First run default admin:
- Username: `admin`
- Password: `admin123`

Change password after first setup in production workflow.
