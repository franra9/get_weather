def format_weather(weather_data):
    # Format the weather data for display
    formatted_data = f"Temperature: {weather_data['temperature']}°C\n"
    formatted_data += f"Condition: {weather_data['condition']}\n"
    return formatted_data

def log_error(error_message):
    # Log the error message to a file or console
    with open('error.log', 'a') as log_file:
        log_file.write(f"ERROR: {error_message}\n")