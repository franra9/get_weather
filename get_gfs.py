import os
import requests
import subprocess
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
# Script to download GFS data, convert it to NetCDF, and plot temperature and precipitation

# Coordinates for Barcelona and Olot, Catalonia
locations = {
    "Barcelona": (41.3888, 2.159),
#    "Olot": (42.1854, 2.4881)
}

# Time configuration (latest cycle and 2-day forecast)
now = datetime.utcnow()
date_str = now.strftime('%Y%m%d')
hour = (now.hour // 6) * 6
cycle = f"{hour:02d}"

# 2-day forecast, every 3 hours
forecast_hours = list(range(0, 49, 3))  # 2 days = 48h, 3h step

# Bounding box around both locations
all_lats = [lat for lat, lon in locations.values()]
all_lons = [lon for lat, lon in locations.values()]
leftlon = min(all_lons) - 1.0
rightlon = max(all_lons) + 1.0
toplat = max(all_lats) + 1.0
bottomlat = min(all_lats) - 1.0

# Output directories
os.makedirs("gfs_data/grib", exist_ok=True)
os.makedirs("gfs_data/netcdf", exist_ok=True)

# Download and convert data for 4 days (forecast hours)
for fh in forecast_hours:
    fhr = f"{fh:03d}"

    url = (
        f"https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?"
        f"file=gfs.t{cycle}z.pgrb2.0p25.f{fhr}"
        f"&lev_2_m_above_ground=on"
        f"&lev_surface=on"
        f"&var_TMP=on&var_APCP=on"
        f"&subregion=&leftlon={leftlon}&rightlon={rightlon}"
        f"&toplat={toplat}&bottomlat={bottomlat}"
        f"&dir=%2Fgfs.{date_str}%2F{cycle}%2Fatmos"
    )

    print(f"Downloading forecast hour {fhr}...")
    response = requests.get(url)
    if response.status_code == 200:
        grib_path = f"gfs_data/grib/gfs_{date_str}_{cycle}z_f{fhr}.grb2"
        nc_path = grib_path.replace("/grib/", "/netcdf/").replace(".grb2", ".nc")

        with open(grib_path, "wb") as f:
            f.write(response.content)
        print(f"Saved: {grib_path}")

        # Convert GRIB2 to NetCDF
        subprocess.run(["wgrib2", grib_path, "-netcdf", nc_path], check=True)
        print(f"Converted to NetCDF: {nc_path}")
    else:
        print(f"Failed to download forecast hour {fhr}: {response.status_code}")

# Prepare data containers for each location
results = {}
times = []

for loc_name, (olat, olon) in locations.items():
    temperature = []
    precipitation = []
    precip0 = 0  # For cumulative precipitation
    for idx, fh in enumerate(forecast_hours):
        fhr = f"{fh:03d}"
        nc_path = f"gfs_data/netcdf/gfs_{date_str}_{cycle}z_f{fhr}.nc"

        # Calculate the actual UTC hour for the forecast
        forecast_datetime = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=fh)
        if loc_name == "Barcelona":
            if idx == 0:
                times.clear()
            hour_label = forecast_datetime.strftime('%d %b %H:%M UTC')
            times.append(hour_label)

        # Load the NetCDF file using xarray
        ds = xr.open_dataset(nc_path, engine="netcdf4")

        # Extract the relevant variables: TMP (temperature at 2m) and APCP (precipitation)
        temp = ds['TMP_2maboveground'].sel(latitude=olat, longitude=olon, method='nearest').values - 273.15  # Convert K to °C
        if fhr != '000':
            precip = ds['APCP_surface'].sel(latitude=olat, longitude=olon, method='nearest').values  # Precipitation in mm
            precipitation.append((precip - precip0).item())
            precip0 = precip
        else:
            precip0 = 0
            precipitation.append(0)
        temperature.append(temp.item())
    results[loc_name] = {"temperature": temperature, "precipitation": precipitation}

# Plot the results
fig, ax1 = plt.subplots(figsize=(12, 7))

# Temperature plot (left y-axis)
ax1.set_xlabel('Forecast Time (UTC)')
ax1.set_ylabel('Temperature (°C)', color='tab:red')
for loc_name in locations:
    ax1.plot(times, results[loc_name]["temperature"], marker='o', label=f'Temperature {loc_name}')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax1.set_xticks(range(len(times)))
ax1.set_xticklabels(times, rotation=45)

# Precipitation plot (right y-axis)
ax2 = ax1.twinx()
ax2.set_ylabel('Precipitation (mm)', color='tab:blue')
width = 0.35
x = np.arange(len(times))
for i, loc_name in enumerate(locations):
    offset = (i - 0.1) * width

    print(results[loc_name]["precipitation"])

    ax2.bar(x + offset, results[loc_name]["precipitation"], width=width, alpha=0.5, label=f'Precipitation {loc_name}')
ax2.tick_params(axis='y', labelcolor='tab:blue')

# Legends
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper left')

# Title and layout
plt.title('2-Day Weather Forecast: Barcelona(Catalonia)')
fig.tight_layout()

# Show plot
plt.show()
