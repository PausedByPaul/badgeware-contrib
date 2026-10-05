# Copyright (C) 2026 Chris Parrish
# SPDX-License-Identifier: MIT
"""Track screens and edits. Browsing scenes leaves the clock and settings alone."""

from story import EVENTS, month_days, preview_date
from clock import shift, valid_local

# Selected existing chapters: winter, seasons, Christmas, and the quiet days after.
TOUR = (1, 2, 3, 4, 8, 10, 11, 17, 21, 22, 23, 24)


class Controller:
    def __init__(self, dt, offset=0, dst=False):
        usable = valid_local(dt, offset + (60 if dst else 0))
        self.mode = "live" if usable else "settings"
        self.values = list(dt[:5]) if usable else [2026, 1, 1, 12, 0]
        self.clock_original = tuple(self.values) if usable else None
        self.clock_error = "" if usable else "Check date and time"
        self.save_partial = False
        self.preferences_error = False
        self.index = 0
        self.year = self.values[0]
        self.dst = dst
        self.dst_choice = dst
        self.offset = offset
        self.offset_choice = offset
        self.setting_field = 0
        self.save_error = False
        self.hunt_step = 0
        self.hunt_miss = False

    def press(self, key, dt):
        if self.mode == "settings":
            if key in ("UP", "DOWN"):
                self.setting_field = (
                    self.setting_field + (1 if key == "DOWN" else -1)
                ) % 7
            elif key in ("A", "C"):
                self.clock_error = ""
                self.save_error = False
                step = 1 if key == "C" else -1
                if self.setting_field < 2:
                    before = self.offset_choice + (60 if self.dst_choice else 0)
                    if self.setting_field == 0:
                        self.offset_choice = max(
                            -720, min(840, self.offset_choice + step * 60)
                        )
                    else:
                        self.dst_choice = not self.dst_choice
                    after = self.offset_choice + (60 if self.dst_choice else 0)
                    self.values = list(
                        shift(tuple(self.values) + (0,), after - before)[:5]
                    )
                    if self.clock_original is not None:
                        self.clock_original = shift(
                            self.clock_original + (0,), after - before
                        )[:5]
                else:
                    field = self.setting_field - 2
                    offset = self.offset_choice + (60 if self.dst_choice else 0)
                    low = shift((2025, 1, 1, 0, 0, 0), offset)[0]
                    high = shift((2099, 12, 31, 23, 59, 59), offset)[0]
                    bounds = (
                        (low, high),
                        (1, 12),
                        (1, month_days(*self.values[:2])),
                        (0, 23),
                        (0, 59),
                    )
                    lo, hi = bounds[field]
                    value = self.values[field] + step
                    self.values[field] = (
                        max(lo, min(hi, value))
                        if field == 0
                        else lo + (value - lo) % (hi - lo + 1)
                    )
                    self.values[2] = min(self.values[2], month_days(*self.values[:2]))
            elif key == "B":
                if self.clock_dirty():
                    return tuple(self.values) + (0,)
            return None
        if self.mode == "tour":
            if key in ("A", "C"):
                self.advance_tour(-1 if key == "A" else 1)
            elif key in ("B", "UP", "DOWN"):
                self.mode = "live"
            return None
        if self.mode == "diary" and key == "C":
            self.mode = "tour"
            self.year = dt[0]
            self.index = 0
            return None
        if self.mode == "diary" and key in ("A", "SECRET"):
            return None
        if self.mode == "task" and key == "A":
            self.mode = "diary"
            return None
        if self.mode == "hunt":
            if key in ("UP", "DOWN"):
                self.mode = "live"
            elif key in ("A", "B", "C"):
                if key == ("A", "C", "B")[self.hunt_step]:
                    self.hunt_step += 1
                    self.hunt_miss = False
                    if self.hunt_step == 3:
                        self.mode = "secret"
                else:
                    self.hunt_miss = True
            return None
        if key == "SECRET" or (self.mode == "task" and key == "C"):
            self.mode = "hunt"
            self.hunt_step = 0
            self.hunt_miss = False
        elif key == "UP":
            self.mode = "settings"
            self.offset_choice = self.offset
            self.dst_choice = self.dst
            self.setting_field = 0
            usable = valid_local(dt, self.offset + (60 if self.dst else 0))
            self.values = list(dt[:5]) if usable else [2026, 1, 1, 12, 0]
            self.clock_original = tuple(self.values) if usable else None
            self.clock_error = ""
            self.save_error = False
        elif key == "DOWN":
            self.mode = {"task": "diary", "diary": "task"}.get(self.mode, "task")
        elif key == "B":
            self.mode = "live"
        elif key in ("A", "C"):
            if self.mode != "preview":
                self.year = dt[0]
                self.index = 0
                for i, event in enumerate(EVENTS):
                    if event[:3] <= (dt[1], dt[2], dt[3]):
                        self.index = i
            self.index = (self.index + (-1 if key == "A" else 1)) % len(EVENTS)
            self.mode = "preview"
        return None

    def clock_saved(self):
        self.clock_original = tuple(self.values)
        self.save_partial = False
        self.clock_error = ""
        self.mode = "live"
        self.setting_field = 0

    def clock_dirty(self):
        return tuple(self.values) != self.clock_original

    def advance_tour(self, step=1):
        self.index = max(0, self.index + step)
        if self.index >= len(TOUR):
            self.mode = "live"

    def display_date(self, dt):
        if self.mode == "tour":
            return preview_date(self.year, TOUR[self.index])
        return preview_date(self.year, self.index) if self.mode == "preview" else dt

    def expire(self):
        if self.mode not in ("live", "settings", "tour"):
            self.mode = "live"
            return True
        return False

    def view_key(self):
        if self.mode == "settings":
            return (
                self.mode,
                tuple(self.values),
                self.offset_choice,
                self.dst_choice,
                self.setting_field,
                self.clock_error,
                self.save_error,
                self.save_partial,
                self.preferences_error,
            )
        if self.mode in ("tour", "preview"):
            return self.mode, self.year, self.index
        if self.mode == "hunt":
            return self.mode, self.hunt_step, self.hunt_miss
        return (self.mode,)

    def recover_clock(self):
        if self.mode == "settings":
            return False
        self.press("UP", ())
        self.clock_error = "Check date and time"
        return True
