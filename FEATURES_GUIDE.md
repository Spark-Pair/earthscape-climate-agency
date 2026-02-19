# EarthScape Climate Agency - Feature Guide

## What this app is for

EarthScape Climate Agency helps teams work with climate datasets.

It allows users to:
- upload and clean climate data
- analyze trends (temperature, rainfall, CO2)
- detect anomalies and risk alerts
- predict future temperature with ML
- export reports
- submit support feedback
- track performance timings

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
- Assign dataset access to analysts
- View dataset access mapping

### 3) Analytics and Reports
Location: `Datasets` page -> `Analytics Workspace`
- Dashboard with KPIs, trends, yearly table
- Anomaly detection and disaster risk alerts
- ML prediction for future year temperature
- Export yearly CSV and summary text report

### 4) Feedback and Monitoring
Location: `Datasets` page -> `Analytics Workspace` tabs
- View all feedback
- Update feedback status
- View performance logs/charts/averages

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

## Sidebar Pages
- `Users` (Admin only)
- `Datasets` (Admin + Analyst)
- `Logout`

## Datasets Page Tabs
For Admin:
- `Upload & Assign`
- `Saved Datasets`
- `Analytics Workspace`
- `Access Matrix`

For Analyst:
- `Saved Datasets`
- `Analytics Workspace`

## Analytics Workspace Tabs
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

The app cleans data by:
- removing duplicates
- converting numeric values safely
- dropping invalid year/month
- enforcing month 1-12
- filling missing numeric values with mean

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
