import pandas as pd
from datetime import datetime
import argparse
import matplotlib.pyplot as plt

# ----------------------
# Arguments
# ----------------------
parser = argparse.ArgumentParser(description="YouTube Report Generator")
parser.add_argument("--period", choices=["day", "week", "month"], required=True,
                    help="Période du rapport")
args = parser.parse_args()

# ----------------------
# Charger CSV
# ----------------------
df = pd.read_csv("youtube_log.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date
df["week"] = df["timestamp"].dt.strftime("%Y-W%U")
df["month"] = df["timestamp"].dt.to_period("M")

# ----------------------
# Sélection période
# ----------------------
if args.period == "day":
    grouped = df.groupby("date")["session_seconds"].sum()
    title = "Temps quotidien passé sur YouTube"
    xlabel = "Date"

elif args.period == "week":
    grouped = df.groupby("week")["session_seconds"].sum()
    title = "Temps hebdomadaire passé sur YouTube"
    xlabel = "Semaine"

else:  # month
    grouped = df.groupby("month")["session_seconds"].sum()
    title = "Temps mensuel passé sur YouTube"
    xlabel = "Mois"

# Convertir en minutes
grouped = grouped / 60

# ----------------------
# Affichage console
# ----------------------
print("\n=== Rapport YouTube ===")
print(grouped.round(2).to_string())

# ----------------------
# Graphique
# ----------------------
plt.figure(figsize=(10, 5))
grouped.plot(kind="bar")
plt.title(title)
plt.ylabel("Minutes")
plt.xlabel(xlabel)
plt.tight_layout()
plt.show()
