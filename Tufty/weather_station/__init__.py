"""KiloGramowy Weather Station for Pimoroni Tufty 2350 / BadgeWare."""

try:
    import os
    import sys
    import time
except ImportError:  # pragma: no cover
    os = None
    sys = None
    time = None


BADGEWARE_EXCEPTIONS = (AttributeError, NameError, OSError, RuntimeError, TypeError, ValueError)
CONVERSION_EXCEPTIONS = (TypeError, ValueError)


def _bootstrap_app_dir():
    if os is None or sys is None:
        return
    for candidate in ("/apps/weather_station", "/system/apps/weather_station"):
        try:
            os.stat(candidate)
        except OSError:
            continue
        try:
            os.chdir(candidate)
        except OSError:
            pass
        if candidate not in sys.path:
            sys.path.insert(0, candidate)
        return


_bootstrap_app_dir()

try:
    from . import weather_config as cfg
    from . import reality_history
    from . import reality_check
    from . import weather_provider
    from . import local_sensor
    from . import safe_wifi
except ImportError:
    import weather_config as cfg
    import reality_history
    import reality_check
    import weather_provider
    import local_sensor
    import safe_wifi


try:
    badge.mode(HIRES | VSYNC)
    screen.antialias = image.X4
    BADGEWARE_READY = True
except BADGEWARE_EXCEPTIONS:
    BADGEWARE_READY = False


W = cfg.SCREEN_WIDTH
H = cfg.SCREEN_HEIGHT

if BADGEWARE_READY:
    W = screen.width
    H = screen.height
    MONA = font.load("/system/assets/fonts/MonaSans-Medium.af")
    BG = color.rgb(5, 9, 13)
    PANEL = color.rgb(11, 18, 23)
    PANEL_2 = color.rgb(18, 29, 35)
    PANEL_3 = color.rgb(24, 39, 45)
    GRID = color.rgb(34, 56, 62)
    WHITE = color.rgb(235, 242, 235)
    DIM = color.rgb(118, 140, 137)
    MUTED = color.rgb(73, 92, 94)
    CYAN = color.rgb(80, 184, 218)
    GREEN = color.rgb(89, 192, 124)
    GOLD = color.rgb(218, 169, 84)
    COPPER = color.rgb(204, 112, 70)
    RED = color.rgb(214, 78, 80)
    BLUE = color.rgb(76, 128, 198)
else:
    MONA = None
    BG = PANEL = PANEL_2 = PANEL_3 = GRID = WHITE = DIM = MUTED = CYAN = GREEN = GOLD = COPPER = RED = BLUE = None


PAGES = ("NOW", "DETAILS", "HOURLY", "FORECAST", "LOCAL")
PAGE_NOW = 0
PAGE_LOCAL = len(PAGES) - 1

SCREEN_W = 320
SCREEN_H = 240
SAFE_X = 8
SAFE_RIGHT = 312
HEADER_Y = 6
HEADER_H = 24
CONTENT_Y = 34
CONTENT_BOTTOM = 207
FOOTER_Y = 214
FOOTER_H = 24
GRID_STEP = 40
ICON_MAIN_SIZE = 44
ICON_HOURLY_SIZE = 20
ICON_DAILY_SIZE = 22
COMMENTARY_BOX = (10, 108, 300, 50)
PAGE1_REALITY_BOX = (10, 148, 300, 54)
PAGE1_REALITY_LABEL_SIZE = 12
PAGE1_REALITY_COMMENT_SIZE = 12
PAGE1_REALITY_COMMENT_MIN_SIZE = 11
LOCAL_COMMENTARY_BOX = (10, 160, 300, 44)
DETAIL_CARD_W = 144
DETAIL_CARD_H = 36
DETAIL_LEFT_X = 10
DETAIL_RIGHT_X = 166
DETAIL_TOP_Y = 42
HOURLY_LEFT_X = 10
HOURLY_COL_W = 50
DAILY_ROW_X = 10
DAILY_ROW_W = 300
DAILY_ROW_H = 31

page_index = PAGE_NOW
last_input = None
pending_button = None
last_outdoor_attempt = None

weather_service = weather_provider.WeatherService()
outdoor_payload = weather_service.restore_cache()
local_reader = local_sensor.create_default_sensor()
local_reading = None

reality_engine = reality_check.RealityCheckEngine(reality_history.load())
current_reality = {
    "id": "",
    "text": "Awaiting enough reality to check.",
    "mood": "skeptic",
    "reaction": "skeptic",
    "lines": ("Awaiting enough reality", "to check."),
    "font_size": PAGE1_REALITY_COMMENT_SIZE,
}
current_reality_context = {}

auto_brightness_last_sample = None
auto_brightness_smoothed = cfg.AUTO_BRIGHTNESS_DEFAULT
auto_brightness_applied = cfg.AUTO_BRIGHTNESS_DEFAULT


def _clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value


def _brightness_bounds():
    low = float(getattr(cfg, "AUTO_BRIGHTNESS_MIN", 0.22))
    high = float(getattr(cfg, "AUTO_BRIGHTNESS_MAX", 1.0))
    if high < low:
        high = low
    return low, high


def brightness_for_light_level(raw):
    raw = int(raw)
    minimum, maximum = _brightness_bounds()
    curve = cfg.AUTO_BRIGHTNESS_CURVE
    if raw <= curve[0][0]:
        return _clamp(curve[0][1], minimum, maximum)

    previous_raw, previous_value = curve[0]
    for next_raw, next_value in curve[1:]:
        if raw <= next_raw:
            span = next_raw - previous_raw
            if span <= 0:
                value = next_value
            else:
                ratio = float(raw - previous_raw) / float(span)
                value = previous_value + (next_value - previous_value) * ratio
            return _clamp(value, minimum, maximum)
        previous_raw, previous_value = next_raw, next_value
    return _clamp(curve[-1][1], minimum, maximum)


