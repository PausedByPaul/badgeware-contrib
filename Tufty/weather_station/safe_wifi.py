"""Non-fatal, multi-network Wi-Fi state helper for BadgeWare apps."""

try:
    import network
except ImportError:  # pragma: no cover
    network = None

try:
    import secrets
except ImportError:  # pragma: no cover
    secrets = None

try:
    import sys
except ImportError:  # pragma: no cover
    sys = None

try:
    import time
except ImportError:  # pragma: no cover
    time = None


CONNECT_TIMEOUT_MS = 8000
RETRY_COOLDOWN_MS = 60000
WIFI_EXCEPTIONS = (AttributeError, NameError, OSError, RuntimeError, TypeError, ValueError)

STATE_IDLE = 0
STATE_CONNECTING = 1
STATE_CONNECTED = 2
STATE_FAILED = 3

_state = STATE_IDLE
_wlan = None
_started_at = None
_failed_at = None
_networks = None
_attempt_order = None
_attempt_index = 0
_current_network = None
_last_successful = None
_last_result = "IDLE"


def _set_result(value):
    global _last_result
    _last_result = value
    return value


def _load_secrets():
    global secrets
    if secrets is not None and (
        hasattr(secrets, "WIFI_NETWORKS")
        or hasattr(secrets, "WIFI_SSID")
        or hasattr(secrets, "WIFI_PASSWORD")
    ):
        return secrets
    if sys is None or not hasattr(sys, "path"):
        return secrets
    try:
        if "/" not in sys.path:
            sys.path.insert(0, "/")
    except WIFI_EXCEPTIONS:
        pass
    try:
        import secrets as loaded
        secrets = loaded
    except ImportError:
        pass
    return secrets


def _ticks_ms():
    if time is not None and hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    try:
        return badge.ticks
    except WIFI_EXCEPTIONS:
        return 0


def _ticks_diff(now, then):
    if time is not None and hasattr(time, "ticks_diff"):
        try:
            return time.ticks_diff(now, then)
        except WIFI_EXCEPTIONS:
            pass
    return int(now) - int(then)


def _valid_pair(entry):
    if not isinstance(entry, (tuple, list)) or len(entry) < 2:
        return None
    ssid = entry[0]
    psk = entry[1]
    if not isinstance(ssid, str) or not ssid:
        return None
    if psk is None:
        psk = ""
    if not isinstance(psk, str):
        return None
    return ssid, psk


def _dedupe(pairs):
    clean = []
    seen = set()
    for pair in pairs:
        if pair in seen:
            continue
        clean.append(pair)
        seen.add(pair)
    return clean


def configured_networks():
    """Return sanitized networks from /secrets.py without exposing them elsewhere."""
    source = _load_secrets()
    if source is None:
        return []

    networks = getattr(source, "WIFI_NETWORKS", None)
    if networks:
        pairs = []
        try:
            iterator = iter(networks)
        except TypeError:
            iterator = iter(())
        for entry in iterator:
            pair = _valid_pair(entry)
            if pair is not None:
                pairs.append(pair)
        pairs = _dedupe(pairs)
        if pairs:
            return pairs

    legacy = _valid_pair((
        getattr(source, "WIFI_SSID", ""),
        getattr(source, "WIFI_PASSWORD", ""),
    ))
    if legacy is None:
        return []
    return [legacy]


def _attempt_sequence(networks):
    if not networks:
        return []
    if _last_successful is None or _last_successful not in networks:
        return list(networks)
    ordered = [_last_successful]
    for pair in networks:
        if pair != _last_successful:
            ordered.append(pair)
    return ordered


def _disconnect_current(deactivate=False):
    try:
        if _wlan is not None:
            _wlan.disconnect()
            if deactivate:
                _wlan.active(False)
    except WIFI_EXCEPTIONS:
        pass


