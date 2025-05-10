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

    # Extract the relevant variables: TMP (temperature at 2m) and APCP (precipitation)
    temp = ds['TMP'].sel(lat=olat, lon=olon, method='nearest').values - 273.15  # Convert K to °C
    precip = ds['APCP'].sel(lat=olat, lon=olon, method='nearest').values  # Precipitation in mm

    # Append values
    times.append(f"{fhr} hours")
    temperature.append(temp)
    precipitation.append(precip)

# Plot the results
fig, ax1 = plt.subplots(figsize=(10, 6))

# Temperature plot (left y-axis)
ax1.set_xlabel('Forecast Hour (H)')
ax1.set_ylabel('Temperature (°C)', color='tab:red')
ax1.plot(times, temperature, color='tab:red', marker='o', label='Temperature (°C)')
ax1.tick_params(axis='y', labelcolor='tab:red')

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