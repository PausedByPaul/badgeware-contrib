"""Outdoor weather provider abstraction and Open-Meteo current weather."""

try:
    import json
except ImportError:  # pragma: no cover
    json = None

try:
    from fetch import AsyncFetch, HTTPException
except ImportError:  # pragma: no cover
    AsyncFetch = None

    class HTTPException(Exception):
        pass

try:
    from . import weather_config as cfg
    from . import weather_model
    from . import persistent_cache
except ImportError:
    import weather_config as cfg
    import weather_model
    import persistent_cache


STATUS_LIVE = "LIVE"
STATUS_CACHED = "CACHED"
STATUS_OFFLINE = "OFFLINE"

FETCH_IDLE = "IDLE"
FETCH_WAIT_WIFI = "WAIT_WIFI"
FETCH_FETCHING = "FETCHING"
FETCH_LIVE = "LIVE"
FETCH_ERROR_RETRY = "ERROR_RETRY"

WIFI_WAIT = "WIFI_WAIT"
WIFI_FAIL = "WIFI_FAIL"
DNS_FAIL = "DNS_FAIL"
CONNECT_FAIL = "CONNECT_FAIL"
SOCKET_FAIL = "SOCKET_FAIL"
TLS_FAIL = "TLS_FAIL"
TIMEOUT = "TIMEOUT"
HTTP_STATUS = "HTTP_STATUS"
BODY_EMPTY = "BODY_EMPTY"
BODY_TOO_LARGE = "BODY_TOO_LARGE"
JSON_FAIL = "JSON_FAIL"
CURRENT_MISSING = "CURRENT_MISSING"
MODEL_FAIL = "MODEL_FAIL"
CONVERSION_EXCEPTIONS = (TypeError, ValueError)
FETCH_EXCEPTIONS = (AttributeError, OSError, RuntimeError, TypeError, ValueError)


class WeatherProviderError(OSError):
    def __init__(self, code, message="", status=None):
        super().__init__(message or code)
        self.code = code
        self.status = status


_WIFI_STATE_UNSET = object()


def _ticks_diff(now, then):
    try:
        import time
        if hasattr(time, "ticks_diff"):
            return time.ticks_diff(now, then)
    except (AttributeError, ImportError, OSError, RuntimeError, TypeError, ValueError):
        pass
    return int(now) - int(then)


def _timer_due(now, then, interval):
    if then is None:
        return True
    return _ticks_diff(now, then) >= interval


def _quote(value, safe=",.-_"):
    safe_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" + safe
    out = []
    for char in str(value):
        if char in safe_chars:
            out.append(char)
        else:
            for byte in char.encode("utf-8"):
                out.append("%{:02X}".format(byte))
    return "".join(out)


def _float_or_none(value):
    if value is None:
        return None
    try:
        return float(value)
    except CONVERSION_EXCEPTIONS:
        return None


def _int_or_none(value):
    if value is None:
        return None
    try:
        return int(value)
    except CONVERSION_EXCEPTIONS:
        return None


