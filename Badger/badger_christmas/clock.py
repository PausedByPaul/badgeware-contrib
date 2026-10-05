# Copyright (C) 2026 Chris Parrish
# SPDX-License-Identifier: MIT
"""UTC conversion and the saved timezone/DST settings."""

from story import month_days, ordinal, valid


def shift(dt, minutes):
    if len(dt) < 6:
        return dt
    y, m, d, h, mi, s = dt[:6]
    if not (
        1 <= m <= 12 and 1 <= d <= month_days(y, m) and 0 <= h < 24 and 0 <= mi < 60
    ):
        return dt
    total = h * 60 + mi + minutes
    while total < 0:
        total += 1440
        d -= 1
        if d < 1:
            m -= 1
            if m < 1:
                y -= 1
                m = 12
            d = month_days(y, m)
    while total >= 1440:
        total -= 1440
        d += 1
        if d > month_days(y, m):
            d = 1
            m += 1
            if m > 12:
                y += 1
                m = 1
    return (y, m, d, total // 60, total % 60, s, (ordinal(y, m, d) - 1) % 7)


def valid_local(dt, offset):
    """Check the UTC date before accepting a local date."""
    try:
        return valid(shift(dt, -offset))
    except (TypeError, ValueError, IndexError):
        return False


def label(minutes):
    return "UTC%s%02d:%02d" % (
        "-" if minutes < 0 else "+",
        abs(minutes) // 60,
        abs(minutes) % 60,
    )


class LocalClock:
    def __init__(self, hardware, offset=0):
        self.hardware = hardware
        self.offset = offset

    def datetime(self, value=None):
        if value is None:
            return shift(self.hardware.datetime(), self.offset)
        utc = shift(value, -self.offset)
        if not valid(utc):
            raise ValueError("Outside UTC date range")
        return self.hardware.datetime(utc)

    def rtc_to_localtime(self):
        return self.hardware.rtc_to_localtime()


def read_clock(rtc):
    """A failed RTC read must not prevent the recovery settings from opening."""
    try:
        return rtc.datetime()
    except (OSError, ValueError, TypeError, IndexError):
        return ()


import os

PATH = "/badger_christmas.cfg"

status = "missing"


def read(path):
    global status
    try:
        with open(path, "rb") as f:
            data = f.read(3)
    except OSError as error:
        status = "missing" if error.args and error.args[0] == 2 else "unreadable"
        return 0, False
    status = "corrupt"
    if len(data) != 2 or data[0] > 26 or data[1] not in (0, 1):
        return 0, False
    status = "ok"
    return (data[0] - 12) * 60, bool(data[1])


def load(path=PATH):
    return read(path)


def save(offset, dst, path=PATH):
    if offset % 60 or not -720 <= offset <= 840:
        raise ValueError("Invalid timezone")
    if not isinstance(dst, bool):
        raise ValueError("Invalid DST flag")
    previous = read(path)
    if previous == (offset, dst) and status in ("ok", "missing"):
        return False
    data = bytes((offset // 60 + 12, int(dst)))
    temporary = path + ".tmp"
    try:
        with open(temporary, "wb") as f:
            f.write(data)
        os.rename(temporary, path)
    except OSError:
        try:
            os.remove(temporary)
        except OSError:
            pass
        raise
    return True
