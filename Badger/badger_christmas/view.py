# Copyright (C) 2026 Chris Parrish
# SPDX-License-Identifier: MIT
"""Stream the packed artwork and draw the badge screens."""

# BEGIN ARTWORK INDEX
ASSETS = {
    "woodland": (0, 4566, 264, 128),
    "firewood": (4566, 598, 64, 64),
    "present": (5164, 671, 64, 64),
    "sleeping": (5835, 527, 64, 64),
    "forest": (6362, 3924, 264, 128),
    "burrow": (10286, 3063, 264, 128),
    "cookies": (13349, 914, 64, 64),
    "lights": (14263, 997, 64, 64),
    "snow": (15260, 743, 64, 64),
    "pudding": (16003, 776, 64, 64),
    "mushroom": (16779, 134, 20, 20),
    "fir0": (16913, 821, 72, 104),
    "fir1": (17734, 1096, 72, 104),
    "fir2": (18830, 1221, 72, 104),
    "fir3": (20051, 1717, 72, 104),
    "fir4": (21768, 1806, 72, 104),
    "letterbox": (23574, 563, 36, 48),
    "friend_robin": (24137, 125, 20, 24),
    "friend_rabbit": (24262, 331, 28, 40),
    "friend_hedgehog": (24593, 250, 32, 24),
    "invitation": (24843, 721, 64, 64),
    "reading": (25564, 1072, 64, 64),
    "leftovers": (26636, 963, 64, 64),
    "biscuits": (27599, 766, 64, 64),
    "n0": (28365, 202, 23, 30),
    "n1": (28567, 102, 23, 29),
    "n2": (28669, 134, 23, 29),
    "n3": (28803, 152, 23, 30),
    "n4": (28955, 145, 23, 29),
    "n5": (29100, 151, 23, 30),
    "n6": (29251, 192, 23, 30),
    "n7": (29443, 96, 23, 29),
    "n8": (29539, 198, 23, 30),
    "n9": (29737, 194, 23, 30),
    "t!": (29931, 36, 5, 10),
    't"': (29967, 22, 7, 10),
    "t#": (29989, 56, 8, 10),
    "t$": (30045, 57, 8, 13),
    "t%": (30102, 89, 13, 12),
    "t&": (30191, 61, 10, 12),
    "t'": (30252, 14, 4, 10),
    "t(": (30266, 44, 5, 13),
    "t)": (30310, 39, 5, 13),
    "t*": (30349, 19, 6, 10),
    "t+": (30368, 26, 9, 9),
    "t,": (30394, 11, 4, 5),
    "t-": (30405, 8, 5, 5),
    "t.": (30413, 5, 4, 2),
    "t/": (30418, 30, 5, 10),
    "t0": (30448, 59, 8, 11),
    "t1": (30507, 45, 8, 10),
    "t2": (30552, 43, 8, 10),
    "t3": (30595, 50, 8, 11),
    "t4": (30645, 50, 8, 10),
    "t5": (30695, 44, 8, 11),
    "t6": (30739, 55, 8, 11),
    "t7": (30794, 32, 8, 10),
    "t8": (30826, 59, 8, 11),
    "t9": (30885, 57, 8, 11),
    "t:": (30942, 19, 5, 8),
    "t;": (30961, 24, 5, 11),
    "t<": (30985, 34, 9, 9),
    "t=": (31019, 15, 9, 8),
    "t>": (31034, 32, 9, 9),
    "t?": (31066, 45, 9, 11),
    "t@": (31111, 119, 14, 15),
    "tA": (31230, 54, 11, 10),
    "tB": (31284, 46, 10, 10),
    "tC": (31330, 52, 10, 11),
    "tD": (31382, 51, 10, 10),
    "tE": (31433, 28, 10, 10),
    "tF": (31461, 25, 9, 10),
    "tG": (31486, 64, 11, 12),
    "tH": (31550, 39, 10, 10),
    "tI": (31589, 21, 4, 10),
    "tJ": (31610, 51, 8, 11),
    "tK": (31661, 55, 11, 10),
    "tL": (31716, 22, 9, 10),
    "tM": (31738, 87, 12, 10),
    "tN": (31825, 54, 10, 10),
    "tO": (31879, 63, 11, 12),
    "tP": (31942, 40, 10, 10),
    "tQ": (31982, 68, 11, 12),
    "tR": (32050, 49, 11, 10),
    "tS": (32099, 61, 10, 12),
    "tT": (32160, 40, 9, 10),
    "tU": (32200, 47, 10, 11),
    "tV": (32247, 57, 11, 10),
    "tW": (32304, 95, 14, 10),
    "tX": (32399, 52, 10, 10),
    "tY": (32451, 52, 11, 10),
    "tZ": (32503, 34, 9, 10),
    "t[": (32537, 40, 5, 13),
    "t\\": (32577, 29, 5, 10),
    "t]": (32606, 48, 5, 13),
    "t^": (32654, 29, 9, 11),
    "t_": (32683, 5, 9, 3),
    "t`": (32688, 8, 5, 10),
    "ta": (32696, 41, 8, 9),
    "tb": (32737, 49, 9, 11),
    "tc": (32786, 42, 8, 9),
    "td": (32828, 63, 9, 11),
    "te": (32891, 42, 8, 9),
    "tf": (32933, 42, 6, 11),
    "tg": (32975, 72, 9, 11),
    "th": (33047, 49, 9, 10),
    "ti": (33096, 21, 4, 10),
    "tj": (33117, 31, 5, 13),
    "tk": (33148, 43, 8, 10),
    "tl": (33191, 21, 4, 10),
    "tm": (33212, 88, 13, 8),
    "tn": (33300, 47, 9, 8),
    "to": (33347, 47, 9, 9),
    "tp": (33394, 50, 9, 11),
    "tq": (33444, 68, 9, 11),
    "tr": (33512, 24, 6, 8),
    "ts": (33536, 43, 8, 9),
    "tt": (33579, 30, 5, 11),
    "tu": (33609, 48, 9, 9),
    "tv": (33657, 38, 8, 8),
    "tw": (33695, 65, 11, 8),
    "tx": (33760, 40, 8, 8),
    "ty": (33800, 55, 8, 11),
    "tz": (33855, 28, 7, 8),
    "t{": (33883, 47, 6, 14),
    "t|": (33930, 30, 4, 14),
    "t}": (33960, 53, 6, 14),
    "t~": (34013, 15, 9, 7),
    "season_spring": (34028, 7742, 264, 128),
    "season_autumn": (41770, 6072, 264, 128),
    "crumbs": (47842, 45, 46, 18),
    "letter": (47887, 49, 14, 10),
    "butterfly": (47936, 119, 20, 18),
    "fallen_apple": (48055, 76, 16, 16),
    "rabbit_gift": (48131, 297, 26, 38),
}
GLYPHS = {
    "n0": (0, -29, 222),
    "n1": (0, -29, 222),
    "n2": (0, -29, 222),
    "n3": (0, -29, 222),
    "n4": (0, -29, 222),
    "n5": (0, -29, 222),
    "n6": (0, -29, 222),
    "n7": (0, -29, 222),
    "n8": (0, -29, 222),
    "n9": (0, -29, 222),
    "t ": (0, 0, 40),
    "t!": (0, -10, 48),
    't"': (0, -10, 68),
    "t#": (0, -10, 78),
    "t$": (0, -11, 78),
    "t%": (0, -11, 125),
    "t&": (0, -11, 100),
    "t'": (0, -10, 32),
    "t(": (0, -10, 48),
    "t)": (0, -10, 48),
    "t*": (0, -10, 55),
    "t+": (0, -9, 82),
    "t,": (0, -2, 40),
    "t-": (0, -5, 48),
    "t.": (0, -2, 40),
    "t/": (-1, -10, 40),
    "t0": (0, -10, 78),
    "t1": (0, -10, 78),
    "t2": (0, -10, 78),
    "t3": (0, -10, 78),
    "t4": (0, -10, 78),
    "t5": (0, -10, 78),
    "t6": (0, -10, 78),
    "t7": (0, -10, 78),
    "t8": (0, -10, 78),
    "t9": (0, -10, 78),
    "t:": (0, -8, 48),
    "t;": (0, -8, 48),
    "t<": (0, -9, 82),
    "t=": (0, -8, 82),
    "t>": (0, -9, 82),
    "t?": (0, -11, 85),
    "t@": (0, -11, 138),
    "tA": (0, -10, 100),
    "tB": (0, -10, 100),
    "tC": (0, -11, 100),
    "tD": (0, -10, 100),
    "tE": (0, -10, 92),
    "tF": (0, -10, 85),
    "tG": (0, -11, 110),
    "tH": (0, -10, 100),
    "tI": (0, -10, 40),
    "tJ": (0, -10, 78),
    "tK": (0, -10, 100),
    "tL": (0, -10, 85),
    "tM": (0, -10, 118),
    "tN": (0, -10, 100),
    "tO": (0, -11, 110),
    "tP": (0, -10, 92),
    "tQ": (0, -11, 110),
    "tR": (0, -10, 100),
    "tS": (0, -11, 92),
    "tT": (0, -10, 85),
    "tU": (0, -10, 100),
    "tV": (-1, -10, 92),
    "tW": (0, -10, 132),
    "tX": (0, -10, 92),
    "tY": (-1, -10, 92),
    "tZ": (0, -10, 85),
    "t[": (0, -10, 48),
    "t\\": (-1, -10, 40),
    "t]": (0, -10, 48),
    "t^": (0, -11, 82),
    "t_": (-1, 0, 78),
    "t`": (0, -10, 48),
    "ta": (0, -8, 78),
    "tb": (0, -10, 85),
    "tc": (0, -8, 78),
    "td": (0, -10, 85),
    "te": (0, -8, 78),
    "tf": (0, -11, 48),
    "tg": (0, -8, 85),
    "th": (0, -10, 85),
    "ti": (0, -10, 40),
    "tj": (-1, -10, 40),
    "tk": (0, -10, 78),
    "tl": (0, -10, 40),
    "tm": (0, -8, 125),
    "tn": (0, -8, 85),
    "to": (0, -8, 85),
    "tp": (0, -8, 85),
    "tq": (0, -8, 85),
    "tr": (0, -8, 55),
    "ts": (0, -8, 78),
    "tt": (0, -10, 48),
    "tu": (0, -8, 85),
    "tv": (0, -8, 78),
    "tw": (0, -8, 110),
    "tx": (0, -8, 78),
    "ty": (0, -8, 78),
    "tz": (0, -8, 70),
    "t{": (0, -11, 55),
    "t|": (0, -10, 40),
    "t}": (0, -11, 55),
    "t~": (0, -7, 82),
}
# END ARTWORK INDEX


