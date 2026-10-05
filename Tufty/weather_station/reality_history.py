"""Persistent compact Reality Check history."""

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
except ImportError:
    import weather_config as cfg


PATH = "/weather_station_reality_history.json"
TEMP_PATH = "/weather_station_reality_history.tmp"
VERSION = 1
JSON_EXCEPTIONS = (OSError, TypeError, ValueError)


def _trim(items, limit):
    if limit <= 0:
        return []
    clean = []
    for item in list(items or []):
        if isinstance(item, str) and item.startswith("rc-"):
            clean.append(item)
    return clean[-limit:]


def sanitize(raw):
    if not isinstance(raw, dict):
        return {"global": [], "categories": {}}
    global_recent = _trim(raw.get("global", []), cfg.GLOBAL_REALITY_HISTORY)
    categories = {}
    raw_categories = raw.get("categories", {})
    if isinstance(raw_categories, dict):
        for category, ids in raw_categories.items():
            if isinstance(category, str):
                clean = _trim(ids, cfg.PER_CATEGORY_REALITY_HISTORY)
                if clean:
                    categories[category] = clean
    return {"global": global_recent, "categories": categories}


def load(path=PATH):
    if json is None:
        return {"global": [], "categories": {}}
    try:
        with open(path, "r") as handle:
            raw = json.load(handle)
    except JSON_EXCEPTIONS:
        return {"global": [], "categories": {}}
    if not isinstance(raw, dict) or raw.get("version") != VERSION:
        return {"global": [], "categories": {}}
    return sanitize(raw.get("history", {}))


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


def _write(payload, path, temp_path):
    if json is None:
        return False
    try:
        with open(temp_path, "w") as handle:
            json.dump(payload, handle)
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
            json.dump(payload, handle)
        return True
    except JSON_EXCEPTIONS:
        return False


def save(history, path=PATH, temp_path=TEMP_PATH):
    clean = sanitize(history)
    if clean == load(path):
        return False
    return _write({"version": VERSION, "history": clean}, path, temp_path)

