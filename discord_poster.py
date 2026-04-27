import os
import csv
import json
import datetime
import requests
from io import StringIO

STATE_FILE = "state.json"


# ------------------------
# Time
# ------------------------
def get_current_year_week():
    today = datetime.date.today()
    iso = today.isocalendar()
    return iso.year, iso.week


# ------------------------
# State handling
# ------------------------
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"posted": []}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def should_post(year, week, state):
    key = f"{year}-{week}"
    return key not in state.get("posted", [])


def mark_posted(year, week, state):
    key = f"{year}-{week}"
    state.setdefault("posted", []).append(key)
    save_state(state)


# ------------------------
# CSV parsing
# ------------------------
def get_names_from_schema(schema_str, year, week):
    names = []

    f = StringIO(schema_str)
    reader = csv.reader(f, delimiter=';')

    header = next(reader)

    for row in reader:
        if not row or len(row) < 4:
            continue

        try:
            row_year = int(row[0])
            row_week = int(row[1])
        except ValueError:
            continue

        if row_year == year and row_week == week:
            for cell in row[3:]:
                if cell.strip() == "":
                    break
                names.append(cell.strip())

            return names

    return []


# ------------------------
# Discord
# ------------------------
def send_discord_message(webhook_url, names, year, week):
    if not names:
        return

    message = f"🧹 Städvecka {week} ({year})\n\n"
    message += "\n".join(f"- {name}" for name in names)

    response = requests.post(webhook_url, json={"content": message})

    if response.status_code != 204:
        raise Exception(f"Discord error: {response.status_code}, {response.text}")


# ------------------------
# Main flow
# ------------------------
def main():
    schema = os.environ.get("SCHEMA")
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")

    if not schema:
        raise Exception("Missing SCHEMA secret")

    if not webhook:
        raise Exception("Missing DISCORD_WEBHOOK_URL secret")

    year, week = get_current_year_week()
    state = load_state()

    names = get_names_from_schema(schema, year, week)

    if not names:
        print(f"No cleaning scheduled for {year}-W{week}")
        return

    if not should_post(year, week, state):
        print("Already posted, skipping.")
        return

    print(f"Posting for {year}-W{week}: {names}")

    send_discord_message(webhook, names, year, week)
    mark_posted(year, week, state)


if __name__ == "__main__":
    main()
