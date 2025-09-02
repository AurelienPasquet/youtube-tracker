import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import pandas as pd
import argparse

# ----------------------
# Arguments
# ----------------------
parser = argparse.ArgumentParser(description="YouTube Watch Time Report Generator")
parser.add_argument("--period", choices=["day", "week", "month"], default="day",
                    help="Reporting period: daily, weekly, or monthly")
args = parser.parse_args()

# ----------------------
# Load CSV
# ----------------------
df = pd.read_csv("youtube_log.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date
df["week"] = df["timestamp"].dt.strftime("%Y-W%U")
df["month"] = df["timestamp"].dt.to_period("M")

# ----------------------
# Group data by period
# ----------------------
if args.period == "day":
    grouped = df.groupby("date")["session_seconds"].sum()
    title = "Daily YouTube Watch Time"
    xlabel = "Date"
elif args.period == "week":
    grouped = df.groupby("week")["session_seconds"].sum()
    title = "Weekly YouTube Watch Time"
    xlabel = "Week"
else:  # month
    grouped = df.groupby("month")["session_seconds"].sum()
    title = "Monthly YouTube Watch Time"
    xlabel = "Month"

# ----------------------
# Convert seconds to HH:MM
# ----------------------
def seconds_to_hhmm(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{int(hours):02d}:{int(minutes):02d}"

grouped_hhmm = grouped.apply(seconds_to_hhmm)

# ----------------------
# Print report to console
# ----------------------
print("\n=== YouTube Watch Time Report ===")
print(grouped_hhmm.to_string())

# ----------------------
# Plot improved bar chart
# ----------------------

plt.figure(figsize=(12, 6))
bars = plt.bar(grouped.index.astype(str), grouped, color='skyblue')  # height in seconds
plt.title(title, fontsize=16)
plt.xlabel(xlabel, fontsize=12)
plt.ylabel("Watch Time", fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Custom y-axis formatter: seconds -> HH:MM
def sec_to_hhmm(x, pos):
    hours = int(x // 3600)
    minutes = int((x % 3600) // 60)
    return f"{hours:02d}:{minutes:02d}"

plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(sec_to_hhmm))

plt.tight_layout()
plt.show()