def _wind_direction_label(degrees):
    value = _float_or_none(degrees)
    if value is None:
        return None
    labels = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    return labels[int((value + 22.5) // 45) % len(labels)]


def build_open_meteo_path():
    current = ",".join(cfg.OPEN_METEO_CURRENT_FIELDS)
    hourly = ",".join(cfg.OPEN_METEO_HOURLY_FIELDS)
    daily = ",".join(cfg.OPEN_METEO_DAILY_FIELDS)
    pairs = (
        ("latitude", "{:.4f}".format(float(cfg.WEATHER_LATITUDE))),
        ("longitude", "{:.4f}".format(float(cfg.WEATHER_LONGITUDE))),
        ("current", current),
        ("hourly", hourly),
        ("daily", daily),
        ("forecast_hours", str(int(cfg.OPEN_METEO_FORECAST_HOURS))),
        ("forecast_days", str(int(cfg.OPEN_METEO_FORECAST_DAYS))),
        ("temperature_unit", "celsius"),
        ("wind_speed_unit", "kmh"),
        ("precipitation_unit", "mm"),
        ("timezone", cfg.WEATHER_TIMEZONE),
    )
    query = "&".join("{}={}".format(key, _quote(value)) for key, value in pairs)
    return "{}?{}".format(cfg.OPEN_METEO_PATH, query)


def normalize_open_meteo_current(data, now_ms=0):
    if not isinstance(data, dict):
        return None
    current = data.get("current")
    if not isinstance(current, dict):
        return None

    code = _int_or_none(current.get("weather_code"))
    surface_pressure = _float_or_none(current.get("surface_pressure"))
    pressure_msl = _float_or_none(current.get("pressure_msl"))
    pressure = surface_pressure if surface_pressure is not None else pressure_msl
    humidity = _int_or_none(current.get("relative_humidity_2m"))
    wind_direction = _float_or_none(current.get("wind_direction_10m"))
    precipitation = _float_or_none(current.get("precipitation"))
    wind_speed = _float_or_none(current.get("wind_speed_10m"))
    wind_gust = _float_or_none(current.get("wind_gusts_10m"))
    cloud = _int_or_none(current.get("cloud_cover"))
    is_day = current.get("is_day")
    if is_day is not None:
        is_day = bool(is_day)

    normalized = {
        "condition": weather_model.wmo_condition(code),
        "temperature_c": _float_or_none(current.get("temperature_2m")),
        "feels_like_c": _float_or_none(current.get("apparent_temperature")),
        "humidity_percent": humidity,
        "humidity_pct": humidity,
        "pressure_hpa": pressure,
        "pressure_msl_hpa": pressure_msl,
        "surface_pressure_hpa": surface_pressure,
        "wind_speed": wind_speed,
        "wind_speed_kmh": wind_speed,
        "wind_direction": _wind_direction_label(wind_direction),
        "wind_direction_deg": wind_direction,
        "wind_gust_kmh": wind_gust,
        "precipitation_amount": precipitation,
        "precipitation_mm": precipitation,
        "cloud_pct": cloud,
        "weather_code": code,
        "is_day": is_day,
        "observed_at": current.get("time"),
        "interval": _int_or_none(current.get("interval")),
        "timestamp": now_ms,
        "location": cfg.WEATHER_LOCATION_NAME,
    }
    return weather_model.normalize_current(normalized)


def _array_value(values, index):
    if not isinstance(values, (list, tuple)):
        return None
    if index < 0 or index >= len(values):
        return None
    return values[index]


def _hour_label_from_iso(value):
    text = str(value or "")
    marker = text.find("T")
    if marker < 0 or marker + 3 >= len(text):
        return "--"
    return text[marker + 1:marker + 3] + ":00"


def _is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _weekday_index(year, month, day):
    if month < 3:
        month += 12
        year -= 1
    k = year % 100
    j = year // 100
    h = (day + ((13 * (month + 1)) // 5) + k + (k // 4) + (j // 4) + (5 * j)) % 7
    return (h + 5) % 7


def weekday_label(date_text):
    try:
        year = int(str(date_text)[0:4])
        month = int(str(date_text)[5:7])
        day = int(str(date_text)[8:10])
    except CONVERSION_EXCEPTIONS:
        return "--"
    if month < 1 or month > 12 or day < 1:
        return "--"
    month_days = (31, 29 if _is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    if day > month_days[month - 1]:
        return "--"
    return ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")[_weekday_index(year, month, day)]


def normalize_open_meteo_hourly(data, current_time=None, limit=6):
    hourly = data.get("hourly") if isinstance(data, dict) else None
    if not isinstance(hourly, dict):
        return []
    times = hourly.get("time")
    if not isinstance(times, (list, tuple)):
        return []
    selected = []
    for index, stamp in enumerate(times):
        if current_time and str(stamp) <= str(current_time):
            continue
        code = _int_or_none(_array_value(hourly.get("weather_code"), index))
        precip = _float_or_none(_array_value(hourly.get("precipitation_probability"), index))
        is_day = _array_value(hourly.get("is_day"), index)
        if is_day is not None:
            is_day = bool(is_day)
        item = {
            "time": stamp,
            "label": _hour_label_from_iso(stamp),
            "temperature_c": _float_or_none(_array_value(hourly.get("temperature_2m"), index)),
            "precipitation_probability_pct": precip,
            "precipitation_probability": precip,
            "weather_code": code,
            "condition": weather_model.wmo_condition(code),
            "is_day": is_day,
        }
        selected.append(item)
        if len(selected) >= limit:
            break
    return weather_model.normalize_hourly(selected)


def normalize_open_meteo_daily(data, limit=5):
    daily = data.get("daily") if isinstance(data, dict) else None
    if not isinstance(daily, dict):
        return []
    times = daily.get("time")
    if not isinstance(times, (list, tuple)):
        return []
    selected = []
    for index, date_text in enumerate(times[:limit]):
        code = _int_or_none(_array_value(daily.get("weather_code"), index))
        low = _float_or_none(_array_value(daily.get("temperature_2m_min"), index))
        high = _float_or_none(_array_value(daily.get("temperature_2m_max"), index))
        precip = _float_or_none(_array_value(daily.get("precipitation_probability_max"), index))
        item = {
            "date": date_text,
            "temperature_min_c": low,
            "temperature_max_c": high,
            "low_c": low,
            "high_c": high,
            "precipitation_probability_max_pct": precip,
            "precipitation_probability": precip,
            "weather_code": code,
            "condition": weather_model.wmo_condition(code),
        }
        selected.append(item)
    return weather_model.normalize_daily(selected)


def _phase_label(fetcher):
    phase = getattr(fetcher, "_phase", None)
    if phase == "dns":
        return "FETCH DNS"
    if phase == "connect":
        return "FETCH CONNECT"
    if phase == "send":
        return "FETCH TLS"
    if phase in ("headers", "body"):
        return "FETCH HTTP"
    status = getattr(fetcher, "status", None)
    done = getattr(fetcher.__class__, "DONE", 2)
    error = getattr(fetcher.__class__, "ERROR", 3)
    if status == done:
        return "LIVE"
    if status == error:
        return "ERR"
    return "FETCH"


def _classify_fetch_exception(exc, fetcher=None):
    if isinstance(exc, WeatherProviderError):
        return exc.code
    text = str(exc).lower()
    if "timed out" in text or "timeout" in text or "etimedout" in text:
        return TIMEOUT
    if "max_bytes" in text or "exceeds" in text:
        return BODY_TOO_LARGE
    if "json" in text:
        return JSON_FAIL
    if "http error" in text:
        return HTTP_STATUS
    phase = getattr(fetcher, "_phase", None)
    if phase == "dns":
        return DNS_FAIL
    if phase == "connect":
        return CONNECT_FAIL
    if phase == "send" and ("ssl" in text or "tls" in text or "handshake" in text):
        return TLS_FAIL
    if phase == "send":
        return CONNECT_FAIL
    return SOCKET_FAIL


def _error_label(code, http_status=None):
    if code == DNS_FAIL:
        return "ERR DNS"
    if code in (CONNECT_FAIL, SOCKET_FAIL):
        return "ERR CONNECT"
    if code == TLS_FAIL:
        return "ERR TLS"
    if code == HTTP_STATUS:
        return "ERR HTTP {}".format(http_status or "")
    if code == JSON_FAIL:
        return "ERR JSON"
    if code == TIMEOUT:
        return "ERR TIMEOUT"
    if code == BODY_TOO_LARGE:
        return "ERR BIG"
    if code == BODY_EMPTY:
        return "ERR EMPTY"
    if code in (CURRENT_MISSING, MODEL_FAIL):
        return "ERR MODEL"
    if code == WIFI_WAIT:
        return "WIFI WAIT"
    if code == WIFI_FAIL:
        return "WIFI FAIL"
    return "ERR FETCH"


class OpenMeteoProvider:
    def __init__(
        self,
        fetch_cls=None,
        host=None,
        path_builder=None,
        timeout_s=None,
        max_bytes=None,
        step_bytes=None,
    ):
        self.fetch_cls = fetch_cls if fetch_cls is not None else AsyncFetch
        self.host = host or cfg.OPEN_METEO_HOST
        self.path_builder = path_builder or build_open_meteo_path
        self.timeout_s = cfg.WEATHER_HTTP_TIMEOUT_S if timeout_s is None else timeout_s
        self.max_bytes = cfg.WEATHER_HTTP_MAX_BYTES if max_bytes is None else max_bytes
        self.step_bytes = step_bytes
        self.fetcher = None
        self.fetcher_created = 0
        self.active = False
        self.last_stage = FETCH_IDLE
        self.last_error_code = None
        self.last_error_text = ""
        self.last_http_status = None
        self.last_payload = None
        self._http_error = None

    def _ensure_fetcher(self):
        if self.fetcher is not None:
            return self.fetcher
        if self.fetch_cls is None:
            raise WeatherProviderError(SOCKET_FAIL, "AsyncFetch unavailable")
        kwargs = {
            "use_tls": True,
            "timeout": self.timeout_s,
            "max_bytes": self.max_bytes,
        }
        if self.step_bytes is not None:
            kwargs["step_bytes"] = self.step_bytes
        self.fetcher = self.fetch_cls(self.host, 443, **kwargs)
        self.fetcher_created += 1
        if hasattr(self.fetcher, "on_error"):
            self.fetcher.on_error(self._handle_http_error)
        return self.fetcher

    def _handle_http_error(self, fetcher):
        self._http_error = HTTPException(fetcher)
        return True

    def start(self, _now_ms=0):
        if self.active:
            return False
        fetcher = self._ensure_fetcher()
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        }
        self._http_error = None
        self.last_error_code = None
        self.last_error_text = ""
        self.last_http_status = None
        self.last_stage = "FETCH DNS"
        fetcher.fetch(self.path_builder(), headers=headers)
        self.active = True
        return True

    def update(self, now_ms=0):
        if not self.active:
            return None
        fetcher = self._ensure_fetcher()
        try:
            status = fetcher.update()
        except FETCH_EXCEPTIONS as exc:
            self.active = False
            self.last_http_status = getattr(fetcher, "http_status", None)
            self.last_error_code = _classify_fetch_exception(exc, fetcher)
            self.last_error_text = str(exc)[:48]
            self.last_stage = _error_label(self.last_error_code, self.last_http_status)
            raise WeatherProviderError(self.last_error_code, self.last_error_text, self.last_http_status) from exc

        self.last_http_status = getattr(fetcher, "http_status", None)
        self.last_stage = _phase_label(fetcher)
        fetching = getattr(self.fetch_cls, "FETCHING", 1)
        done = getattr(self.fetch_cls, "DONE", 2)
        error = getattr(self.fetch_cls, "ERROR", 3)
        if status == fetching:
            return None
        if status == error:
            self.active = False
            self.last_error_code = HTTP_STATUS if self.last_http_status else SOCKET_FAIL
            self.last_error_text = str(self._http_error or self.last_error_code)[:48]
            self.last_stage = _error_label(self.last_error_code, self.last_http_status)
            raise WeatherProviderError(self.last_error_code, self.last_error_text, self.last_http_status)
        if status != done:
            return None

        self.active = False
        try:
            data = fetcher.to_json()
        except FETCH_EXCEPTIONS as exc:
            self.last_error_code = JSON_FAIL
            self.last_error_text = str(exc)[:48]
            self.last_stage = "ERR JSON"
            raise WeatherProviderError(JSON_FAIL, self.last_error_text, self.last_http_status) from exc
        try:
            current = normalize_open_meteo_current(data, now_ms)
            hourly = normalize_open_meteo_hourly(data, current.get("observed_at") if current else None)
            daily = normalize_open_meteo_daily(data)
        except FETCH_EXCEPTIONS as exc:
            self.last_error_code = MODEL_FAIL
            self.last_error_text = str(exc)[:48]
            self.last_stage = "ERR MODEL"
            raise WeatherProviderError(MODEL_FAIL, self.last_error_text, self.last_http_status) from exc
        if not current:
            self.last_error_code = CURRENT_MISSING
            self.last_error_text = "missing current"
            self.last_stage = "ERR MODEL"
            raise WeatherProviderError(CURRENT_MISSING, self.last_error_text, self.last_http_status)
        payload = weather_model.normalize_weather_payload(current, hourly, daily, STATUS_LIVE)
        payload["status"] = STATUS_LIVE
        payload["hourly_source"] = STATUS_LIVE if payload.get("hourly") else STATUS_OFFLINE
        payload["daily_source"] = STATUS_LIVE if payload.get("daily") else STATUS_OFFLINE
        self.last_payload = payload
        self.last_stage = "LIVE"
        self.last_error_code = None
        self.last_error_text = ""
        return payload

    def reset(self):
        self.active = False
        if self.fetcher is not None and hasattr(self.fetcher, "reset"):
            self.fetcher.reset()


def mock_weather_payload(now_ms=0):
    current = {
        "condition": "partly_cloudy",
        "temperature_c": 18.4,
        "feels_like_c": 17.8,
        "high_c": 21.0,
        "low_c": 12.0,
        "humidity_percent": 61,
        "humidity_pct": 61,
        "pressure_hpa": 1012,
        "pressure_msl_hpa": 1012,
        "surface_pressure_hpa": 1012,
        "wind_speed": 18,
        "wind_speed_kmh": 18,
        "wind_direction": "W",
        "wind_direction_deg": 270,
        "wind_gust_kmh": 28,
        "precipitation_probability": 28,
        "precipitation_amount": 0.2,
        "precipitation_mm": 0.2,
        "cloud_pct": 46,
        "weather_code": 2,
        "observed_at": "mock",
        "location": cfg.WEATHER_LOCATION_NAME,
        "visibility": 12,
        "uv": 3,
        "is_day": True,
        "timestamp": now_ms,
    }
    hourly = [
        {"time": "Now", "temperature_c": 18, "condition": "partly_cloudy", "precipitation_probability": 28, "wind_speed": 18},
        {"time": "+1h", "temperature_c": 19, "condition": "mostly_sunny", "precipitation_probability": 18, "wind_speed": 16},
        {"time": "+2h", "temperature_c": 20, "condition": "mostly_sunny", "precipitation_probability": 12, "wind_speed": 15},
        {"time": "+3h", "temperature_c": 20, "condition": "cloudy", "precipitation_probability": 22, "wind_speed": 17},
        {"time": "+4h", "temperature_c": 18, "condition": "drizzle", "precipitation_probability": 46, "wind_speed": 21},
        {"time": "+5h", "temperature_c": 17, "condition": "rain", "precipitation_probability": 62, "wind_speed": 24},
    ]
    daily = [
        {"date": "Today", "high_c": 21, "low_c": 12, "condition": "partly_cloudy", "precipitation_probability": 28},
        {"date": "Mon", "high_c": 19, "low_c": 11, "condition": "rain", "precipitation_probability": 61},
        {"date": "Tue", "high_c": 17, "low_c": 10, "condition": "cloudy", "precipitation_probability": 35},
        {"date": "Wed", "high_c": 22, "low_c": 13, "condition": "sunny", "precipitation_probability": 10},
        {"date": "Thu", "high_c": 20, "low_c": 12, "condition": "drizzle", "precipitation_probability": 42},
    ]
    return weather_model.normalize_weather_payload(current, hourly, daily, STATUS_LIVE)


class MockWeatherProvider:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = 0
        self.active = False
        self.last_stage = "MOCK"
        self.last_error_code = None
        self.last_http_status = None

    def fetch(self, now_ms=0):
        self.calls += 1
        if self.fail:
            raise WeatherProviderError(SOCKET_FAIL, "mock provider offline")
        return mock_weather_payload(now_ms)


class WeatherService:
    def __init__(
        self,
        provider=None,
        cache_module=None,
        startup_delay_ms=None,
        refresh_ms=None,
        retry_ms=None,
        cache_write_min_ms=None,
    ):
        self.provider = provider or OpenMeteoProvider()
        self.cache = cache_module or persistent_cache
        self.startup_delay_ms = cfg.WEATHER_STARTUP_FETCH_DELAY_MS if startup_delay_ms is None else startup_delay_ms
        self.refresh_ms = cfg.CURRENT_WEATHER_REFRESH_MS if refresh_ms is None else refresh_ms
        self.retry_ms = cfg.CURRENT_WEATHER_RETRY_MS if retry_ms is None else retry_ms
        self.cache_write_min_ms = cfg.WEATHER_CACHE_WRITE_MIN_MS if cache_write_min_ms is None else cache_write_min_ms
        self.payload = None
        self.status = STATUS_OFFLINE
        self.fetch_state = FETCH_IDLE
        self.last_error = None
        self.started_at = None
        self.last_attempt_ms = None
        self.last_success_ms = None
        self.last_failure_ms = None
        self.last_cache_write_ms = None
        self.cache_available = False
        self.cache_full_forecast_available = False
        self.defer_cache_write_after_restore = False
        self.wifi_label = "WIFI WAIT"
        self.network_label = "IDLE"
        self.diagnostic_code = None
        self.last_fetch_error_type = None
        self.last_fetch_error_text = ""
        self.last_http_status = None

    def restore_cache(self):
        cached = self.cache.load_cache()
        if cached:
            cached["status"] = STATUS_CACHED
            cached["hourly_source"] = STATUS_CACHED if cached.get("hourly") else STATUS_OFFLINE
            cached["daily_source"] = STATUS_CACHED if cached.get("daily") else STATUS_OFFLINE
            self.payload = cached
            self.status = STATUS_CACHED
            self.fetch_state = FETCH_IDLE
            self.cache_available = True
            self.cache_full_forecast_available = bool(cached.get("hourly")) and bool(cached.get("daily"))
            self.defer_cache_write_after_restore = True
            return cached
        self.status = STATUS_OFFLINE
        return None

    def _mark_unavailable(self):
        if self.payload is not None:
            self.payload["status"] = STATUS_CACHED
            self.payload["hourly_source"] = STATUS_CACHED if self.payload.get("hourly") else STATUS_OFFLINE
            self.payload["daily_source"] = STATUS_CACHED if self.payload.get("daily") else STATUS_OFFLINE
            self.status = STATUS_CACHED
            return self.payload
        cached = self.restore_cache()
        if cached:
            return cached
        self.status = STATUS_OFFLINE
        return None

    def _set_wifi_state(self, wifi_state):
        if wifi_state is True:
            self.wifi_label = "WIFI OK"
            if self.diagnostic_code in (WIFI_WAIT, WIFI_FAIL):
                self.diagnostic_code = None
                self.last_fetch_error_type = None
            return True
        if wifi_state is None:
            self.wifi_label = "WIFI WAIT"
            self.fetch_state = FETCH_WAIT_WIFI
            self.diagnostic_code = WIFI_WAIT
            self.last_fetch_error_type = WIFI_WAIT
        else:
            self.wifi_label = "WIFI FAIL"
            self.fetch_state = FETCH_WAIT_WIFI
            self.diagnostic_code = WIFI_FAIL
            self.last_fetch_error_type = WIFI_FAIL
        return False

    def _set_failure_diagnostic(self, exc):
        code = _classify_fetch_exception(exc, self.provider.fetcher if hasattr(self.provider, "fetcher") else None)
        self.diagnostic_code = code
        self.last_fetch_error_type = code
        self.last_fetch_error_text = str(exc)[:48]
        self.last_http_status = getattr(exc, "status", None) or getattr(self.provider, "last_http_status", None)
        self.network_label = _error_label(code, self.last_http_status)

    def _save_cache_if_due(self, payload, now_ms):
        has_full_forecast = bool(payload.get("hourly")) and bool(payload.get("daily"))
        if not self.cache_available:
            wrote = self.cache.save_cache(payload)
            if wrote:
                self.last_cache_write_ms = now_ms
            self.cache_available = True
            if has_full_forecast:
                self.cache_full_forecast_available = True
            self.defer_cache_write_after_restore = False
            return wrote
        if has_full_forecast and not self.cache_full_forecast_available:
            wrote = self.cache.save_cache(payload)
            if wrote:
                self.last_cache_write_ms = now_ms
                self.cache_full_forecast_available = True
            self.defer_cache_write_after_restore = False
            return wrote
        if self.defer_cache_write_after_restore:
            self.last_cache_write_ms = now_ms
            self.defer_cache_write_after_restore = False
            return False
        if _timer_due(now_ms, self.last_cache_write_ms, self.cache_write_min_ms):
            wrote = self.cache.save_cache(payload)
            if wrote:
                self.last_cache_write_ms = now_ms
                if has_full_forecast:
                    self.cache_full_forecast_available = True
            return wrote
        return False

    def _accept_live(self, payload, now_ms):
        payload["status"] = STATUS_LIVE
        payload["hourly_source"] = STATUS_LIVE if payload.get("hourly") else STATUS_OFFLINE
        payload["daily_source"] = STATUS_LIVE if payload.get("daily") else STATUS_OFFLINE
        self.payload = payload
        self.status = STATUS_LIVE
        self.fetch_state = FETCH_LIVE
        self.last_error = None
        self.last_success_ms = now_ms
        self.last_failure_ms = None
        self.diagnostic_code = None
        self.last_fetch_error_type = None
        self.last_fetch_error_text = ""
        self.last_http_status = getattr(self.provider, "last_http_status", None)
        self.network_label = "LIVE"
        self._save_cache_if_due(payload, now_ms)
        return payload

    def refresh(self, now_ms=0):
        self.last_attempt_ms = now_ms
        try:
            payload = self.provider.fetch(now_ms)
            return self._accept_live(payload, now_ms)
        except FETCH_EXCEPTIONS as exc:
            self.last_error = exc
            self.last_failure_ms = now_ms
            self.fetch_state = FETCH_ERROR_RETRY
            self._set_failure_diagnostic(exc)
            return self._mark_unavailable()

    def _poll_async(self, now_ms):
        try:
            payload = self.provider.update(now_ms)
        except FETCH_EXCEPTIONS as exc:
            self.last_error = exc
            self.last_failure_ms = now_ms
            self.fetch_state = FETCH_ERROR_RETRY
            self._set_failure_diagnostic(exc)
            return self._mark_unavailable()
        self.network_label = getattr(self.provider, "last_stage", self.network_label)
        self.last_http_status = getattr(self.provider, "last_http_status", None)
        if payload is None:
            self.fetch_state = FETCH_FETCHING
            return None
        return self._accept_live(payload, now_ms)

    def _start_async_if_due(self, now_ms):
        if self.last_failure_ms is not None and self.last_attempt_ms == self.last_failure_ms:
            if not _timer_due(now_ms, self.last_failure_ms, self.retry_ms):
                return None
        elif self.last_success_ms is not None:
            if not _timer_due(now_ms, self.last_success_ms, self.refresh_ms):
                return None
        elif self.last_attempt_ms is not None and self.fetch_state != FETCH_ERROR_RETRY:
            return None
        self.last_attempt_ms = now_ms
        self.provider.start(now_ms)
        self.fetch_state = FETCH_FETCHING
        self.network_label = getattr(self.provider, "last_stage", "FETCH DNS")
        return self._poll_async(now_ms)

    def _refresh_sync_if_due(self, now_ms):
        if self.last_failure_ms is not None and self.last_attempt_ms == self.last_failure_ms:
            if not _timer_due(now_ms, self.last_failure_ms, self.retry_ms):
                return None
        elif self.last_success_ms is not None:
            if not _timer_due(now_ms, self.last_success_ms, self.refresh_ms):
                return None
        elif self.last_attempt_ms is not None and self.fetch_state != FETCH_ERROR_RETRY:
            return None
        return self.refresh(now_ms)

    def update(self, now_ms=0, wifi_connected=False, wifi_state=_WIFI_STATE_UNSET):
        if self.started_at is None:
            self.started_at = now_ms
        if getattr(self.provider, "active", False):
            return self._poll_async(now_ms)
        state = wifi_connected if wifi_state is _WIFI_STATE_UNSET else wifi_state
        if not self._set_wifi_state(state):
            self._mark_unavailable()
            return None
        if _ticks_diff(now_ms, self.started_at) < self.startup_delay_ms:
            self.network_label = "WAIT"
            return None
        if hasattr(self.provider, "start") and hasattr(self.provider, "update"):
            return self._start_async_if_due(now_ms)
        return self._refresh_sync_if_due(now_ms)

    def diagnostics(self):
        last = self.diagnostic_code or "NONE"
        return {
            "wifi": self.wifi_label,
            "network": self.network_label,
            "last_error": last,
            "status": self.status,
            "fetch_state": self.fetch_state,
            "http_status": self.last_http_status,
        }
