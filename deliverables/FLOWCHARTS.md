# Flowcharts

**Flowchart 1: Login**

```
Start
  |
  v
Enter Username + Password
  |
  v
Validate User
  |
  +--> Invalid -> Show Error -> End
  |
  v
Check Active Status
  |
  +--> Inactive -> Show Error -> End
  |
  v
Create Session -> Go to Datasets Page
  |
  v
End
```

**Flowchart 2: Upload and Save Dataset (Admin)**

```
Start
  |
  v
Select CSV File
  |
  v
Validate Columns
  |
  +--> Missing -> Show Error -> End
  |
  v
Clean Data (types, range, fill missing)
  |
  +--> Empty -> Show Error -> End
  |
  v
Preview Cleaned Data
  |
  v
Save Dataset
  |
  v
Assign to Analysts (Optional)
  |
  v
End
```

**Flowchart 3: Prediction**

```
Start
  |
  v
Open Dataset
  |
  v
Train Model if Needed
  |
  +--> Not enough data -> Show Warning -> End
  |
  v
Enter Feature Values
  |
  v
Generate Prediction
  |
  v
Show Result
  |
  v
End
```
