from datetime import datetime, date
from winotify import Notification
from flask import Flask, request
from flask_cors import CORS

import argparse
import csv
import os

# ----------------------
# Arguments
# ----------------------
parser = argparse.ArgumentParser(description="YouTube Tracker Server")
parser.add_argument("--limit", type=int, required=True, help="Daily limit in minutes")
args = parser.parse_args()

DAILY_LIMIT = args.limit * 60  # in seconds

PATH = os.path.abspath(os.path.dirname(__file__))
LOG_FILE = "youtube_log.csv"
LOG_FILE_PATH = os.path.join(PATH, LOG_FILE)

app = Flask(__name__)
CORS(app, origins=["https://www.youtube.com"])

# ----------------------
# Init CSV (header without title column)
# ----------------------
if not os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "video_url", "session_seconds"])

# ----------------------
# Daily time tracking
# ----------------------
# daily_usage keeps cumulative seconds per ISO date string (YYYY-MM-DD).
# notified keeps whether we've already shown the toast for that specific date.
daily_usage = {}
notified = {}

def add_daily_time(seconds: int):
    """Accumulate today's time and show a one-time toast only at the crossing moment."""
    today = date.today().isoformat()

    prev = daily_usage.get(today, 0)
    curr = prev + max(0, int(seconds))
    daily_usage[today] = curr

    # Reset old keys (optional hygiene): keep only today's keys
    # This avoids 'notified' carrying over to future days.
    for d in list(daily_usage.keys()):
        if d != today:
            daily_usage.pop(d, None)
    for d in list(notified.keys()):
        if d != today:
            notified.pop(d, None)

    # Show toast ONLY when we cross from below-limit to at/over-limit,
    # and only if we haven't already shown it today.
    crossed_now = (prev < DAILY_LIMIT) and (curr >= DAILY_LIMIT)
    if crossed_now and not notified.get(today, False):
        hours = args.limit // 60
        minutes = args.limit % 60
        toast = Notification(
            app_id="YouTube Tracker",
            title="⚠️ Caution!",
            msg=f"You have exceeded {hours}h{minutes:02d} of viewing time today.",
            icon="C:\\Windows\\System32\\shell32.dll"  # or your custom icon path
        )
        toast.show()
        notified[today] = True

# ----------------------
# Flask endpoint
# ----------------------
@app.route("/log", methods=["POST"])
def log():
    data = request.json or {}
    session_time = int(data.get("session_time", 0))
    url = data.get("url", "") or ""
    timestamp = datetime.now().isoformat(timespec="seconds")

    # Skip if no time or URL isn't a video page
    if session_time <= 0 or "https://www.youtube.com/watch?v=" not in url.strip():
        return {"status": "skipped"}

    # Read existing rows (if any)
    rows = []
    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
    except FileNotFoundError:
        pass  # file does not exist yet

    # If CSV has a header, ensure we don't treat it as data row
    # Header is ["timestamp", "video_url", "session_seconds"]
    has_header = bool(rows) and rows[0] == ["timestamp", "video_url", "session_seconds"]

    # Update last row if same URL, otherwise append
    if rows and (len(rows) > 1 or not has_header):
        last_row = rows[-1]
        # last_row structure: [timestamp, url, session_seconds]
        if last_row[1] == url:
            # Accumulate time
            prev_time = int(last_row[2])
            new_time = prev_time + session_time
            rows[-1] = [timestamp, url, str(new_time)]
            with open(LOG_FILE_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            print(f"Updated last row: {rows[-1]}")
        else:
            with open(LOG_FILE_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, url, session_time])
            print(f"Appended new row: {[timestamp, url, session_time]}")
    else:
        # Either empty file or file with only header → append first data row
        with open(LOG_FILE_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, url, session_time])
        print(f"Appended first data row: {[timestamp, url, session_time]}")

    add_daily_time(session_time)
    return {"status": "ok"}


if __name__ == "__main__":
    # debug=False recommended for background usage
    app.run(port=5000, debug=False)
