"""Provider-independent weather and sensor normalization helpers."""


OUTDOOR_FIELDS = (
    "condition",
    "temperature_c",
    "humidity_pct",
    "feels_like_c",
    "high_c",
    "low_c",
    "humidity_percent",
    "pressure_hpa",
    "pressure_msl_hpa",
    "surface_pressure_hpa",
    "wind_speed",
    "wind_speed_kmh",
    "wind_direction",
    "wind_direction_deg",
    "wind_gust_kmh",
    "precipitation_mm",
    "precipitation_probability",
    "precipitation_amount",
    "cloud_pct",
    "weather_code",
    "observed_at",
    "interval",
    "location",
    "visibility",
    "uv",
    "is_day",
    "timestamp",
)

HOURLY_FIELDS = (
    "time",
    "label",
    "temperature_c",
    "condition",
    "precipitation_probability_pct",
    "precipitation_probability",
    "weather_code",
    "is_day",
    "wind_speed",
)

DAILY_FIELDS = (
    "date",
    "temperature_min_c",
    "temperature_max_c",
    "high_c",
    "low_c",
    "condition",
    "precipitation_probability_max_pct",
    "precipitation_probability",
    "weather_code",
)

SECRET_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "token",
    "password",
    "secret",
    "wifi",
)


def _copy_fields(data, fields):
    clean = {}
    if not isinstance(data, dict):
        return clean
    for field in fields:
        value = data.get(field)
        if value is not None:
            clean[field] = value
    return clean


def normalize_current(data):
    return _copy_fields(data, OUTDOOR_FIELDS)


def normalize_hourly(items):
    if not isinstance(items, list):
        return []
    return [_copy_fields(item, HOURLY_FIELDS) for item in items if isinstance(item, dict)]


def normalize_daily(items):
    if not isinstance(items, list):
        return []
    return [_copy_fields(item, DAILY_FIELDS) for item in items if isinstance(item, dict)]


def normalize_weather_payload(current=None, hourly=None, daily=None, status="LIVE"):
    current = current or {}
    clean_hourly = normalize_hourly(hourly or [])
    clean_daily = normalize_daily(daily or [])
    section_source = status if status in ("LIVE", "CACHED") else "OFFLINE"
    return {
        "current": normalize_current(current),
        "hourly": clean_hourly,
        "daily": clean_daily,
        "status": status,
        "hourly_source": section_source if clean_hourly else "OFFLINE",
        "daily_source": section_source if clean_daily else "OFFLINE",
        "location": current.get("location"),
    }


WMO_CONDITIONS = {
    0: "clear",
    1: "mainly_clear",
    2: "partly_cloudy",
    3: "overcast",
    45: "fog",
    48: "fog",
    51: "drizzle",
    53: "drizzle",
    55: "drizzle",
    56: "freezing_drizzle",
    57: "freezing_drizzle",
    61: "rain",
    63: "rain",
    65: "rain",
    66: "freezing_rain",
    67: "freezing_rain",
    71: "snow",
    73: "snow",
    75: "snow",
    77: "snow",
    80: "showers",
    81: "showers",
    82: "showers",
    85: "snow_showers",
    86: "snow_showers",
    95: "thunderstorm",
    96: "thunderstorm",
    99: "thunderstorm",
}


def wmo_condition(code):
    try:
        numeric = int(code)
    except (TypeError, ValueError):
        return "unknown"
    return WMO_CONDITIONS.get(numeric, "unknown")


