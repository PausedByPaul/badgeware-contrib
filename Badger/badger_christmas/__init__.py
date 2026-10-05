# Copyright (C) 2026 Chris Parrish
# SPDX-License-Identifier: MIT
# Version 1.0
"""Badger Christmas for stock Badger 2350 Badgeware 3.x.
Open from the badge menu. Badgeware supplies the screen, clock, and buttons.
"""

import time
import gc
import powman
from story import next_wake, ordinal, remaining, scene_id
from controller import Controller, TOUR
from view import Renderer
import view as layout
import clock as preferences
from clock import LocalClock, valid_local, read_clock


class Buttons:
    def __init__(self, ticks_diff):
        self.diff = ticks_diff
        self.previous = 0
        self.pending = 0
        self.chord_start = None
        self.latched = False

    def feed(self, held, now):
        pressed = held & ~self.previous
        self.previous = held
        for bit, key in ((2, "B"), (8, "UP"), (16, "DOWN")):
            if pressed & bit:
                self.pending = 0
                self.chord_start = None
                self.latched = bool(held & 5)
                return key
        if held & 5 == 5:
            self.pending = 0
            if self.chord_start is None:
                self.chord_start = now
            if not self.latched and self.diff(now, self.chord_start) >= 1000:
                self.latched = True
                return "SECRET"
            return None
        if self.chord_start is not None:
            self.chord_start = None
            self.latched = True
        if self.latched:
            if not held & 5:
                self.latched = False
            return None
        if self.pending and not held & self.pending:
            key = "A" if self.pending == 1 else "C"
            # A release and the other button's press can share one poll.
            self.pending = pressed & 5
            return key
        if pressed & 1:
            self.pending = 1
        elif pressed & 4:
            self.pending = 4
        return None


class Refresh:
    def __init__(self, badge, display, buttons, held_mask, clock):
        self.badge = badge
        self.display = display
        self.buttons = buttons
        self.held_mask = held_mask
        self.clock = clock
        self.queue = []

    def poll(self):
        self.badge.poll()
        held = self.held_mask()
        key = self.buttons.feed(held, self.clock.ticks_ms())
        if key:
            if len(self.queue) < 8:
                self.queue.append(key)
        return held

    def next_key(self):
        return self.queue.pop(0) if self.queue else None

    def update(self):
        self.badge.update()
        started = self.clock.ticks_ms()
        while True:
            self.poll()
            if not self.display.busy():
                break
            if self.clock.ticks_diff(self.clock.ticks_ms(), started) >= 15000:
                raise OSError("Display timeout")
            self.clock.sleep_ms(10)


badge.mode(FULL_UPDATE | NON_BLOCKING)
badge.caselights(0)
clock_fault = False
try:
    rtc.clear_alarm()
except OSError:
    clock_fault = True
renderer = None
controls = (
    (BUTTON_A, "A"),
    (BUTTON_B, "B"),
    (BUTTON_C, "C"),
    (BUTTON_UP, "UP"),
    (BUTTON_DOWN, "DOWN"),
)
base_offset, dst_enabled = preferences.load()
rtc = LocalClock(rtc, base_offset + (60 if dst_enabled else 0))
state = Controller(() if clock_fault else read_clock(rtc), base_offset, dst_enabled)
if preferences.status in ("corrupt", "unreadable"):
    if state.mode != "settings":
        state.press("UP", read_clock(rtc))
    state.preferences_error = True
buttons = Buttons(time.ticks_diff)
last_signature = None
tour_shown_at = 0
TOUR_INTERVAL_MS = 8000
SETTINGS_IDLE_MS = 300000


def on_exit():
    if renderer is not None:
        renderer.close()


def signature(dt):
    return (dt[0], dt[1], dt[2], remaining(dt), scene_id(dt))