def _mark_failed(now):
    global _state, _failed_at, _started_at
    global _attempt_order, _attempt_index, _current_network
    _state = STATE_FAILED
    _failed_at = now
    _started_at = None
    _attempt_order = None
    _attempt_index = 0
    _current_network = None
    _disconnect_current(True)


def _hard_failure(wlan):
    try:
        return wlan.status() < 0
    except WIFI_EXCEPTIONS:
        return False


def _start_current(now):
    global _state, _wlan, _started_at
    if _current_network is None or network is None:
        _mark_failed(now)
        return False
    try:
        if _wlan is None:
            _wlan = network.WLAN(network.STA_IF)
        _wlan.active(True)
        if _wlan.isconnected():
            _state = STATE_CONNECTED
            return True
        _wlan.connect(_current_network[0], _current_network[1])
    except WIFI_EXCEPTIONS:
        return False
    _started_at = now
    _state = STATE_CONNECTING
    return None


def _start_next(now):
    global _attempt_index, _current_network
    if not _attempt_order or _attempt_index >= len(_attempt_order):
        _mark_failed(now)
        return False

    _disconnect_current(False)
    _current_network = _attempt_order[_attempt_index]
    _attempt_index += 1
    result = _start_current(now)
    if result is False:
        return _start_next(now)
    return result


def _start_attempts(now):
    global _networks, _attempt_order, _attempt_index, _current_network
    _networks = configured_networks()
    if not _networks or network is None:
        _mark_failed(now)
        return False
    _attempt_order = _attempt_sequence(_networks)
    _attempt_index = 0
    _current_network = None
    return _start_next(now)


def connect():
    """Advance Wi-Fi state without blocking.

    Returns:
      True  -> connected
      None  -> connection is still in progress
      False -> unavailable/failed/cooling down
    """
    global _state, _last_successful

    now = _ticks_ms()

    if _wlan is not None:
        try:
            if _wlan.isconnected():
                _state = STATE_CONNECTED
                if _current_network is not None:
                    _last_successful = _current_network
                _set_result("OK")
                return True
        except WIFI_EXCEPTIONS:
            pass

    if _state == STATE_CONNECTED:
        _disconnect_current(False)
        _state = STATE_IDLE

    if _state == STATE_FAILED:
        if _failed_at is not None and _ticks_diff(now, _failed_at) < RETRY_COOLDOWN_MS:
            _set_result("FAIL")
            return False
        _state = STATE_IDLE

    if _state == STATE_IDLE:
        result = _start_attempts(now)
        _set_result("OK" if result is True else "FAIL" if result is False else "TRY")
        return result

    if _state == STATE_CONNECTING:
        if _wlan is not None and _hard_failure(_wlan):
            result = _start_next(now)
            _set_result("OK" if result is True else "FAIL" if result is False else "TRY")
            return result
        if _started_at is None or _ticks_diff(now, _started_at) >= CONNECT_TIMEOUT_MS:
            result = _start_next(now)
            _set_result("OK" if result is True else "FAIL" if result is False else "TRY")
            return result
        _set_result("TRY")
        return None

    _set_result("FAIL")
    return False


def is_connected():
    try:
        return bool(_wlan is not None and _wlan.isconnected())
    except WIFI_EXCEPTIONS:
        return False


def status_label():
    if is_connected():
        return "OK"
    return _last_result


def disconnect():
    global _state, _wlan, _started_at, _failed_at
    global _attempt_order, _attempt_index, _current_network
    _disconnect_current(True)
    _state = STATE_IDLE
    _started_at = None
    _failed_at = None
    _attempt_order = None
    _attempt_index = 0
    _current_network = None


def _reset_for_tests():
    global _state, _wlan, _started_at, _failed_at, _networks
    global _attempt_order, _attempt_index, _current_network, _last_successful
    global _last_result
    _state = STATE_IDLE
    _wlan = None
    _started_at = None
    _failed_at = None
    _networks = None
    _attempt_order = None
    _attempt_index = 0
    _current_network = None
    _last_successful = None
    _last_result = "IDLE"
