"""Persistent last-known outdoor weather cache."""

try:
    import json
except ImportError:  # pragma: no cover
    json = None

try:
    import os
except ImportError:  # pragma: no cover
    os = None

try:
    from . import weather_config as cfg
    from . import weather_model
except ImportError:
    import weather_config as cfg
    import weather_model


VERSION = 3
SCHEMA = "open_meteo_forecast_v2"
SUPPORTED_VERSIONS = (1, 2, 3)
JSON_EXCEPTIONS = (OSError, TypeError, ValueError)


def _empty():
    return {"version": VERSION}


def sanitize_payload(payload):
    if not isinstance(payload, dict):
        return None
    if weather_model.contains_secret_key(payload):
        return None
    current = weather_model.normalize_current(payload.get("current") or {})
    hourly = weather_model.normalize_hourly(payload.get("hourly") or [])
    daily = weather_model.normalize_daily(payload.get("daily") or [])
    status = payload.get("status") or "LIVE"
    location = payload.get("location") or current.get("location") or cfg.WEATHER_LOCATION_NAME
    if not current and not hourly and not daily:
        return None
    section_source = status if status in ("LIVE", "CACHED") else "OFFLINE"
    return {
        "current": current,
        "hourly": hourly,
        "daily": daily,
        "status": status,
        "hourly_source": payload.get("hourly_source") or (section_source if hourly else "OFFLINE"),
        "daily_source": payload.get("daily_source") or (section_source if daily else "OFFLINE"),
        "location": location,
    }


def load_cache(path=cfg.WEATHER_CACHE_PATH):
    if json is None:
        return None
    try:
        with open(path, "r") as handle:
            raw = json.load(handle)
    except JSON_EXCEPTIONS:
        return None
    if not isinstance(raw, dict) or raw.get("version") not in SUPPORTED_VERSIONS:
        return None
    payload = sanitize_payload(raw.get("weather"))
    if payload is None:
        return None
    if raw.get("location") and not payload.get("location"):
        payload["location"] = raw.get("location")
    payload["status"] = "CACHED"
    payload["hourly_source"] = "CACHED" if payload.get("hourly") else "OFFLINE"
    payload["daily_source"] = "CACHED" if payload.get("daily") else "OFFLINE"
    return payload


def _exists(path):
    if os is not None and hasattr(os, "stat"):
        try:
            os.stat(path)
            return True
        except OSError:
            return False
    try:
        with open(path, "r"):
            return True
    except OSError:
        return False


def _rename(src, dst):
    if os is not None and hasattr(os, "rename"):
        os.rename(src, dst)
    else:
        raise OSError("rename unavailable")


def _remove(path):
    if os is not None and hasattr(os, "remove"):
        os.remove(path)
    else:
        raise OSError("remove unavailable")


def _write_cache(cache, path, temp_path):
    if json is None:
        return False
    try:
        with open(temp_path, "w") as handle:
            json.dump(cache, handle)
    except JSON_EXCEPTIONS:
        return False
    try:
        _rename(temp_path, path)
        return True
    except OSError:
        pass
    try:
        if _exists(path):
            _remove(path)
        _rename(temp_path, path)
        return True
    except OSError:
        pass
    try:
        with open(path, "w") as handle:
            json.dump(cache, handle)
        return True
    except JSON_EXCEPTIONS:
        return False


def save_cache(
    payload,
    path=cfg.WEATHER_CACHE_PATH,
    temp_path=cfg.WEATHER_CACHE_TEMP_PATH,
):
    clean = sanitize_payload(payload)
    if clean is None:
        return False
    existing = load_cache(path)
    comparable_existing = None
    if existing is not None:
        comparable_existing = {
            "current": existing.get("current", {}),
            "hourly": existing.get("hourly", []),
            "daily": existing.get("daily", []),
            "status": "LIVE",
            "hourly_source": "LIVE" if existing.get("hourly") else "OFFLINE",
            "daily_source": "LIVE" if existing.get("daily") else "OFFLINE",
            "location": existing.get("location"),
        }
    comparable_clean = {
        "current": clean.get("current", {}),
        "hourly": clean.get("hourly", []),
        "daily": clean.get("daily", []),
        "status": "LIVE",
        "hourly_source": "LIVE" if clean.get("hourly") else "OFFLINE",
        "daily_source": "LIVE" if clean.get("daily") else "OFFLINE",
        "location": clean.get("location"),
    }
    if comparable_existing == comparable_clean:
        return False
    return _write_cache(
        {
            "version": VERSION,
            "schema": SCHEMA,
            "location": clean.get("location"),
            "weather": clean,
        },
        path,
        temp_path,
    )