class Renderer:
    def __init__(self, screen, path):
        if (screen.width, screen.height) != (264, 176):
            raise ValueError("Badger 2350 screen required")
        self.pixels = memoryview(screen)
        if len(self.pixels) != 264 * 176 * 4:
            raise ValueError("Unsupported screen buffer layout")
        self.file = open(path, "rb")
        self.chunk = bytearray(128)

    def close(self):
        self.file.close()

    def draw(self, name, x, y):
        offset, length, w, h = ASSETS[name]
        if x < 0 or y < 0 or x + w > 264 or y + h > 176:
            raise ValueError("Asset outside display")
        self.file.seek(offset)
        remaining = length
        index = 0
        total = w * h
        pixels = self.pixels
        while remaining:
            count = (
                self.file.readinto(self.chunk)
                if remaining >= 128
                else self.file.readinto(memoryview(self.chunk)[:remaining])
            )
            if not count:
                raise ValueError("Truncated artwork")
            remaining -= count
            for j in range(count):
                token = self.chunk[j]
                shade = token >> 5
                run = (token & 31) + 1
                if shade > 4 or index + run > total:
                    raise ValueError("Invalid artwork run")
                if shade != 4:
                    value = shade * 85
                    for i in range(index, index + run):
                        pos = ((y + i // w) * 264 + x + i % w) * 4
                        pixels[pos] = value
                        pixels[pos + 1] = value
                        pixels[pos + 2] = value
                        pixels[pos + 3] = 255
                index += run
        if index != total:
            raise ValueError("Incomplete artwork")

    def text_width(self, text, large=False):
        total = 0
        for ch in text:
            total += GLYPHS[("n" if large else "t") + ch][2] + (0 if large else 4)
        return max(0, (total - (0 if large else 4) + 5) // 10)

    def text(self, text, x, baseline, large=False):
        cursor = x * 10
        for ch in text:
            key = ("n" if large else "t") + ch
            dx, dy, advance = GLYPHS[key]
            if key in ASSETS:
                self.draw(key, (cursor + 5) // 10 + dx, baseline + dy)
            cursor += advance + (0 if large else 4)

    def rule(self, y):
        for x in range(264):
            p = (y * 264 + x) * 4
            self.pixels[p] = 0
            self.pixels[p + 1] = 0
            self.pixels[p + 2] = 0
            self.pixels[p + 3] = 255


from story import (
    SCENES,
    remaining,
    scene_id,
    mushroom_day,
    tree_stage,
    friends,
    daily_task,
)

from story import draw_surprise


def draw_story(r, dt, secret=False):
    background, pose, _ = SCENES[scene_id(dt)]
    if secret:
        background, pose = "burrow", "biscuits"
    r.draw(background, 0, 48)
    if pose is None:
        # Seasonal pictures already contain Badger and a visiting friend.
        if not secret:
            draw_surprise(r, dt)
        if mushroom_day(dt):
            r.draw("mushroom", 244, 154)
        return
    stage = tree_stage(dt)
    if background == "burrow" and stage >= 0:
        r.draw("fir" + str(stage), 12, 66)
    if scene_id(dt) == 1 and not secret:
        r.draw("letterbox", 108, 126)
    # Leave the friends off screen while Badger is asleep.
    visitors = friends(dt) if pose != "sleeping" and not secret else 0
    if visitors >= 1:
        r.draw("friend_robin", 140, 148)
    if visitors >= 2:
        r.draw("friend_rabbit", 110, 132)
    if visitors >= 3:
        r.draw("friend_hedgehog", 228, 148)
    if mushroom_day(dt) and not secret:
        r.draw("mushroom", 88, 154)
    r.draw(pose, 160, 110)
    if not secret:
        draw_surprise(r, dt)


def scene(r, dt):
    count = remaining(dt)
    digits = str(count)
    x = max(47, 20 + 22 * len(digits))
    r.text(digits, 12, 36, True)
    word = "DAY" if count == 1 else "DAYS"
    r.text(word + " TO CHRISTMAS", x, 18)
    from story import daily_saying

    caption = daily_saying(dt)
    r.text(caption, x, 37)
    r.rule(46)
    draw_story(r, dt)


def tour_page(r, dt, index, total):
    r.text("OSWIN'S YEAR", 10, 18)
    progress = str(index + 1) + "/" + str(total)
    r.text(progress, 254 - r.text_width(progress), 18)
    month = (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    )[dt[1] - 1]
    r.text(month + "  A/C: skip  B: today", 10, 37)
    r.rule(46)
    draw_story(r, dt)


def secret_page(r, dt):
    r.text("BADGER'S BISCUIT STASH", 10, 18)
    r.text("You found it! B: back.", 10, 37)
    r.rule(46)
    draw_story(r, dt, True)


def wrap(r, text, width):
    lines = []
    line = ""
    for word in text.split():
        candidate = line + (" " if line else "") + word
        if line and r.text_width(candidate) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def diary_page(r, dt):
    # Select the diary entry for the current local date.
    from story import entry

    r.text("BADGER'S DIARY", 10, 21)
    r.text("%04d-%02d-%02d" % tuple(dt[:3]), 10, 44)
    for i, line in enumerate(wrap(r, entry(dt), 242)):
        r.text(line, 10, 72 + i * 21)
    r.text("B: today   C: year tour", 10, 170)


def task_page(r, dt):
    r.text("TODAY'S LITTLE TASK", 10, 21)
    r.text("%04d-%02d-%02d" % tuple(dt[:3]), 10, 47)
    for i, line in enumerate(wrap(r, daily_task(dt), 242)):
        r.text(line, 10, 82 + i * 23)
    r.text("C: follow the crumbs", 10, 125)
    r.text("UP: settings", 10, 147)
    r.text("A: diary   B: today", 10, 169)
    r.draw("friend_robin", 234, 146)


def settings_page(
    r, error=False, offset=0, field=0, dst=False, values=None, message="", partial=False
):
    from clock import label

    if values is None:
        values = (2026, 10, 2, 12, 0)
    r.text("SETTINGS", 10, 18)
    r.text(("> " if field == 0 else "  ") + "Timezone: " + label(offset), 10, 42)
    r.text(
        ("> " if field == 1 else "  ") + "DST: " + ("On (+1 hour)" if dst else "Off"),
        10,
        64,
    )
    # Measure each date/time part so the underline stays under the selected field.
    parts = (
        "%04d" % values[0],
        "%02d" % values[1],
        "%02d" % values[2],
        "%02d" % values[3],
        "%02d" % values[4],
    )
    gaps = ("-", "-", "   ", ":", "")
    x = 10
    for i, part in enumerate(parts):
        r.text(part, x, 89)
        width = r.text_width(part)
        if field == i + 2:
            for px in range(x, x + width):
                pos = (93 * 264 + px) * 4
                r.pixels[pos] = 0
                r.pixels[pos + 1] = 0
                r.pixels[pos + 2] = 0
                r.pixels[pos + 3] = 255
        x += r.text_width(part + gaps[i]) + 1
        if gaps[i]:
            r.text(gaps[i], x - r.text_width(gaps[i]) - 1, 89)
    labels = ("Timezone", "DST", "Year", "Month", "Day", "Hour", "Minute")
    r.text(
        message or ("Save failed. B: Retry" if error else "Editing: " + labels[field]),
        10,
        112,
    )
    r.text("UP/DOWN: Select", 10, 132)
    r.text("A/C: Change   B: Save", 10, 151)
    r.text("HOME: Exit" if partial else "HOME: Cancel", 10, 170)


HUNT = (
    (
        "A little forest lives indoors.",
        "Look for branches.",
        ("A: the tree", "B: the book", "C: the letterbox"),
    ),
    (
        "Where do invitations wait?",
        "Look for the envelope.",
        ("A: the window", "B: the tree", "C: the letterbox"),
    ),
    (
        "Where does Badger warm his paws?",
        "Follow the warmth.",
        ("A: the shelf", "B: the fireplace", "C: the window"),
    ),
)


def hunt_page(r, step, miss=False):
    clue, hint, options = HUNT[step]
    r.text("FOLLOW THE CRUMBS", 10, 20)
    r.text(str(step + 1) + "/3", 229, 20)
    for i, line in enumerate(wrap(r, clue, 242)):
        r.text(line, 10, 46 + i * 21)
    if miss:
        r.text(hint, 10, 89)
    for i, option in enumerate(options):
        r.text(option, 10, 112 + i * 21)
    r.text("DOWN: leave the hunt", 10, 173)