def _ticks_ms():
    if time is not None and hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    try:
        return badge.ticks
    except BADGEWARE_EXCEPTIONS:
        pass
    return local_sensor.ticks_ms()


def _timer_due(now, then, interval):
    if then is None:
        return True
    diff = _ticks_diff(now, then)
    return diff is not None and diff >= interval


def update_auto_brightness(now):
    global auto_brightness_last_sample, auto_brightness_smoothed, auto_brightness_applied
    if not getattr(cfg, "AUTO_BRIGHTNESS_ENABLED", True):
        return False
    if not _timer_due(now, auto_brightness_last_sample, cfg.AUTO_BRIGHTNESS_SAMPLE_MS):
        return False
    auto_brightness_last_sample = now
    try:
        raw = badge.light_level()
    except BADGEWARE_EXCEPTIONS:
        return False
    target = brightness_for_light_level(raw)
    auto_brightness_smoothed = (
        auto_brightness_smoothed * (1.0 - cfg.AUTO_BRIGHTNESS_SMOOTHING)
        + target * cfg.AUTO_BRIGHTNESS_SMOOTHING
    )
    auto_brightness_smoothed = _clamp(auto_brightness_smoothed, *_brightness_bounds())
    if abs(auto_brightness_smoothed - auto_brightness_applied) < cfg.AUTO_BRIGHTNESS_HYSTERESIS:
        return False
    try:
        display.backlight(auto_brightness_smoothed)
    except BADGEWARE_EXCEPTIONS:
        return False
    auto_brightness_applied = auto_brightness_smoothed
    return True


def navigation_step(index, button):
    if button == "C":
        return PAGE_NOW
    if button == "A" and index > PAGE_NOW:
        return index - 1
    if button == "B" and index < PAGE_LOCAL:
        return index + 1
    return index


def capture_button_press():
    try:
        if badge.pressed(BUTTON_C):
            return "C"
        if badge.pressed(BUTTON_A):
            return "A"
        if badge.pressed(BUTTON_B):
            return "B"
    except BADGEWARE_EXCEPTIONS:
        return None
    return None


def handle_navigation(now):
    global page_index, last_input, pending_button
    pressed = capture_button_press()
    if pressed is not None:
        pending_button = pressed

    if pending_button is None:
        return False
    if last_input is not None and _ticks_diff(now, last_input) <= cfg.INPUT_DELAY_MS:
        return False

    page_index = navigation_step(page_index, pending_button)
    pending_button = None
    last_input = now
    return True


def _ticks_diff(now, then):
    if then is None:
        return None
    return local_sensor.ticks_diff(now, then)


def _format(value, suffix="", decimals=0, missing="--"):
    if value is None:
        return missing
    try:
        if decimals:
            return ("{0:0." + str(decimals) + "f}{1}").format(value, suffix)
        return "{}{}".format(int(round(value)), suffix)
    except CONVERSION_EXCEPTIONS:
        return "{}{}".format(value, suffix)


def _format_temp(value, decimals=0, missing="--"):
    if value is None:
        return missing
    if decimals:
        return ("{0:0." + str(decimals) + "f}°").format(value)
    return "{}°".format(int(round(value)))


def _format_pressure(value, missing="--"):
    pressure = reality_check.normalize_pressure_hpa(value)
    if pressure is None:
        return missing
    return "{} hPa".format(int(round(pressure)))


def _comparison_line(context):
    temp_delta = context.get("temperature_delta_c")
    humidity_delta = context.get("humidity_delta_percent")
    parts = []
    temp_phrase = None
    if temp_delta is not None:
        if abs(temp_delta) <= reality_check.TEMP_DELTA_SIMILAR_C:
            temp_phrase = "TEMPERATURES ALMOST MATCH"
        else:
            sign = "+" if temp_delta > 0 else ""
            direction = "WARMER" if temp_delta > 0 else "COOLER"
            temp_phrase = "HERE IS {}{:.1f}°C {}".format(sign, temp_delta, direction)
        parts.append(temp_phrase)
    if humidity_delta is not None:
        if abs(humidity_delta) <= reality_check.HUMIDITY_DELTA_SIMILAR:
            parts.append("RH ALMOST MATCHES")
        else:
            direction = "DRIER" if humidity_delta < 0 else "MORE HUMID"
            parts.append("{}% {}".format(abs(humidity_delta), direction))
    return " · ".join(parts) if parts else "COMPARISON WAITING"


def _delta_line(context):
    return _comparison_line(context)


def _condition_label(condition):
    return str(condition or "unknown").replace("_", " ").upper()


def _condition_accent(condition):
    name = str(condition or "").lower()
    if "snow" in name or "freez" in name:
        return WHITE
    if "thunder" in name or "storm" in name:
        return GOLD
    if "rain" in name or "drizzle" in name:
        return CYAN
    if "sun" in name or "clear" in name:
        return GOLD
    if "hot" in name:
        return COPPER
    if "wind" in name:
        return CYAN
    return BLUE


def _current():
    if not outdoor_payload:
        return {}
    return outdoor_payload.get("current") or {}


def _status():
    if not outdoor_payload:
        return weather_service.status or "OFFLINE"
    return outdoor_payload.get("status", weather_service.status or "OFFLINE")


