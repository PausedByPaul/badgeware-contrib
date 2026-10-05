"""Configuration for KiloGramowy Weather Station."""

APP_NAME = "KG Weather"

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240

LOCAL_TEMP_OFFSET_C = 0.0
LOCAL_SENSOR_READ_MS = 1000
LTR_SENSOR_READ_MS = 100
LTR_USE_DEDICATED_I2C = False

COMMENTARY_REFRESH_MS = 30 * 60 * 1000
RECENT_COMMENT_HISTORY = 8
GLOBAL_REALITY_HISTORY = 32
PER_CATEGORY_REALITY_HISTORY = 12

WEATHER_CACHE_PATH = "/weather_station_cache.json"
WEATHER_CACHE_TEMP_PATH = "/weather_station_cache.tmp"
COMMENT_HISTORY_PATH = "/weather_station_history.json"
COMMENT_HISTORY_TEMP_PATH = "/weather_station_history.tmp"

WEATHER_LOCATION_NAME = "LONDON"
WEATHER_LATITUDE = 51.5074
WEATHER_LONGITUDE = -0.1278
WEATHER_TIMEZONE = "Europe/London"
OPEN_METEO_HOST = "api.open-meteo.com"
OPEN_METEO_PATH = "/v1/forecast"
OPEN_METEO_CURRENT_FIELDS = (
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "weather_code",
    "cloud_cover",
    "pressure_msl",
    "surface_pressure",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "is_day",
)
OPEN_METEO_HOURLY_FIELDS = (
    "temperature_2m",
    "precipitation_probability",
    "weather_code",
    "is_day",
)
OPEN_METEO_DAILY_FIELDS = (
    "weather_code",
    "temperature_2m_min",
    "temperature_2m_max",
    "precipitation_probability_max",
)
OPEN_METEO_FORECAST_HOURS = 7
OPEN_METEO_FORECAST_DAYS = 5
WEATHER_STARTUP_FETCH_DELAY_MS = 2000
CURRENT_WEATHER_REFRESH_MS = 15 * 60 * 1000
CURRENT_WEATHER_RETRY_MS = 60 * 1000
WEATHER_CACHE_WRITE_MIN_MS = 30 * 60 * 1000
WEATHER_HTTP_TIMEOUT_S = 5
WEATHER_HTTP_MAX_BYTES = 32768

AUTO_BRIGHTNESS_ENABLED = True
AUTO_BRIGHTNESS_MIN = 0.22
AUTO_BRIGHTNESS_MAX = 1.0
AUTO_BRIGHTNESS_DEFAULT = 0.70
AUTO_BRIGHTNESS_SAMPLE_MS = 250
AUTO_BRIGHTNESS_SMOOTHING = 0.35
AUTO_BRIGHTNESS_HYSTERESIS = 0.025
AUTO_BRIGHTNESS_CURVE = (
    (0, 0.22),
    (80, 0.22),
    (300, 0.32),
    (1000, 0.45),
    (2500, 0.58),
    (5000, 0.70),
    (12000, 0.88),
    (25000, 1.0),
)

INPUT_DELAY_MS = 170

OUTDOOR_REFRESH_MS = 20 * 60 * 1000
OUTDOOR_RETRY_MS = 60 * 1000
