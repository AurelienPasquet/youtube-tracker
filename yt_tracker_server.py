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
# Init CSV
# ----------------------
if not os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "video_title", "video_url", "session_seconds"])

# ----------------------
# Daily time tracking
# ----------------------
daily_usage = {}

def add_daily_time(seconds):
    today = date.today().isoformat()
    if today not in daily_usage:
        daily_usage[today] = 0
    daily_usage[today] += seconds

    if daily_usage[today] >= DAILY_LIMIT:
        hours = f"{args.limit // 60}"
        minutes = f"0{args.limit % 60}" if args.limit % 60 < 10 else f"{args.limit % 60}"
        toast = Notification(
            app_id="YouTube Tracker",
            title="⚠️ Caution !",
            msg=f"You have exceeded {hours}H{minutes} of viewing time today.",
            icon="C:\\Windows\\System32\\shell32.dll"  # or custom icon
        )
        toast.show()

# ----------------------
# Flask endpoint 
# ----------------------
@app.route("/log", methods=["POST"])
def log():
    data = request.json
    session_time = int(data.get("session_time", 0))
    url = data.get("url", "")
    timestamp = datetime.now().isoformat(timespec="seconds")

    # Skip if session time = 0 or url = homepage
    if session_time == 0 or url.strip() in ["https://www.youtube.com/", "https://www.youtube.com"]:
        return {"status": "skipped"}

    rows = []
    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
    except FileNotFoundError:
        pass  # file does not exist yet

    if rows and rows[-1][1] == url:
        # Accumulate session time with the last row
        prev_time = int(rows[-1][2])
        new_time = prev_time + session_time
        rows[-1] = [timestamp, url, str(new_time)]
        with open(LOG_FILE_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print(f"Updated last row: {rows[-1]}")
    else:
        # Append new row
        with open(LOG_FILE_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, url, session_time])
        print(f"Appended new row: {[timestamp, url, session_time]}")

    add_daily_time(session_time)
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(port=5000, debug=False)  # debug=False for background run
