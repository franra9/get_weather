import unittest
from get_weather.core import WeatherFetcher

class TestWeatherFetcher(unittest.TestCase):

    def setUp(self):
        self.fetcher = WeatherFetcher()

    def test_fetch_weather(self):
        # Test fetching weather data
        weather_data = self.fetcher.fetch_weather("New York")
        self.assertIsNotNone(weather_data)
        self.assertIn("temperature", weather_data)
        self.assertIn("condition", weather_data)

    def test_parse_weather(self):
        # Test parsing weather data
        raw_data = {"temp": 75, "weather": "Sunny"}
        parsed_data = self.fetcher.parse_weather(raw_data)
        self.assertEqual(parsed_data["temperature"], 75)
        self.assertEqual(parsed_data["condition"], "Sunny")

if __name__ == '__main__':
    unittest.main()