def _section_source(section):
    if not outdoor_payload:
        return "OFFLINE"
    items = outdoor_payload.get(section) or []
    if not items:
        return "OFFLINE"
    key = section + "_source"
    return outdoor_payload.get(key) or outdoor_payload.get("status") or "OFFLINE"


def _use_ui_font():
    if not BADGEWARE_READY:
        return
    screen.font = MONA
    try:
        screen.antialias = image.X4
    except BADGEWARE_EXCEPTIONS:
        pass


def _measure_text(text, size=12):
    if not BADGEWARE_READY:
        return (0, 0)
    _use_ui_font()
    return screen.measure_text(str(text), int(size))


def _text(text, x, y, size=12, pen=None):
    if not BADGEWARE_READY:
        return
    _use_ui_font()
    screen.pen = pen or WHITE
    screen.text(str(text), int(x), int(y), int(size))


def _fit_text(text, max_chars):
    text = str(text or "")
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return text[: max_chars - 3] + "..."


def _hour_label(value):
    text = str(value or "")
    marker = text.find("T")
    if marker >= 0 and marker + 3 < len(text):
        return text[marker + 1:marker + 3] + ":00"
    if len(text) >= 5 and text[2] == ":":
        return text[:2] + ":00"
    return "--"


def _clamp_pct(value):
    try:
        numeric = float(value)
    except CONVERSION_EXCEPTIONS:
        return None
    if numeric < 0:
        return 0
    if numeric > 100:
        return 100
    return numeric


