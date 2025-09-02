from flask import Flask, request
from flask_cors import CORS
import csv
import os
from datetime import datetime, date
import argparse
from winotify import Notification

# ----------------------
# Arguments
# ----------------------
parser = argparse.ArgumentParser(description="YouTube Tracker Server")
parser.add_argument("--limit", type=int, required=True, help="Limite quotidienne en minutes")
args = parser.parse_args()

DAILY_LIMIT = args.limit * 60  # en secondes
LOG_FILE = "youtube_log.csv"

app = Flask(__name__)
CORS(app, origins=["https://www.youtube.com"])

# ----------------------
# Init CSV
# ----------------------
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "video_title", "video_url", "session_seconds"])

# ----------------------
# Suivi du temps quotidien
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
            title="⚠️ Attention !",
            msg=f"Tu as dépassé {hours}H{minutes} de visionnage aujourd'hui.",
            icon="C:\\Windows\\System32\\shell32.dll"  # tu peux mettre une icône custom
        )
        toast.show()

# ----------------------
# Endpoint Flask
# ----------------------
@app.route("/log", methods=["POST"])
def log():
    data = request.json
    timestamp = datetime.now().isoformat(timespec="seconds")

    print([timestamp, data["title"], data["url"], data["session_time"]])

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, data["title"], data["url"], data["session_time"]])

    add_daily_time(data["session_time"])
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(port=5000, debug=False)  # debug=False car tu veux en arrière-plan