def draw_page():
    global last_signature, tour_shown_at
    while True:
        dt = read_clock(rtc)
        if not valid_local(dt, rtc.offset):
            state.recover_clock()
        screen.pen = color.white
        screen.clear()
        if state.mode == "tour":
            layout.tour_page(renderer, state.display_date(dt), state.index, len(TOUR))
        elif state.mode == "diary":
            layout.diary_page(renderer, dt)
        elif state.mode == "task":
            layout.task_page(renderer, dt)
        elif state.mode == "settings":
            layout.settings_page(
                renderer,
                state.save_error,
                state.offset_choice,
                state.setting_field,
                state.dst_choice,
                state.values,
                state.clock_error,
                state.save_partial,
            )
        elif state.mode == "hunt":
            layout.hunt_page(renderer, state.hunt_step, state.hunt_miss)
        elif state.mode == "secret":
            layout.secret_page(renderer, dt)
        else:
            layout.scene(renderer, state.display_date(dt))
        refresh.update()
        if state.mode == "tour":
            tour_shown_at = time.ticks_ms()
        if state.mode != "live":
            return
        last_signature = signature(dt)
        # If the date or scene changed during the refresh, redraw before sleeping.
        current = read_clock(rtc)
        if valid_local(current, rtc.offset) and last_signature == signature(current):
            return


def show():
    global renderer
    try:
        if renderer is None:
            renderer = Renderer(screen, "art.bin")
        draw_page()
    except (OSError, ValueError, KeyError):
        if renderer is not None:
            renderer.close()
        renderer = None
        # Firmware lettering remains usable even when art.bin is missing.
        screen.pen = color.white
        screen.clear()
        screen.pen = color.black
        screen.font = font.sins
        screen.text("OSWIN: DISPLAY ERROR", 10, 25)
        screen.text("Reinstall the app files.", 10, 60)
        screen.text("HOME: menu", 10, 95)
        screen.text("Press RESET to retry.", 10, 125)
        if not display.busy():
            try:
                refresh.update()
            except OSError:
                pass
        powman.sleep()


def settings_timeout():
    # Drafts are never saved by inactivity. Keep unresolved errors visible.
    dt = read_clock(rtc)
    if (
        not state.save_partial
        and not state.preferences_error
        and valid_local(dt, rtc.offset)
    ):
        state.mode = "live"
        show()
        sleep_until_change()
    else:
        state.mode = "live"
        state.press("UP", dt)
        if state.save_partial:
            state.clock_original = None
        state.clock_error = "Check time and zone"
        # Deep sleep restarts the app: do not leave a stale "B: Retry" promise.
        screen.pen = color.white
        screen.clear()
        screen.pen = color.black
        screen.font = font.sins
        screen.text("SETTINGS PAUSED", 10, 25)
        screen.text("Unsaved edits canceled.", 10, 60)
        screen.text("Check time and zone.", 10, 95)
        screen.text("UP: settings after wake.", 10, 125)
        refresh.update()
        if refresh.queue or held_mask():
            show()
            return
        if renderer is not None:
            renderer.close()
        powman.sleep()


def sleep_until_change():
    dt = read_clock(rtc)
    if not valid_local(dt, rtc.offset):
        state.recover_clock()
        show()
        return
    if signature(dt) != last_signature:
        show()
        dt = read_clock(rtc)
    if state.mode != "live" or not valid_local(dt, rtc.offset):
        return
    # A button may have been pressed during the refresh. Check before sleeping.
    previous = buttons.previous
    held = refresh.poll()
    key = refresh.next_key()
    if key:
        if press(key):
            show()
    if key or held or refresh.queue or previous != held:
        return
    seconds = next_wake(dt)
    if renderer is not None:
        renderer.close()
    # badge.sleep(seconds) uses timer-only dormant sleep on Badgeware 3.x.
    # powman.sleep also arms the front-button interrupt and RTC wake sources.
    powman.sleep(seconds)


def press(key):
    before = state.view_key()
    handle_press(key)
    return before != state.view_key()


