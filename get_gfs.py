import os
import requests
import subprocess
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Coordinates for Olot, Catalonia
olat = 42.1833
olon = 2.5

# Time configuration (latest cycle and 3-day forecast)
now = datetime.utcnow()
date_str = now.strftime('%Y%m%d')
hour = (now.hour // 6) * 6
cycle = f"{hour:02d}"
forecast_hours = list(range(0, 72, 3))  # 3-day forecast, every 3 hours

# Bounding box around Olot
leftlon = olon - 1.0
rightlon = olon + 1.0
toplat = olat + 1.0
bottomlat = olat - 1.0

# Output directories
os.makedirs("gfs_data/grib", exist_ok=True)
os.makedirs("gfs_data/netcdf", exist_ok=True)

# Download and convert data for 3 days (forecast hours)
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

# Load NetCDF files and extract temperature and precipitation for Olot
# Time steps: [0-72 hours]
times = []
temperature = []
precipitation = []



for fh in forecast_hours:
    fhr = f"{fh:03d}"
    nc_path = f"gfs_data/netcdf/gfs_{date_str}_{cycle}z_f{fhr}.nc"

    # Load the NetCDF file using xarray
    ds = xr.open_dataset(nc_path)
    print(ds.data_vars)
    print(fhr)


    # Extract the relevant variables: TMP (temperature at 2m) and APCP (precipitation)
    temp = ds['TMP_2maboveground'].sel(latitude=olat, longitude=olon, method='nearest').values - 273.15  # Convert K to °C
    if fhr != '000':
        precip=precip
        precip0=precip
        precip = ds['APCP_surface'].sel(latitude=olat, longitude=olon, method='nearest').values  # Precipitation in mm
    else:
        precip0 = 0
        precip=0
    # Append values
    times.append(f"{fhr} hours")
    temperature.append(temp)
    precipitation.append(precip-precip0)

# Plot the results
fig, ax1 = plt.subplots(figsize=(10, 6))

# Temperature plot (left y-axis)
ax1.set_xlabel('Forecast Hour (H)')
ax1.set_ylabel('Temperature (°C)', color='tab:red')
ax1.plot(times, temperature, color='tab:red', marker='o', label='Temperature (°C)')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax1.set_xticks(range(len(times)))
ax1.set_xticklabels(times, rotation=45)

# Precipitation plot (right y-axis)
ax2 = ax1.twinx()
ax2.set_ylabel('Precipitation (mm)', color='tab:blue')
ax2.bar(times, precipitation, color='tab:blue', alpha=0.5, label='Precipitation (mm)')
ax2.tick_params(axis='y', labelcolor='tab:blue')


# Title and layout
plt.title('3-Day Weather Forecast for Olot, Catalonia')

fig.tight_layout()

# Show plot
plt.show()
