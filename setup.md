# Setup Guide

## What You Need

- **Python 3.9 or higher** — [python.org/downloads](https://www.python.org/downloads/)
- **An Anthropic API key** — [console.anthropic.com](https://console.anthropic.com/)
- **A Google Cloud service account** with the Google Sheets API enabled — [Google Cloud Console](https://console.cloud.google.com/)
- **A Google Sheet** with two tabs:
  - `Sheet1` — where completed research results are logged
  - `Requests` — where pending research jobs are queued (optional)

---

## Steps

**1. Download this repo**

Click the green **Code** button and select **Download ZIP**, or clone it:

```
git clone <repo-url>
cd ai-research-log-agent
```

**2. Install dependencies**

```
pip install -r requirements.txt
```

**3. Configure your environment**

Copy the example file and fill in your keys:

```
cp .env.example .env
```

Open `.env` and add your values (the video shows exactly where to find each one):

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SHEET_ID=your_google_sheet_id_here
CREDENTIALS_PATH=credentials.json
```

**4. Add your Google credentials**

Download your service account `credentials.json` from Google Cloud and place it in the root folder. The video walks through this step in detail.

**5. Run it**

```
python agent.py "your research topic here"
```

Example:
```
python agent.py "AI adoption in financial services Q1 2026"
```

---

## What Gets Created

After running, you'll have:

- A report file in `/reports` named by date and topic
- A new row in your Google Sheet:

```
Topic        | AI adoption in financial services Q1 2026
Date         | 2026-05-20
Summary      | AI adoption across financial services accelerated...
Key Findings | • 67% of mid-size banks deployed AI in lending workflows...
Sources      | https://... / https://...
Next Steps   | • Evaluate vendor options for AI-assisted underwriting...
```

---

## Files in This Repo

| File | Purpose |
|---|---|
| `agent.py` | Main pipeline — research, save report, log to sheet |
| `append_row.py` | Google Sheets integration |
| `.env.example` | Template for your API keys and config |
| `reports/` | Where generated report files are saved |

> **Never commit** `.env` or `credentials.json` — they contain your private keys. Both are excluded by `.gitignore`.

---

## Copy the Code

### append_row.py
Copy this file into your project folder. The video shows exactly where each value gets inserted.

```python
import sys
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("SHEET_ID")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "credentials.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_sheet(tab_name):
    creds = Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(tab_name)


def append_report(topic, date, summary, findings, sources, next_steps):
    sheet = _get_sheet("Sheet1")
    sheet.append_row([topic, date, summary, findings, sources, next_steps])
    print("Report row appended successfully.")


def get_pending_requests():
    sheet = _get_sheet("Requests")
    rows = sheet.get_all_records()
    pending = [(i, r) for i, r in enumerate(rows)
               if r.get("Status") == "Pending"]
    if not pending:
        print("No pending requests.")
    else:
        print(json.dumps(pending, indent=2))
    return pending


def update_last_row(findings, sources, next_steps):
    sheet = _get_sheet("Sheet1")
    last_row = len(sheet.get_all_values())
    sheet.update_cell(last_row, 4, findings)
    sheet.update_cell(last_row, 5, sources)
    sheet.update_cell(last_row, 6, next_steps)
    print(f"Row {last_row} updated successfully.")


def mark_completed(row_index):
    sheet = _get_sheet("Requests")
    sheet.update_cell(row_index + 2, 6, "Completed")
    print(f"Row {row_index + 1} marked as Completed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python append_row.py '<json>'")
        print("  python append_row.py --check-requests")
        print("  python append_row.py --mark-done <n>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--check-requests":
        get_pending_requests()
    elif command == "--update-last":
        data = json.loads(sys.argv[2])
        update_last_row(data["findings"], data["sources"], data["next_steps"])
    elif command == "--mark-done":
        mark_completed(int(sys.argv[2]))
    else:
        data = json.loads(command)
        append_report(
            data["topic"], data["date"], data["summary"],
            data["findings"], data["sources"], data["next_steps"]
        )
```
