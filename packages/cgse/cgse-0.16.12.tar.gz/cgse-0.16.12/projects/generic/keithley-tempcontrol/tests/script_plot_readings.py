import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

timestamps = []
readings_101 = []
readings_102 = []

with open("buffer_vat.log", "r") as file:
    for line in file:
        data = json.loads(line.strip())

        # Parse timestamp
        timestamp = datetime.fromisoformat(data["timestamp"])
        timestamps.append(timestamp)

        # Extract temperature readings
        readings_101.append(data["readings"]["101"])
        readings_102.append(data["readings"]["102"])

plt.figure(figsize=(12, 6))

plt.plot(timestamps, readings_101, label="Sensor buffer tank", marker=".", linewidth=2)
plt.plot(timestamps, readings_102, label="Sensor room", marker=".", linewidth=2)

# Format the plot
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Readings Buffer Tank in Basement")
plt.legend()
plt.grid(True, alpha=0.3)

time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600  # hours

if time_span <= 2:  # Less than 2 hours
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
elif time_span <= 12:  # Less than 12 hours
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.xticks(rotation=45)
elif time_span <= 48:  # 12-48 hours (up to 2 days)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=4))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=2))
    plt.xticks(rotation=45)
else:  # More than 2 days
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=6))
    plt.xticks(rotation=45)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Optional: Save the plot
plt.savefig("buffer_vat.png", dpi=300, bbox_inches="tight")

plt.show()