def _is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _weekday_label(date_text):
    try:
        text = str(date_text)
        year = int(text[0:4])
        month = int(text[5:7])
        day = int(text[8:10])
    except CONVERSION_EXCEPTIONS:
        return "--"
    if month < 1 or month > 12 or day < 1:
        return "--"
    days = (31, 29 if _is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    if day > days[month - 1]:
        return "--"
    if month < 3:
        month += 12
        year -= 1
    k = year % 100
    j = year // 100
    h = (day + ((13 * (month + 1)) // 5) + k + (k // 4) + (j // 4) + (5 * j)) % 7
    return ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")[(h + 5) % 7]


def _label(text, x, y, pen=None):
    _text(text, x, y, 9, pen or DIM)


def _right(text, right, y, size=12, pen=None):
    if not BADGEWARE_READY:
        return
    width = int(_measure_text(str(text), int(size))[0])
    _text(text, right - width, y, size, pen)


def _clear():
    if not BADGEWARE_READY:
        return
    screen.pen = BG
    try:
        screen.clear()
    except BADGEWARE_EXCEPTIONS:
        screen.rectangle(0, 0, W, H)


def _line(x1, y1, x2, y2, pen=None):
    if not BADGEWARE_READY:
        return
    screen.pen = pen or GRID
    screen.line(int(x1), int(y1), int(x2), int(y2))


def _rect(x, y, w, h, pen=None):
    if not BADGEWARE_READY:
        return
    screen.pen = pen or PANEL
    screen.rectangle(int(x), int(y), int(w), int(h))


def _circle(x, y, r, pen=None):
    if not BADGEWARE_READY:
        return
    screen.pen = pen or WHITE
    screen.circle(int(x), int(y), int(r))


def _draw_bg(show_grid=True):
    _clear()
    _rect(0, 0, W, 32, PANEL)
    if not show_grid:
        return
    for x in range(SAFE_X, SAFE_RIGHT + 1, GRID_STEP):
        _line(x, 162, x, CONTENT_BOTTOM, MUTED)
    for y in range(162, CONTENT_BOTTOM + 1, GRID_STEP):
        _line(SAFE_X, y, SAFE_RIGHT, y, MUTED)


def _status_chip(status, right=SAFE_RIGHT, y=7, size=9):
    if not status:
        return
    text = str(status)
    width = int(_measure_text(text, size)[0]) + 10
    x = right - width
    _rect(x, y - 1, width, size + 8, PANEL_3)
    _line(x, y - 1, x + width, y - 1, _status_pen(text))
    _text(text, x + 5, y + 2, size, _status_pen(text))


def _header(title, status, subtitle=None):
    _draw_bg()
    _text(title, 10, 7, 13, WHITE)
    if subtitle:
        _text(subtitle, 10, 22, 8, DIM)
    if status:
        _status_chip(status, SAFE_RIGHT, 7, 9)
    _line(SAFE_X, 32, SAFE_RIGHT, 32, GRID)


def _footer(show_page=True):
    _rect(0, FOOTER_Y, W, FOOTER_H, PANEL)
    _line(SAFE_X, FOOTER_Y, SAFE_RIGHT, FOOTER_Y, GRID)
    page = "{}/{}".format(page_index + 1, len(PAGES))
    a_pen = DIM if page_index > PAGE_NOW else GRID
    b_pen = DIM if page_index < PAGE_LOCAL else GRID
    _text("A BACK", 10, 222, 9, a_pen)
    _text("B NEXT", 116, 222, 9, b_pen)
    _text("C HOME", 220, 222, 9, DIM)
    if show_page:
        _right(page, SAFE_RIGHT, 222, 9, DIM)


def _panel(x, y, w, h, pen=None):
    _rect(x, y, w, h, pen or PANEL)
    _line(x, y, x + w, y, GRID)
    _line(x, y + h, x + w, y + h, MUTED)


def _metric(label, value, x, y, _w=56):
    _label(label, x, y)
    _text(value, x, y + 13, 14, WHITE)


def _local_header(title, reading):
    _draw_bg(False)
    _text(title, 10, 7, 14, WHITE)
    status = reading.get("status", {})
    _sensor_status("BME", status.get("bme", "N/A"), 196, 10)
    _sensor_status("LTR", status.get("ltr", "N/A"), 237, 10)
    _sensor_status("IMU", status.get("motion", "N/A"), 278, 10)
    _line(SAFE_X, 32, SAFE_RIGHT, 32, GRID)


def _sensor_status(label, value, x, y):
    ok = value == "OK"
    unavailable = value in ("N/A", None)
    pen = GREEN if ok else DIM if unavailable else RED
    _rect(x - 3, y - 3, 35, 15, PANEL_3)
    _text(label, x, y, 8, DIM)
    _text("●", x + 23, y - 2, 10, pen)


def _local_metric_card(label, value, x, y, w, h, pen=None):
    _panel(x, y, w, h, PANEL_2)
    _line(x + 1, y + 4, x + 1, y + h - 5, pen or CYAN)
    _text(label, x + 9, y + 8, 10, DIM)
    _text(value, x + 9, y + 29, 22, pen or WHITE)


def _detail_card(label, value, helper, x, y):
    _panel(x, y, DETAIL_CARD_W, DETAIL_CARD_H, PANEL_2)
    _line(x + 1, y + 4, x + 1, y + DETAIL_CARD_H - 5, CYAN)
    _label(label, x + 8, y + 5)
    _text(value, x + 8, y + 18, 14, WHITE)
    if helper:
        _right(helper, x + DETAIL_CARD_W - 7, y + 20, 8, DIM)


def _health(label, state, x):
    pen = GREEN if state == "OK" else RED if state == "ERR" else DIM
    _text(label, x, 8, 9, DIM)
    _circle(x + 27, 13, 3, pen)


def _draw_mood_marker(mood, x, y, size=14):
    mood = mood or "skeptic"
    cx = x + size // 2
    cy = y + size // 2
    if mood == "devil":
        _line(cx, y + 2, x + 3, y + 7, COPPER)
        _line(cx, y + 2, x + size - 3, y + 7, COPPER)
        _circle(cx, cy + 2, size // 3, GOLD)
        _line(cx - 3, cy + 1, cx - 1, cy + 1, BG)
        _line(cx + 1, cy + 1, cx + 3, cy + 1, BG)
    elif mood == "laugh":
        _circle(cx, cy, size // 3, GOLD)
        _line(cx - 4, cy - 2, cx - 2, cy - 1, BG)
        _line(cx + 2, cy - 1, cx + 4, cy - 2, BG)
        _line(cx - 4, cy + 3, cx + 4, cy + 3, BG)
    elif mood in ("fire", "thermal"):
        _line(cx, y + 2, x + 3, y + size - 3, COPPER)
        _line(cx, y + 2, x + size - 3, y + size - 3, GOLD)
        _line(x + 3, y + size - 3, x + size - 3, y + size - 3, COPPER)
    elif mood in ("water", "rain"):
        _line(cx, y + 2, x + 4, y + size - 4, CYAN)
        _line(cx, y + 2, x + size - 4, y + size - 4, CYAN)
        _line(x + 4, y + size - 4, x + size - 4, y + size - 4, CYAN)
    elif mood == "sun":
        _circle(cx, cy, size // 4, GOLD)
        _line(cx, y + 1, cx, y + 4, GOLD)
        _line(cx, y + size - 4, cx, y + size - 1, GOLD)
        _line(x + 1, cy, x + 4, cy, GOLD)
        _line(x + size - 4, cy, x + size - 1, cy, GOLD)
    elif mood == "snow":
        _line(cx, y + 2, cx, y + size - 2, WHITE)
        _line(x + 2, cy, x + size - 2, cy, WHITE)
        _line(x + 4, y + 4, x + size - 4, y + size - 4, WHITE)
    elif mood == "coffee":
        _rect(x + 2, y + 4, size - 7, size - 5, GOLD)
        _line(x + size - 5, y + 6, x + size - 2, y + 9, GOLD)
        _line(x + 4, y + 1, x + 4, y + 3, DIM)
    elif mood == "cool":
        _line(x + 2, cy, x + size - 2, cy, CYAN)
        _rect(x + 3, cy - 4, 4, 4, CYAN)
        _rect(x + size - 7, cy - 4, 4, 4, CYAN)
    elif mood == "eyes":
        _circle(x + 5, cy, 3, WHITE)
        _circle(x + size - 5, cy, 3, WHITE)
    elif mood == "wind":
        _line(x + 2, y + 5, x + size - 2, y + 5, CYAN)
        _line(x + 5, y + 9, x + size - 5, y + 9, CYAN)
    elif mood == "tropical":
        _line(cx, y + 3, cx, y + size - 2, GREEN)
        _line(cx, y + 5, x + 3, y + 9, GREEN)
        _line(cx, y + 5, x + size - 3, y + 9, GREEN)
        _circle(cx, y + size - 3, 3, GOLD)
    elif mood == "facepalm":
        _circle(cx, cy, size // 3, DIM)
        _line(cx - 4, cy - 2, cx + 4, cy - 2, BG)
        _line(cx - 3, cy + 3, cx + 3, cy + 1, BG)
        _line(x + 3, y + 4, x + size - 3, y + 8, GOLD)
    else:
        _circle(cx, cy, size // 3, DIM)
        _line(cx - 3, cy - 2, cx - 1, cy - 2, DIM)
        _line(cx + 1, cy - 2, cx + 3, cy - 2, DIM)


def _draw_reaction_marker(reaction, x, y, size=14):
    reaction = reaction or "skeptic"
    if reaction == "fire":
        cx = x + size // 2
        _circle(cx, y + size - 5, max(3, size // 4), COPPER)
        _line(cx, y + 1, x + 4, y + size - 7, GOLD)
        _line(cx, y + 1, x + size - 4, y + size - 7, COPPER)
        _circle(cx, y + size - 7, max(2, size // 7), GOLD)
        return
    if reaction in ("plant", "umbrella", "droplet", "ice", "side_eye", "home", "cloud", "warning", "moon", "thermometer"):
        cx = x + size // 2
        cy = y + size // 2
        if reaction == "plant":
            _line(cx, y + 3, cx, y + size - 2, GREEN)
            _line(cx, y + 5, x + 3, y + 9, GREEN)
            _line(cx, y + 5, x + size - 3, y + 9, GREEN)
            _circle(cx, y + size - 3, 3, GOLD)
        elif reaction == "umbrella":
            _line(x + 2, cy, x + size - 2, cy, CYAN)
            _line(x + 2, cy, cx, y + 3, CYAN)
            _line(cx, y + 3, x + size - 2, cy, CYAN)
            _line(cx, cy, cx, y + size - 2, DIM)
        elif reaction == "droplet":
            _line(cx, y + 2, x + 4, y + size - 4, CYAN)
            _line(cx, y + 2, x + size - 4, y + size - 4, CYAN)
            _line(x + 4, y + size - 4, x + size - 4, y + size - 4, CYAN)
        elif reaction == "ice":
            _line(cx, y + 2, cx, y + size - 2, WHITE)
            _line(x + 2, cy, x + size - 2, cy, WHITE)
            _line(x + 4, y + 4, x + size - 4, y + size - 4, WHITE)
        elif reaction == "side_eye":
            _circle(cx, cy, size // 3, DIM)
            _line(cx - 4, cy - 2, cx - 2, cy - 2, WHITE)
            _line(cx + 1, cy - 2, cx + 5, cy - 2, WHITE)
        elif reaction == "home":
            _line(x + 2, cy, cx, y + 3, GREEN)
            _line(cx, y + 3, x + size - 2, cy, GREEN)
            _rect(x + 4, cy, size - 8, size // 2, GREEN)
        elif reaction == "cloud":
            _cloud(cx, cy, float(size) / 44.0, BLUE)
        elif reaction == "warning":
            _line(cx, y + 2, x + 3, y + size - 3, GOLD)
            _line(cx, y + 2, x + size - 3, y + size - 3, GOLD)
            _line(x + 3, y + size - 3, x + size - 3, y + size - 3, GOLD)
        elif reaction == "moon":
            _circle(cx - 1, cy, size // 3, GOLD)
            _circle(cx + 4, cy - 2, size // 3, BG)
        elif reaction == "thermometer":
            _line(cx, y + 2, cx, y + size - 4, COPPER)
            _circle(cx, y + size - 4, 3, GOLD)
        return
    _draw_mood_marker(reaction, x, y, size)


def _comment_box(label, text, box):
    x, y, w, h = box
    _panel(x, y, w, h, PANEL_2)
    _label(label, x + 7, y + 6, GOLD)
    lines, size = _fit_commentary_lines(text, w - 14, 2, 13, 10)
    y_text = y + 21
    for line in lines:
        _text(line, x + 7, y_text, size, WHITE)
        y_text += size + 2


def _reality_box(record):
    x, y, w, h = COMMENTARY_BOX
    _panel(x, y, w, h, PANEL_2)
    _label("REALITY CHECK", x + 7, y + 6, GOLD)
    marker_size = 14
    text_w = w - 24 - marker_size
    lines, size = _fit_commentary_lines(record.get("text", ""), text_w, 2, 12, 9)
    y_text = y + 22
    for line in lines:
        _text(line, x + 7, y_text, size, WHITE)
        y_text += size + 2
    _draw_reaction_marker(record.get("reaction") or record.get("mood"), x + w - marker_size - 8, y + h - marker_size - 8, marker_size)


def _status_pen(status):
    return GREEN if status == "LIVE" else GOLD if status == "CACHED" else RED


def _connection_diagnostics():
    try:
        return weather_service.diagnostics()
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError):
        return {"wifi": "WIFI: ?", "network": "NET: ?", "last_error": "MODEL_FAIL"}


def _draw_connection_diagnostics(y=32):
    diag = _connection_diagnostics()
    last = diag.get("last_error", "NONE")
    if last in (None, "NONE", weather_provider.WIFI_WAIT):
        return
    network = str(diag.get("network", "") or "")
    if "TIMEOUT" in network or last == weather_provider.TIMEOUT:
        label = "TIMEOUT"
    elif network.startswith("ERR HTTP"):
        label = network.replace("ERR ", "")
    elif "DNS" in network or "CONNECT" in network or "TLS" in network or last in (
        weather_provider.DNS_FAIL,
        weather_provider.CONNECT_FAIL,
        weather_provider.SOCKET_FAIL,
        weather_provider.TLS_FAIL,
        weather_provider.WIFI_FAIL,
    ):
        label = "NETWORK ERROR"
    else:
        label = "FETCH ERROR"
    _text(_fit_text(label, 18), 10, y, 8, RED)


def _page1_header():
    _clear()
    _rect(0, 0, W, 35, PANEL)
    _text("WEATHER STATION", 10, 7, 13, WHITE)
    _text("{} · OUTSIDE ↔ HERE".format(cfg.WEATHER_LOCATION_NAME), 10, 22, 9, DIM)
    status = _status()
    _status_chip(status, SAFE_RIGHT, 8, 8)
    _line(SAFE_X, 35, SAFE_RIGHT, 35, GRID)


def _page1_reality_area(record):
    x, y, w, h = PAGE1_REALITY_BOX
    _panel(x, y, w, h, PANEL_2)
    _line(x + 1, y + 6, x + 1, y + h - 6, GOLD)
    _text("REALITY CHECK", x + 8, y + 5, PAGE1_REALITY_LABEL_SIZE, GOLD)
    marker_size = 15
    lines = record.get("lines") or (record.get("text", ""),)
    size = int(record.get("font_size", PAGE1_REALITY_COMMENT_MIN_SIZE))
    y_text = y + 24
    for line in tuple(lines)[:2]:
        _text(line, x + 8, y_text, size, WHITE)
        y_text += size + 2
    _draw_reaction_marker(record.get("reaction") or record.get("mood"), x + w - marker_size - 8, y + h - marker_size - 9, marker_size)


def _words(text):
    return str(text or "").split()


def _wrap_lines(text, max_width, size, max_lines):
    lines = []
    current = ""
    for word in _words(text):
        candidate = word if not current else current + " " + word
        if _measure_text(candidate, size)[0] <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines


def _fit_commentary_lines(text, max_width, max_lines=2, preferred_size=13, min_size=10):
    raw = str(text or "")
    for size in range(int(preferred_size), int(min_size) - 1, -1):
        lines = _wrap_lines(raw, max_width, size, max_lines)
        joined = " ".join(lines)
        if joined == " ".join(_words(raw)) and all(_measure_text(line, size)[0] <= max_width for line in lines):
            return lines, size
    size = int(min_size)
    lines = _wrap_lines(raw, max_width, size, max_lines)
    if not lines:
        return [""], size
    last = lines[-1]
    while last and _measure_text(last + "...", size)[0] > max_width:
        last = last[:-1]
    lines[-1] = last + "..." if last else "..."
    return lines, size


def _fit_commentary_complete(text, max_width, max_lines=2, preferred_size=13, min_size=10):
    raw_words = " ".join(_words(text))
    for size in range(int(preferred_size), int(min_size) - 1, -1):
        lines = _wrap_lines(text, max_width, size, max_lines)
        if " ".join(lines) == raw_words and all(_measure_text(line, size)[0] <= max_width for line in lines):
            return tuple(lines), size
    return None


def _page1_comment_fit(record):
    x, _y, w, _h = PAGE1_REALITY_BOX
    marker_size = 15
    text_w = w - marker_size - 23
    fitted = _fit_commentary_complete(
        record.get("text", ""),
        text_w,
        2,
        PAGE1_REALITY_COMMENT_SIZE,
        PAGE1_REALITY_COMMENT_MIN_SIZE,
    )
    if fitted is None:
        return None
    lines, size = fitted
    return {"lines": lines, "font_size": size}


def _cloud(cx, cy, scale, pen):
    _circle(cx - 8 * scale, cy + 1 * scale, 7 * scale, pen)
    _circle(cx, cy - 3 * scale, 9 * scale, pen)
    _circle(cx + 10 * scale, cy + 2 * scale, 7 * scale, pen)
    _rect(cx - 17 * scale, cy + 3 * scale, 34 * scale, 8 * scale, pen)


def _draw_icon(condition, x, y, size):
    condition = str(condition or "cloudy").lower()
    cx = x + size // 2
    cy = y + size // 2
    scale = float(size) / 44.0

    if "fog" in condition:
        for offset in (-0.25, 0, 0.25):
            yy = cy + int(size * offset)
            _line(x + 4, yy, x + size - 4, yy, DIM)
        return
    if "wind" in condition:
        _line(x + 4, cy - int(size * 0.22), x + size - 6, cy - int(size * 0.22), CYAN)
        _line(x + 8, cy, x + size - 3, cy, CYAN)
        _line(x + 4, cy + int(size * 0.22), x + size - 8, cy + int(size * 0.22), CYAN)
        return
    if "clear" in condition and "day" not in condition:
        _circle(cx - 2, cy, size // 3, GOLD)
        _circle(cx + 5, cy - 3, size // 3, BG)
        return
    if "sun" in condition or "clear" in condition:
        _circle(cx, cy, size // 4, GOLD)
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0), (1, 1), (-1, -1)):
            inner = int(size * 0.30)
            outer = int(size * 0.42)
            _line(cx + dx * inner, cy + dy * inner, cx + dx * outer, cy + dy * outer, GOLD)
        return

    if "partly" in condition or "mostly" in condition:
        _circle(x + int(size * 0.33), y + int(size * 0.33), int(size * 0.18), GOLD)
        _cloud(cx + int(size * 0.07), cy + int(size * 0.07), scale, BLUE)
    else:
        _cloud(cx, cy, scale, BLUE)

    if "drizzle" in condition:
        drops = (-8, 0, 8)
    elif "heavy" in condition:
        drops = (-12, -4, 4, 12)
    elif "rain" in condition:
        drops = (-9, 0, 9)
    else:
        drops = ()
    for offset in drops:
        _line(cx + int(offset * scale), y + size - int(11 * scale), cx + int((offset - 4) * scale), y + size - int(4 * scale), CYAN)
    if "thunder" in condition or "storm" in condition:
        _line(cx + int(4 * scale), y + size - int(18 * scale), cx - int(2 * scale), y + size - int(6 * scale), GOLD)
        _line(cx - int(2 * scale), y + size - int(6 * scale), cx + int(7 * scale), y + size - int(10 * scale), GOLD)
        _line(cx + int(7 * scale), y + size - int(10 * scale), cx + int(1 * scale), y + size - int(1 * scale), GOLD)
    if "snow" in condition:
        for offset in (-8, 7):
            ox = int(offset * scale)
            arm = max(2, int(3 * scale))
            _line(cx + ox - arm, y + size - int(7 * scale), cx + ox + arm, y + size - int(7 * scale), WHITE)
            _line(cx + ox, y + size - int(10 * scale), cx + ox, y + size - int(4 * scale), WHITE)


def draw_now():
    current = _current()
    local = local_reading or {}
    context = current_reality_context or reality_check.derive_context(current, local)
    _page1_header()

    _panel(10, 42, 144, 82, PANEL_2)
    _panel(166, 42, 144, 82, PANEL_2)

    _line(12, 48, 12, 118, CYAN)
    _label("OUTSIDE", 19, 47, CYAN)
    _text(_format_temp(current.get("temperature_c")), 18, 58, 29, WHITE)
    _draw_icon(current.get("condition"), 119, 55, 27)
    _text(_condition_label(current.get("condition"))[:15], 18, 91, 8, _condition_accent(current.get("condition")))
    _text("RH " + _format(current.get("humidity_percent"), "%"), 18, 103, 10, DIM)
    _text(_format_pressure(current.get("pressure_hpa")), 77, 103, 10, DIM)
    _text("FEELS " + _format_temp(current.get("feels_like_c")), 18, 115, 9, DIM)

    _line(168, 48, 168, 118, GREEN)
    _label("HERE", 175, 47, GREEN)
    here_temp = _format_temp(local.get("temperature_c"), 1)
    _text(here_temp, 174, 58, 29, WHITE)
    _text("RH " + _format(local.get("humidity_percent"), "%"), 175, 98, 11, DIM)
    _text(_format_pressure(local.get("pressure_hpa")), 175, 113, 11, DIM)

    _panel(10, 127, 300, 18, PANEL)
    comparison = _fit_text(_comparison_line(context), 39)
    _text(comparison, 17, 132, 10, GOLD)
    _page1_reality_area(current_reality)
    _text("designed by KiloGramowy", 10, 204, 8, DIM)
    _right("1/5", SAFE_RIGHT, 204, 8, DIM)
    _footer(False)


def draw_details():
    current = _current()
    _header("DETAILS", _status(), "{} / OUTDOOR".format(cfg.WEATHER_LOCATION_NAME))
    _draw_connection_diagnostics(32)
    cards = (
        ("FEELS LIKE", _format(current.get("feels_like_c"), "°"), "", DETAIL_LEFT_X, DETAIL_TOP_Y),
        ("WIND", _format(current.get("wind_speed")), "km/h", DETAIL_RIGHT_X, DETAIL_TOP_Y),
        ("HUMIDITY", _format(current.get("humidity_percent"), "%"), "", DETAIL_LEFT_X, DETAIL_TOP_Y + 42),
        ("GUST", _format(current.get("wind_gust_kmh")), "km/h", DETAIL_RIGHT_X, DETAIL_TOP_Y + 42),
        ("PRESSURE", _format_pressure(current.get("pressure_hpa")), "", DETAIL_LEFT_X, DETAIL_TOP_Y + 84),
        ("PRECIP", _format(current.get("precipitation_amount"), "", 1), "mm", DETAIL_RIGHT_X, DETAIL_TOP_Y + 84),
        ("CLOUD", _format(current.get("cloud_pct"), "%"), "", DETAIL_LEFT_X, DETAIL_TOP_Y + 126),
        ("DIRECTION", current.get("wind_direction", "--"), _format(current.get("wind_direction_deg"), "°"), DETAIL_RIGHT_X, DETAIL_TOP_Y + 126),
    )
    for label, value, helper, x, y in cards:
        _detail_card(label, value, helper, x, y)
    _footer()


def draw_hourly():
    _header("HOURLY", _section_source("hourly"), "NEXT 6 HOURS")
    source = outdoor_payload or {}
    items = (source.get("hourly") or [])[:6]
    temps = [item.get("temperature_c") for item in items if item.get("temperature_c") is not None]
    low = min(temps) if temps else None
    high = max(temps) if temps else None
    graph_top = 112
    graph_bottom = 151
    graph_pad = 5
    graph_range = (graph_bottom - graph_top) - (graph_pad * 2)
    points = []
    if not items:
        _text("NO HOURLY FORECAST", 72, 92, 14, DIM)
    else:
        _line(18, graph_top - 1, SAFE_RIGHT - 18, graph_top - 1, MUTED)
        _line(18, graph_bottom + 1, SAFE_RIGHT - 18, graph_bottom + 1, MUTED)
    for index in range(6):
        item = items[index] if index < len(items) else {}
        x = HOURLY_LEFT_X + index * HOURLY_COL_W
        cx = x + HOURLY_COL_W // 2
        _text(_hour_label(item.get("time")), x + 7, 46, 9, GOLD)
        _draw_icon(item.get("condition"), cx - ICON_HOURLY_SIZE // 2, 68, ICON_HOURLY_SIZE)
        _text(_format(item.get("temperature_c"), "°"), x + 10, 96, 14, WHITE)
        temp = item.get("temperature_c")
        if temp is not None and low is not None and high is not None:
            if high == low:
                py = (graph_top + graph_bottom) // 2
            else:
                py = int(graph_bottom - graph_pad - ((temp - low) * graph_range / (high - low)))
            points.append((cx, py))
        else:
            points.append(None)
        rain = _clamp_pct(item.get("precipitation_probability_pct", item.get("precipitation_probability")))
        _text(_format(rain, "%"), x + 9, 170, 10, CYAN)
        if rain is not None:
            bar_h = int(min(24, max(2, rain / 100.0 * 24)))
            _rect(cx - 5, 200 - bar_h, 10, bar_h, CYAN)
        _line(cx - 7, 200, cx + 7, 200, MUTED)
        if index:
            _line(x, 43, x, 204, GRID)
    for i in range(1, len(points)):
        if points[i - 1] is not None and points[i] is not None:
            _line(points[i - 1][0], points[i - 1][1], points[i][0], points[i][1], GOLD)
    _footer()


def draw_forecast():
    _header("FORECAST", _section_source("daily"), "5 DAY OUTLOOK")
    source = outdoor_payload or {}
    items = (source.get("daily") or [])[:5]
    lows = [item.get("temperature_min_c", item.get("low_c")) for item in items if item.get("temperature_min_c", item.get("low_c")) is not None]
    highs = [item.get("temperature_max_c", item.get("high_c")) for item in items if item.get("temperature_max_c", item.get("high_c")) is not None]
    range_low = min(lows) if lows else None
    range_high = max(highs) if highs else None
    if not items:
        _text("NO 5-DAY FORECAST", 72, 104, 14, DIM)
    for index in range(5):
        item = items[index] if index < len(items) else {}
        y = 42 + index * DAILY_ROW_H
        _rect(10, y + 1, 300, DAILY_ROW_H - 4, PANEL_2 if index % 2 == 0 else PANEL)
        _line(DAILY_ROW_X, y + DAILY_ROW_H - 2, DAILY_ROW_X + DAILY_ROW_W, y + DAILY_ROW_H - 2, GRID)
        day_label = "TODAY" if index == 0 and item.get("date") else _weekday_label(item.get("date"))
        _text(day_label, 12, y + 8, 11, WHITE)
        _draw_icon(item.get("condition"), 61, y + 5, ICON_DAILY_SIZE)
        low = item.get("temperature_min_c", item.get("low_c"))
        high = item.get("temperature_max_c", item.get("high_c"))
        _text(_format(low, "°"), 104, y + 8, 11, DIM)
        _text(_format(high, "°"), 232, y + 8, 11, WHITE)
        bar_x = 145
        bar_w = 74
        _line(bar_x, y + 15, bar_x + bar_w, y + 15, GRID)
        if low is not None and high is not None and range_low is not None and range_high is not None:
            if range_high == range_low:
                sx = bar_x + (bar_w // 2) - 3
                ex = sx + 6
            else:
                sx = int(bar_x + (low - range_low) * bar_w / (range_high - range_low))
                ex = int(bar_x + (high - range_low) * bar_w / (range_high - range_low))
            sx = max(bar_x, min(bar_x + bar_w, sx))
            ex = max(bar_x, min(bar_x + bar_w, ex))
            if ex <= sx:
                ex = min(bar_x + bar_w, sx + 4)
            _line(sx, y + 15, ex, y + 15, GOLD)
        rain = _clamp_pct(item.get("precipitation_probability_max_pct", item.get("precipitation_probability")))
        _right(_format(rain, "%"), SAFE_RIGHT, y + 8, 10, CYAN)
    _footer()


def draw_local():
    reading = local_reading or {}
    _local_header("LOCAL SENSOR", reading)
    if reading.get("temperature_c") is None and reading.get("lux") is None:
        _text("SENSOR NOT FOUND", 58, 58, 22, RED)
        _text("BME N/A   LTR N/A   IMU N/A", 44, 88, 13, DIM)
        _text("No local values available.", 10, 151, 14, WHITE)
        _footer()
        return

    light = _format(reading.get("lux"), " lux")
    _local_metric_card("TEMPERATURE", _format(reading.get("temperature_c"), "", 1) + "°C", 12, 44, 142, 66, COPPER)
    _local_metric_card("HUMIDITY", _format(reading.get("humidity_percent"), "%"), 166, 44, 142, 66, CYAN)
    _local_metric_card("PRESSURE", _format_pressure(reading.get("pressure_hpa")), 12, 126, 142, 66, GOLD)
    _local_metric_card("LIGHT", light, 166, 126, 142, 66, CYAN if reading.get("lux") is not None else WHITE)
    _footer()


def draw():
    if page_index == 0:
        draw_now()
    elif page_index == 1:
        draw_details()
    elif page_index == 2:
        draw_hourly()
    elif page_index == 3:
        draw_forecast()
    else:
        draw_local()


def refresh_outdoor(now):
    global outdoor_payload
    wifi_state = safe_wifi.connect()
    payload = weather_service.update(now, wifi_state is True, wifi_state=wifi_state)
    if payload is not None:
        outdoor_payload = payload
        return True
    if weather_service.payload is not None:
        outdoor_payload = weather_service.payload
    return False


def refresh_commentary(now):
    global current_reality, current_reality_context
    line, context, _ranked, changed = reality_engine.select(_current(), local_reading, now, fit_checker=_page1_comment_fit)
    current_reality = line
    current_reality_context = context
    if changed:
        reality_history.save(reality_engine.export_history())
    return changed


def update():
    global local_reading
    now = _ticks_ms()
    update_auto_brightness(now)
    refresh_outdoor(now)

    next_local = local_reader.update(now)
    if next_local is not None:
        local_reading = next_local

    refresh_commentary(now)
    handle_navigation(now)
    draw()


def on_exit():
    pass


if BADGEWARE_READY:
    try:
        display.backlight(auto_brightness_applied)
    except BADGEWARE_EXCEPTIONS:
        pass
    run(update)
