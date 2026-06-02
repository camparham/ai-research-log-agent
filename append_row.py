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
