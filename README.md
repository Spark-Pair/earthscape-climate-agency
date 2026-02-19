# EarthScape Climate Agency - Setup & Run Walkthrough

This guide explains prerequisites and exact commands to run the app from a fresh clone.

## 1. Prerequisites

Install these first:
- Python 3.10+ (recommended: Python 3.11 or 3.12)
- Git

Verify:
```bash
python3 --version
git --version
```

On Windows, use `python` instead of `python3` in commands below.

## 2. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd sem6-eProject
```

## 3. Create and Activate Virtual Environment

### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the App

```bash
streamlit run main.py
```

If `streamlit` command is not found:
```bash
python -m streamlit run main.py
```

## 6. First Login

On first run, database and default admin are auto-created.

Default admin credentials:
- Username: `admin`
- Password: `admin123`

## 7. What Happens on First Run

- `earthscape.db` is created automatically.
- Required tables are created automatically.
- Default admin user is created if missing.

## 8. Common Issues

### `No module named streamlit`
Install dependencies again inside the activated virtual environment:
```bash
pip install -r requirements.txt
```

### Wrong Python interpreter in IDE
Make sure your IDE uses:
- Linux/macOS: `./venv/bin/python`
- Windows: `./venv/Scripts/python.exe`

### Port already in use
Run on another port:
```bash
streamlit run main.py --server.port 8502
```
