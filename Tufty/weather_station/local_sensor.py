"""Pimoroni Multi-Sensor Stick support with graceful partial failures."""

try:
    import time
except ImportError:  # pragma: no cover
    time = None

try:
    from . import weather_config as cfg
except ImportError:
    import weather_config as cfg


BME280_ADDRESS = 0x76
LTR559_ADDRESS = 0x23
LSM6DS3_ADDRESS = 0x6A
LTR559_PROXIMITY_INDEX = 0
LTR559_LUX_INDEX = 6
LUX_CHANGE_EPS = 0.1
CONVERSION_EXCEPTIONS = (TypeError, ValueError)
HARDWARE_EXCEPTIONS = (AttributeError, ImportError, OSError, RuntimeError, TypeError, ValueError)


def lux_changed(previous, current, epsilon=LUX_CHANGE_EPS):
    if current is None:
        return False
    if previous is None:
        return True
    try:
        return abs(float(current) - float(previous)) >= epsilon
    except CONVERSION_EXCEPTIONS:
        return current != previous


def normalize_pressure_hpa(value):
    if value is None:
        return None
    pressure = float(value)
    if pressure > 2000:
        pressure = pressure / 100.0
    return pressure


def ticks_ms():
    if time is not None and hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    try:
        return badge.ticks
    except HARDWARE_EXCEPTIONS:
        return 0


def ticks_diff(now, then):
    if then is None:
        return None
    if time is not None and hasattr(time, "ticks_diff"):
        try:
            return time.ticks_diff(now, then)
        except HARDWARE_EXCEPTIONS:
            pass
    return int(now) - int(then)


def _ticks_ms():
    return ticks_ms()


def _ticks_diff(now, then):
    return ticks_diff(now, then)


def _timer_due(now, then, interval):
    if then is None:
        return True
    diff = _ticks_diff(now, then)
    return diff is not None and diff >= interval