def contains_secret_key(data):
    if isinstance(data, dict):
        for key, value in data.items():
            lowered = str(key).lower()
            if any(marker in lowered for marker in SECRET_MARKERS):
                return True
            if contains_secret_key(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if contains_secret_key(item):
                return True
    return False


def condition_category(current):
    current = current or {}
    condition = str(current.get("condition", "")).lower().replace(" ", "_")
    temp = current.get("temperature_c")
    feels = current.get("feels_like_c")
    humidity = current.get("humidity_percent")
    wind = current.get("wind_speed")
    precip = current.get("precipitation_probability")
    is_day = current.get("is_day", True)

    temp_ref = feels if feels is not None else temp
    if temp_ref is not None and temp_ref <= 0:
        return "freezing"
    if temp_ref is not None and temp_ref <= 5:
        return "cold"
    if temp_ref is not None and temp_ref >= 32:
        return "very_hot"
    if temp_ref is not None and temp_ref >= 27:
        return "hot"

    if "thunder" in condition:
        return "thunderstorm"
    if "snow" in condition:
        return "snow"
    if "heavy" in condition and "rain" in condition:
        return "heavy_rain"
    if "rain" in condition or "shower" in condition:
        return "rain"
    if "drizzle" in condition:
        return "drizzle"
    if "fog" in condition or "mist" in condition:
        return "fog"
    if "overcast" in condition:
        return "overcast"
    if "cloud" in condition:
        if "part" in condition:
            return "partly_cloudy"
        return "cloudy"
    if "sun" in condition:
        if "mostly" in condition:
            return "mostly_sunny"
        return "sunny"
    if "clear" in condition:
        return "clear" if is_day else "clear_night"

    if wind is not None and wind >= 45:
        return "very_windy"
    if wind is not None and wind >= 25:
        return "windy"
    if humidity is not None and humidity >= 82:
        return "humid"
    if humidity is not None and humidity <= 32:
        return "dry"
    if precip is not None and precip >= 55:
        return "rain"
    if not is_day:
        return "night"
    return "cloudy"


def contextual_category(current):
    current = current or {}
    base = condition_category(current)
    condition = str(current.get("condition", "")).lower().replace(" ", "_")
    temp = current.get("temperature_c")
    feels = current.get("feels_like_c")
    temp_ref = feels if feels is not None else temp
    wind = current.get("wind_speed")
    humidity = current.get("humidity_percent")
    is_day = current.get("is_day", True)

    rainy = base in ("rain", "heavy_rain", "drizzle", "thunderstorm") or "rain" in condition or "drizzle" in condition
    windy = wind is not None and wind >= 25
    cold = temp_ref is not None and temp_ref <= 6
    freezing = temp_ref is not None and temp_ref <= 0
    hot = temp_ref is not None and temp_ref >= 27
    humid = humidity is not None and humidity >= 78
    sunny = base in ("sunny", "mostly_sunny", "clear") or "sun" in condition or "clear" in condition

    if rainy and windy:
        return "rain_wind"
    if freezing and windy:
        return "freezing_wind"
    if rainy and cold:
        return "cold_rain"
    if hot and humid:
        return "hot_humid"
    if sunny and cold:
        return "sunny_cold"
    if rainy and not is_day:
        return "rain_night"
    if base in ("clear", "clear_night") and not is_day:
        return "clear_night"
    if windy and cold:
        return "windy_cold"
    return base


def local_category(reading):
    reading = reading or {}
    temp = reading.get("temperature_c")
    humidity = reading.get("humidity_percent")
    pressure = reading.get("pressure_hpa")
    lux = reading.get("lux")

    if temp is not None and temp < 17:
        return "local_cold"
    if temp is not None and temp > 26:
        return "local_hot"
    if humidity is not None and humidity > 68:
        return "local_humid"
    if humidity is not None and humidity < 35:
        return "local_dry"
    if lux is not None and lux < 20:
        return "local_dark"
    if lux is not None and lux > 1200:
        return "local_bright"
    if pressure is not None and pressure < 995:
        return "local_pressure_low"
    if pressure is not None and pressure > 1030:
        return "local_pressure_high"
    if temp is not None or humidity is not None or pressure is not None or lux is not None:
        return "local_comfortable"
    return "local_unavailable"


def compare_local_outdoor(local_reading, outdoor_current):
    if not local_reading or not outdoor_current:
        return None
    inside = local_reading.get("temperature_c")
    outside = outdoor_current.get("temperature_c")
    if inside is None or outside is None:
        return None
    if outside <= 6 and inside >= 19:
        return "outside_rejected"
    if outside >= 28 and inside <= 23:
        return "indoor_wins"
    if abs(inside - outside) >= 8:
        return "temperature_gap"
    return None