def handle_press(key):
    current = read_clock(rtc)
    if not valid_local(current, rtc.offset) and state.mode != "settings":
        state.recover_clock()
        return
    saving = state.mode == "settings" and key == "B"
    dt = state.press(key, current)
    if not saving:
        return
    offset = state.offset_choice + (60 if state.dst_choice else 0)
    if dt is not None and not valid_local(dt, offset):
        state.clock_error = "Outside UTC date range"
        return
    old_offset = rtc.offset
    old_clock = None
    attempted = False
    phase = "Time"
    try:
        if dt is not None:
            # Snapshot UTC for best-effort rollback; never persist the zone first.
            old_clock = rtc.hardware.datetime()
            rtc.offset = offset
            attempted = True
            weekday = (ordinal(*dt[:3]) - 1) % 7
            rtc.datetime(dt + (weekday,))
            rtc.rtc_to_localtime()
            if tuple(rtc.datetime()[:5]) != tuple(dt[:5]):
                raise OSError("Readback")
        phase = "Save"
        if state.preferences_error or (state.offset, state.dst) != (
            state.offset_choice,
            state.dst_choice,
        ):
            preferences.save(offset=state.offset_choice, dst=state.dst_choice)
    except (OSError, ValueError):
        rtc.offset = old_offset
        state.save_error = phase == "Save"
        if attempted:
            # A failed write may still have reached the chip. Read back rollback.
            try:
                rtc.hardware.datetime(old_clock)
                rtc.rtc_to_localtime()
                actual = rtc.hardware.datetime()
                if tuple(actual[:5]) != tuple(old_clock[:5]):
                    raise OSError("Readback")
            except (OSError, ValueError):
                state.save_partial = True
                state.clock_original = None
        state.clock_error = (
            "Partial save. B: Retry"
            if state.save_partial
            else phase + " failed. B: Retry"
        )
        return
    rtc.offset = offset
    state.offset = state.offset_choice
    state.dst = state.dst_choice
    state.save_error = False
    state.preferences_error = False
    state.clock_saved()


def held_mask():
    mask = 0
    for i, (button, _) in enumerate(controls):
        if badge.held(button):
            mask |= 1 << i
    return mask


refresh = Refresh(badge, display, buttons, held_mask, time)

# Read the wake buttons before refreshing. A/C waits for release or a one-second hold.
badge.poll()
mask = held_mask()
if badge.woken_by_button():
    for i, (button, _) in enumerate(controls):
        if badge.pressed_to_wake(button):
            mask |= 1 << i
key = buttons.feed(mask, time.ticks_ms())
if state.mode != "settings":
    if key:
        press(key)
    if badge.woken_by_button() and mask & 5:
        started = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), started) < 1500:
            badge.poll()
            current = held_mask()
            key = buttons.feed(current, time.ticks_ms())
            if key:
                press(key)
                break
            if not current & 5:
                break
            time.sleep_ms(25)

show()
gc.collect()
last_action = time.ticks_ms()
# Go straight back to sleep after a timed refresh. Stay awake after a button press.
if state.mode == "live" and badge.wake_reason() == powman.WAKE_ALARM:
    sleep_until_change()
    last_action = time.ticks_ms()
last_check = last_action
while True:
    held = refresh.poll()
    key = refresh.next_key()
    if held:
        last_action = time.ticks_ms()
    changed = press(key) if key is not None else False
    now = time.ticks_ms()
    if changed:
        show()
    if key is not None:
        last_action = time.ticks_ms()
    if (
        state.mode == "tour"
        and not held
        and time.ticks_diff(time.ticks_ms(), tour_shown_at) >= TOUR_INTERVAL_MS
    ):
        state.advance_tour()
        show()
        last_action = time.ticks_ms()
    if time.ticks_diff(now, last_check) >= 1000:
        last_check = now
        dt = read_clock(rtc)
        if not valid_local(dt, rtc.offset):
            if state.recover_clock():
                show()
        elif state.mode == "live":
            current = signature(dt)
            if current != last_signature:
                show()
    idle = time.ticks_diff(time.ticks_ms(), last_action)
    if (
        state.mode == "settings"
        and idle >= SETTINGS_IDLE_MS
        and not held
        and not refresh.queue
    ):
        settings_timeout()
        last_action = time.ticks_ms()
    if idle >= 30000 and state.expire():
        show()
    if state.mode == "live" and idle >= 30000:
        # Work out the next wake after the display has finished refreshing.
        dt = read_clock(rtc)
        if valid_local(dt, rtc.offset):
            gc.collect()
            sleep_until_change()
            last_action = time.ticks_ms()
        else:
            state.recover_clock()
            show()
    # Settings cancel unsaved edits after five idle minutes.
    time.sleep_ms(25)