class LocalSensor:
    def __init__(
        self,
        i2c_factory=None,
        bme_cls=None,
        ltr_cls=None,
        lsm_cls=None,
        lsm_mode=None,
        read_interval_ms=None,
        ltr_interval_ms=None,
        ltr_use_dedicated_i2c=None,
        temp_offset_c=None,
    ):
        self.i2c_factory = i2c_factory
        self.bme_cls = bme_cls
        self.ltr_cls = ltr_cls
        self.lsm_cls = lsm_cls
        self.lsm_mode = lsm_mode
        self.read_interval_ms = cfg.LOCAL_SENSOR_READ_MS if read_interval_ms is None else int(read_interval_ms)
        self.ltr_interval_ms = cfg.LTR_SENSOR_READ_MS if ltr_interval_ms is None else int(ltr_interval_ms)
        if ltr_use_dedicated_i2c is None:
            ltr_use_dedicated_i2c = getattr(cfg, "LTR_USE_DEDICATED_I2C", False)
        self.ltr_use_dedicated_i2c = bool(ltr_use_dedicated_i2c)
        self.temp_offset_c = cfg.LOCAL_TEMP_OFFSET_C if temp_offset_c is None else float(temp_offset_c)
        self.i2c = None
        self.bme_i2c = None
        self.imu_i2c = None
        self.ltr_i2c = None
        self.bme = None
        self.ltr = None
        self.lsm = None
        self.motion_available = False
        self.status = {"bme": "N/A", "ltr": "N/A", "motion": "N/A"}
        self.last_environment_read_ms = None
        self.last_ltr_read_ms = None
        self.last_read_ms = self.last_environment_read_ms
        self.last_valid = None
        self.last_ltr_raw_lux = None
        self.last_ltr_raw_proximity = None
        self.last_error = None
        self.detected_addresses = []

    def _replace_last_valid(self, reading):
        self.last_valid = reading

    def _resolve_i2c(self):
        if self.i2c_factory is not None:
            return self.i2c_factory()
        from machine import I2C
        return I2C()

    def _resolve_classes(self):
        if self.bme_cls is None:
            try:
                from breakout_bme280 import BreakoutBME280
                self.bme_cls = BreakoutBME280
            except ImportError:
                self.bme_cls = False
        if self.ltr_cls is None:
            try:
                from breakout_ltr559 import BreakoutLTR559
                self.ltr_cls = BreakoutLTR559
            except ImportError:
                self.ltr_cls = False
        if self.lsm_cls is None:
            try:
                from lsm6ds3 import LSM6DS3, NORMAL_MODE_104HZ
                self.lsm_cls = LSM6DS3
                self.lsm_mode = NORMAL_MODE_104HZ
            except ImportError:
                self.lsm_cls = False

    def init(self):
        self._resolve_classes()

        if self.bme_cls:
            try:
                self.bme_i2c = self._resolve_i2c()
                if self.i2c is None:
                    self.i2c = self.bme_i2c
                if not self.detected_addresses:
                    try:
                        self.detected_addresses = list(self.bme_i2c.scan())
                    except HARDWARE_EXCEPTIONS:
                        self.detected_addresses = []
                self.bme = self.bme_cls(self.bme_i2c)
                self.status["bme"] = "OK"
            except HARDWARE_EXCEPTIONS as exc:
                self.bme_i2c = None
                self.bme = None
                self.status["bme"] = "N/A"
                self.last_error = exc

        if self.lsm_cls:
            try:
                self.imu_i2c = self._resolve_i2c()
                if self.i2c is None:
                    self.i2c = self.imu_i2c
                if self.lsm_mode is None:
                    self.lsm = self.lsm_cls(self.imu_i2c)
                else:
                    self.lsm = self.lsm_cls(self.imu_i2c, mode=self.lsm_mode)
                self.motion_available = True
                self.status["motion"] = "OK"
            except HARDWARE_EXCEPTIONS as exc:
                self.imu_i2c = None
                self.lsm = None
                self.motion_available = False
                self.status["motion"] = "N/A"
                self.last_error = exc

        if self.ltr_cls:
            try:
                self.ltr_i2c = self._resolve_i2c()
                if self.i2c is None:
                    self.i2c = self.ltr_i2c
                self.ltr = self.ltr_cls(self.ltr_i2c)
                self.status["ltr"] = "OK"
            except HARDWARE_EXCEPTIONS as exc:
                self.ltr_i2c = None
                self.ltr = None
                self.status["ltr"] = "N/A"
                self.last_error = exc

        return self.bme is not None or self.ltr is not None or self.lsm is not None

    def _read_bme(self, reading):
        if self.bme is None:
            return
        values = self.bme.read()
        raw_temp = values[0]
        reading["temperature_raw_c"] = raw_temp
        reading["temperature_c"] = raw_temp + self.temp_offset_c
        reading["humidity_percent"] = values[2]
        reading["pressure_hpa"] = normalize_pressure_hpa(values[1])

    def _ltr_value(self, values, attr_name, fallback_index):
        key = getattr(self.ltr_cls, attr_name, fallback_index)
        try:
            return values[key]
        except (AttributeError, IndexError, KeyError, TypeError):
            return None

    def _read_ltr(self, reading, _now_ms=None):
        if self.ltr is None:
            return False
        values = self.ltr.get_reading()
        if values is None:
            return False

        proximity = self._ltr_value(values, "PROXIMITY", LTR559_PROXIMITY_INDEX)
        lux = self._ltr_value(values, "LUX", LTR559_LUX_INDEX)

        if lux is not None:
            reading["lux"] = lux
            self.last_ltr_raw_lux = lux

        if proximity is not None:
            reading["proximity"] = proximity
            self.last_ltr_raw_proximity = proximity

        self.status["ltr"] = "OK"
        return True

    def _read_lsm(self, reading):
        reading["motion_available"] = bool(self.motion_available)
        if self.lsm is None:
            return
        try:
            values = self.lsm.get_readings()
            reading["motion_sample"] = True
            reading["_motion_axes"] = values
        except HARDWARE_EXCEPTIONS:
            reading["motion_sample"] = False

    def _empty_reading(self, now_ms):
        return {
            "temperature_c": None,
            "humidity_percent": None,
            "pressure_hpa": None,
            "lux": None,
            "proximity": None,
            "motion_available": bool(self.motion_available),
            "status": dict(self.status),
            "timestamp": now_ms,
        }

    def _retain_last_measurements(self, reading):
        if self.last_valid is None:
            return
        for field in (
            "temperature_raw_c",
            "temperature_c",
            "humidity_percent",
            "pressure_hpa",
            "lux",
            "proximity",
            "motion_sample",
            "_motion_axes",
        ):
            if reading.get(field) is None and self.last_valid.get(field) is not None:
                reading[field] = self.last_valid.get(field)

    def read_now(self, now_ms=None):
        now_ms = _ticks_ms() if now_ms is None else int(now_ms)
        reading = self._empty_reading(now_ms)
        self.last_environment_read_ms = now_ms
        self.last_ltr_read_ms = now_ms
        self.last_read_ms = now_ms
        any_success = False
        try:
            self._read_bme(reading)
            if reading.get("temperature_c") is not None:
                any_success = True
        except HARDWARE_EXCEPTIONS as exc:
            self.status["bme"] = "ERR"
            reading["status"] = dict(self.status)
            self.last_error = exc
        try:
            if self._read_ltr(reading, now_ms):
                any_success = True
        except HARDWARE_EXCEPTIONS as exc:
            self.status["ltr"] = "ERR"
            reading["status"] = dict(self.status)
            self.last_error = exc
        try:
            self._read_lsm(reading)
        except HARDWARE_EXCEPTIONS as exc:
            self.status["motion"] = "N/A"
            reading["motion_available"] = False
            reading["status"] = dict(self.status)
            self.last_error = exc

        reading["status"] = dict(self.status)
        if any_success:
            self._retain_last_measurements(reading)
            self._replace_last_valid(reading)
        return self.last_valid if self.last_valid is not None else reading

    def update(self, now_ms=None):
        now_ms = _ticks_ms() if now_ms is None else int(now_ms)
        environment_due = _timer_due(now_ms, self.last_environment_read_ms, self.read_interval_ms)
        ltr_due = _timer_due(now_ms, self.last_ltr_read_ms, self.ltr_interval_ms)
        if not environment_due and not ltr_due:
            return self.last_valid

        reading = self._empty_reading(now_ms)
        self._retain_last_measurements(reading)
        any_success = self.last_valid is not None

        if environment_due:
            self.last_environment_read_ms = now_ms
            self.last_read_ms = now_ms
            try:
                self._read_bme(reading)
                if reading.get("temperature_c") is not None:
                    any_success = True
            except HARDWARE_EXCEPTIONS as exc:
                self.status["bme"] = "ERR"
                self.last_error = exc
            try:
                self._read_lsm(reading)
            except HARDWARE_EXCEPTIONS as exc:
                self.status["motion"] = "N/A"
                reading["motion_available"] = False
                self.last_error = exc

        if ltr_due:
            self.last_ltr_read_ms = now_ms
            try:
                if self._read_ltr(reading, now_ms):
                    any_success = True
            except HARDWARE_EXCEPTIONS as exc:
                self.status["ltr"] = "ERR"
                self.last_error = exc

        reading["status"] = dict(self.status)
        if any_success or environment_due or ltr_due:
            self._replace_last_valid(reading)
        return self.last_valid


def create_default_sensor():
    sensor = LocalSensor()
    sensor.init()
    return sensor
