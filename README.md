# METAR Wind Visualization Script for Termux on Android

This project provides a self-contained Python script for visualizing wind speed, gusts, and wind direction using METAR data for Dallas/Fort Worth International Airport (KDFW). The plot is designed to run inside Termux on Android and display the output image using the system viewer via `termux-open`.

## Features
- Downloads decoded METAR data for a specified time window.
- Parses wind speed, gust, and direction.
- Converts speeds from knots to mph.
- Plots wind speed as a stair-step line and gusts as red points.
- Overlays wind direction arrows on the wind speed line.
- Annotates the current time with a vertical dashed line.
- Configurable plot size (width and height).
- Saves plot as a PNG image.


## Integration into Termux on Android

### 1. Install Required Tools
```sh
pkg update && pkg upgrade
pkg install python
pip install matplotlib pandas requests
termux-setup-storage
```

### 2. Save Script
Store the Python script as:
```sh
~/metar_script.py
```

### 3. Create Widget Script
```sh
mkdir -p ~/.shortcuts
nano ~/.shortcuts/Wind_Plot.sh
```
Contents:
```sh
#!/data/data/com.termux/files/usr/bin/bash
python ~/metar_script.py
# Copy plot to shared storage
cp ~/wind_plot.png ~/storage/downloads/wind_plot.png
# Open image with default viewer
termux-open ~/storage/downloads/wind_plot.png
```
Make it executable:
```sh
chmod +x ~/.shortcuts/Wind_Plot.sh
```

### 4. Enable Display Over Other Apps
Go to:
```text
Settings → Apps → Special Access → Display over other apps → Termux → Allow
```

### 5. Add Termux Widget
- Long press home screen → Widgets → Termux Widget
- Drag widget → select `Wind_Plot.sh`

## Troubleshooting

### Widget not appearing
- Install **Termux:Widget** from F-Droid
- Ensure `~/.shortcuts` exists and has executable `.sh` scripts
- Reboot phone or restart launcher

### `termux-open` opens wrong app
- Uninstall other file managers (e.g., FV File Explorer)
- Retry `termux-open`, select **Photos**, tap **Always**

### `termux-open` shows "media not found"
- Ensure `termux-setup-storage` has been run
- File must be copied to `/storage/emulated/0/Download/`

### Arrows all face sideways
- Ensure `angles='uv'` is set in `quiver()`
- Do **not** use `angles='xy'` with datetime x-axis


## How to Install Pandas in Termux on Android
Step-by-Step Instructions:

### 1. Open Termux and update packages:

```pkg update && pkg upgrade
```

### 2. Install Python:

```pkg install python
```

### 3. Install the Termux user repository (tur-repo), which contains prebuilt pandas:

```pkg install tur-repo
```

### 4. Install pandas directly:

```pkg install python-pandas
```

This will install pandas along with its dependencies, including numpy