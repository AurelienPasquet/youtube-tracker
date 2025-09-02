# YouTube Watch Time Tracker

This project helps you **track how much time you spend watching YouTube videos** each day.  
It consists of:
- A **Tampermonkey userscript** that runs in your browser and logs video sessions.
- A **Flask server** that records watch time into a CSV file and sends Windows notifications when daily limits are exceeded.
- A **report generator** to analyze your YouTube activity (daily / weekly / monthly).

⚠️ This project is designed for **Windows**, since it uses native Windows notifications.

---

## 📦 Requirements

- Python 3.8+  
- Browser with [Tampermonkey](https://www.tampermonkey.net/) extension installed  
- Windows 10/11  

Install Python dependencies:
```bash
pip install -r requirements.txt
````

---

## 🚀 Setup & Usage

### 1. Install the userscript

1. Open your browser with Tampermonkey installed.
2. Create a new script and copy the contents of **`userscript.js`** into it.
3. Save.
4. Now, every time you watch a YouTube video, the script will log your session to the local Flask server.

---

### 2. Run the server

Start the Flask server to receive logs and send notifications.

#### Option A: Run manually

```bash
python yt_tracker_server.py --limit 60
```

* `--limit 60` → sends a Windows notification if you watch more than **60 minutes per day**.

#### Option B: Run automatically at Windows startup

1. Create a file `start_tracker.bat` in the project folder:

   ```bat
   @echo off
   pythonw C:\path\to\project\yt_tracker_server.py --limit 60
   ```
2. Place a shortcut to this `.bat` file in:

   ```
   shell:startup
   ```

   (Press `Win+R`, type `shell:startup`, and paste the shortcut.)

This will launch the tracker automatically when your PC starts.

---

### 3. Generate reports

Use **`yt_report.py`** to analyze your activity:

```bash
python yt_report.py --period daily
python yt_report.py --period weekly
python yt_report.py --period monthly
```

Reports are based on the data stored in `youtube_log.csv`.

---

## 🔔 Features

* Logs time spent on each YouTube video.
* Daily total watch time tracking.
* Windows notifications when exceeding a customizable daily limit.
* CSV-based history.
* Reporting tool (daily/weekly/monthly).

---

## 🛠 Notes

* The tracker only works when the Flask server is running.
* Notifications are implemented with `winotify`, which integrates with Windows 10/11 notification center.
* Data is stored locally (`youtube_log.csv`), nothing is uploaded externally.


