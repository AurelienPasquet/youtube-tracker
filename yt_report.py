import matplotlib.pyplot as plt
import pandas as pd
import argparse

# ----------------------
# Arguments
# ----------------------
parser = argparse.ArgumentParser(description="YouTube Report Generator")
parser.add_argument("--period", choices=["day", "week", "month"], required=True,
                    help="Report period")
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
# Period selection
# ----------------------
if args.period == "day":
    grouped = df.groupby("date")["session_seconds"].sum()
    title = "Daily time spent on YouTube"
    xlabel = "Date"

elif args.period == "week":
    grouped = df.groupby("week")["session_seconds"].sum()
    title = "Weekly time spent on YouTube"
    xlabel = "Week"

else:
    grouped = df.groupby("month")["session_seconds"].sum()
    title = "Monthly time spent on YouTube"
    xlabel = "Month"

# Convert to hours
grouped = grouped / 3600

# ----------------------
# Console display
# ----------------------
print("\n=== Youtube Report ===")
print(grouped.round(2).to_string())

# ----------------------
# Graph
# ----------------------
plt.figure(figsize=(10, 5))
grouped.plot(kind="bar")
plt.title(title)
plt.ylabel("Hours")
plt.xlabel(xlabel)
plt.tight_layout()
plt.show()
