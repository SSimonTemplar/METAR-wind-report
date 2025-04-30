import numpy as np
import pandas as pd
import requests
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# Convert METAR timestamp (DDHHMMZ) to Central US local time
def parse_metar_time(timestr):
    """Convert 6-digit METAR time (DDHHMM) to Central US time."""
    day = int(timestr[:2])
    hour = int(timestr[2:4])
    minute = int(timestr[4:6])
    now = datetime.now(ZoneInfo("UTC"))
    if day > now.day and now.day < 5:
        month = now.month - 1 or 12
        year = now.year if now.month > 1 else now.year - 1
    else:
        month = now.month
        year = now.year
    try:
        utc_dt = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("UTC"))
        return utc_dt.astimezone(ZoneInfo("America/Chicago")).isoformat()
    except ValueError:
        return None

# Download and parse raw METAR reports for KDFW for the past N hours
# Extract wind direction, speed, gusts, and timestamp
# Return a cleaned DataFrame

def fetch_metar(hours=1):
    url = f"https://aviationweather.gov/api/data/metar?ids=KDFW&hours={hours}&order=id%2C-obs&sep=true"
    response = requests.get(url)
    lines = response.text.strip().split('\n')
    data = []
    wind_regex = re.compile(r'(\d{3}|VRB)(\d{2})(G\d{2})?KT')
    time_regex = re.compile(r'(\d{6})Z')
    fetch_time = datetime.now(ZoneInfo("America/Chicago")).isoformat()
    for line in lines:
        wind_match = wind_regex.search(line)
        time_match = time_regex.search(line)
        direction = wind_match.group(1) if wind_match else None
        speed = int(wind_match.group(2)) if wind_match else None
        gust = int(wind_match.group(3)[1:]) if wind_match and wind_match.group(3) else None
        raw_time = time_match.group(1) if time_match else None
        report_time = parse_metar_time(raw_time) if raw_time else None
        if report_time:
            data.append({
                'report_time': report_time,
                'fetch_time': fetch_time,
                'report': line.strip(),
                'wind_direction': direction,
                'wind_speed_kt': speed,
                'wind_gust_kt': gust
            })
    return pd.DataFrame(data)

# Update a DataFrame with newly fetched METAR entries, avoiding duplicates by report_time

def update_metar_df(metar_df, hours=1):
    new_df = fetch_metar(hours=hours)
    if metar_df.empty:
        return new_df.copy()
    metar_df.set_index('report_time', inplace=True, drop=False)
    new_df.set_index('report_time', inplace=True, drop=False)
    new_entries = new_df.loc[~new_df.index.isin(metar_df.index)]
    updated_df = pd.concat([metar_df, new_entries])
    return updated_df.reset_index(drop=True)

# Plot wind speed (stair-step), gusts (points), and wind direction (arrows)
# Extend last value to now, annotate current time, and save as PNG

def plot_wind(metar_df, width=4, height=4):
    metar_df['report_time'] = pd.to_datetime(metar_df['report_time'])
    kt_to_mph = 1.15078
    metar_df['wind_speed_mph'] = metar_df['wind_speed_kt'] * kt_to_mph
    metar_df['wind_gust_mph'] = metar_df['wind_gust_kt'] * kt_to_mph
    now = datetime.now(ZoneInfo("America/Chicago"))
    if not metar_df.empty:
        extended_df = metar_df.copy()
        last_idx = extended_df.index[-1]
        extended_row = extended_df.loc[[last_idx]].copy()
        extended_row['report_time'] = now
        extended_df = pd.concat([extended_df, extended_row], ignore_index=True)
    else:
        extended_df = metar_df.copy()
    extended_df = extended_df.sort_values(by='report_time')

    fig, ax = plt.subplots(figsize=(width, height))
    ax.step(extended_df['report_time'], extended_df['wind_speed_mph'], where='post', label='Wind Speed (mph)')
    ax.plot(metar_df['report_time'], metar_df['wind_gust_mph'], 'o', label='Wind Gusts (mph)', color='red')
    ax.axvline(now, color='gray', linestyle='--', linewidth=1, label='Current Time')

    formatter = DateFormatter('%b-%d %H:%M', tz=ZoneInfo("America/Chicago"))
    ax.xaxis.set_major_formatter(formatter)
    plt.xticks(rotation=90, fontsize=6)

    # Wind direction arrows: point where wind is blowing to (from + 180°)
    N = len(metar_df)
    sampled_df = metar_df.iloc[np.linspace(0, len(metar_df) - 1, N, dtype=int)].copy()
    dir_deg = pd.to_numeric(sampled_df['wind_direction'], errors='coerce')
    dir_rad = np.radians((dir_deg + 180) % 360)
    u = np.cos(dir_rad)
    v = np.sin(dir_rad)
    x = sampled_df['report_time']
    y = sampled_df['wind_speed_mph']
    ax.quiver(
        x, y, u, v,
        angles='uv',
        scale_units='xy',
        color='orange',
        alpha=0.8,
        zorder=3
    )

    ax.set_ylabel('Speed (mph)')
    ax.set_title('Wind Speed (DFW)')
    ax.set_ylim(bottom=0)
    ax.grid(True)
    ax.legend(fontsize=6)
    plt.tight_layout()
    plt.savefig("wind_plot.png", dpi=150)

# Entry point
metar_df = pd.DataFrame()
metar_df = update_metar_df(metar_df, hours=24)
plot_wind(metar_df)
