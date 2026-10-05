# Copyright (C) 2026 Chris Parrish
# SPDX-License-Identifier: MIT
"""Calendar, scenes, diary, sayings, and occasional woodland surprises."""

SCENES = (
    ("woodland", "firewood", "Gathering firewood"),
    ("woodland", "invitation", "Posting invitations"),
    ("woodland", "invitation", "Robin has arrived"),
    ("forest", "firewood", "Welcome, Rabbit"),
    ("woodland", "cookies", "Hello, Hedgehog"),
    ("burrow", "firewood", "A tree for our home"),
    ("burrow", "lights", "The first baubles"),
    ("burrow", "cookies", "A ribbon of sparkle"),
    ("burrow", "present", "Wrapping together"),
    ("forest", "snow", "A snowbadger day"),
    ("burrow", "present", "Gifts beneath the tree"),
    ("burrow", "lights", "The lights go on"),
    ("burrow", "cookies", "Baking with friends"),
    ("burrow", "pudding", "Setting the table"),
    ("burrow", "pudding", "The star is up!"),
    ("burrow", "cookies", "One last little treat"),
    ("burrow", "sleeping", "All tucked in"),
    ("burrow", "present", "Together at Christmas"),
    ("burrow", "leftovers", "Lovely leftovers"),
    ("burrow", "reading", "A book by the fire"),
    ("burrow", "sleeping", "Time for a winter nap"),
    ("season_spring", None, "In the garden"),
    ("season_autumn", None, "Apples for a pie"),
)
EVENTS = (
    (1, 1, 0, 20),
    (1, 8, 0, 0),
    (3, 1, 0, 21),
    (9, 1, 0, 22),
    (11, 1, 0, 1),
    (11, 8, 0, 2),
    (11, 15, 0, 3),
    (11, 22, 0, 4),
    (11, 29, 0, 5),
    (12, 6, 0, 6),
    (12, 13, 0, 7),
    (12, 18, 0, 8),
    (12, 19, 0, 9),
    (12, 20, 0, 10),
    (12, 21, 0, 11),
    (12, 22, 0, 12),
    (12, 23, 0, 13),
    (12, 24, 0, 14),
    (12, 24, 15, 15),
    (12, 24, 20, 16),
    (12, 25, 0, 16),
    (12, 25, 7, 17),
    (12, 26, 0, 18),
    (12, 28, 0, 19),
    (12, 30, 0, 20),
)
TASKS = (
    "Put the kettle on.",
    "Send someone a kind note.",
    "Wrap something lovely.",
    "Listen for woodland birds.",
    "Make a paper snowflake.",
    "Choose a favourite story.",
    "Tell someone you miss them.",
    "Find a cosy pair of socks.",
    "Make time for a warm drink.",
    "Share a happy memory.",
    "Draw a little winter scene.",
    "Tidy a cosy corner.",
    "Leave a cheerful message.",
    "Read a chapter together.",
    "Make a handmade gift tag.",
    "Thank someone for helping.",
    "Plan a little festive treat.",
    "Take a quiet winter walk.",
    "Put on your favourite music.",
    "Wrap a gift with care.",
    "Switch on the little lights.",
    "Bake something to share.",
    "Set a place for a friend.",
    "Make a wish beneath the star.",
    "Enjoy being together.",
    "Enjoy the lovely leftovers.",
    "Call someone you care about.",
    "Read beside a warm blanket.",
    "Share your favourite moment.",
    "Take a well-earned rest.",
    "Remember a happy day this year.",
)


def leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def month_days(y, m):
    return (31, 29 if leap(y) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m - 1]


def valid(dt):
    try:
        y, m, d, h, mi, s = dt[:6]
        return (
            2025 <= y <= 2099
            and 1 <= m <= 12
            and 1 <= d <= month_days(y, m)
            and 0 <= h < 24
            and 0 <= mi < 60
            and 0 <= s < 60
        )
    except (TypeError, ValueError, IndexError):
        return False


def ordinal(y, m, d):
    n = y - 1
    return (
        365 * n
        + n // 4
        - n // 100
        + n // 400
        + sum(month_days(y, i) for i in range(1, m))
        + d
    )


def remaining(dt):
    y, m, d = dt[:3]
    target = y + int((m, d) > (12, 25))
    return ordinal(target, 12, 25) - ordinal(y, m, d)


def scene_id(dt):
    key = (dt[1], dt[2], dt[3])
    chosen = 0
    for m, d, h, i in EVENTS:
        if (m, d, h) > key:
            break
        chosen = i
    return chosen


def tree_stage(dt):
    # -1: no tree; 0: bare; 1: baubles; 2: garland; 3: gifts; 4: star.
    m, d = dt[1:3]
    if m == 1 and d < 8:
        return 4
    if (m, d) < (11, 29):
        return -1
    if (m, d) < (12, 6):
        return 0
    if (m, d) < (12, 13):
        return 1
    if (m, d) < (12, 20):
        return 2
    if (m, d) < (12, 24):
        return 3
    return 4


def friends(dt):
    # Friends arrive in order, stay for Christmas, then leave Badger to rest.
    m, d = dt[1:3]
    if (m, d) > (12, 25) or m < 11:
        return 0
    return int((m, d) >= (11, 8)) + int((m, d) >= (11, 15)) + int((m, d) >= (11, 22))


def daily_task(dt):
    if dt[1] == 12:
        return TASKS[dt[2] - 1]
    if dt[1] == 1 and dt[2] < 8:
        return "Take a little winter rest."
    return TASKS[(ordinal(*dt[:3]) - 1) % 23]


def next_wake(dt):
    y, m, d, h, mi, s = dt[:6]
    now = h * 3600 + mi * 60 + s
    result = 86400 - now
    for em, ed, eh, _ in EVENTS:
        target = eh * 3600
        if (em, ed) == (m, d) and target > now:
            result = min(result, target - now)
    return max(1, result)


def preview_date(year, index):
    m, d, h, _ = EVENTS[index]
    return (year, m, d, h, 0, 0)


def mushroom_day(dt):
    # Pick roughly one day in twenty. The same date always gives the same result.
    n = ordinal(*dt[:3])
    n = ((n ^ (n >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
    n = ((n ^ (n >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
    return (n ^ (n >> 16)) % 20 == 0


DECEMBER = (
    "Found the decorations. Also found a biscuit from last year. Left that one.",
    "Rabbit sent wrapping tips. Apparently, more ribbon is not always the answer.",
    "Tested the fairy lights. One blinked at me. I blinked back.",
    "Made a list of presents. Put biscuits on it twice. An honest mistake.",
    "Swept the burrow. Most of the crumbs belonged to me.",
    "Hung the first baubles. The low branches look especially pleased.",
    "Robin inspected the tree. A very small inspector with very high standards.",
    "Wrapped a present so well I forgot what it was. A surprise for everyone.",
    "Hedgehog offered to carry ribbon. An excellent idea until we needed it back.",
    "Practised my festive welcome. The kettle interrupted at the best bit.",
    "Found a spare stocking. Filled it with hope. Biscuits would be heavier.",
    "Rabbit says the tree leans. I say it is listening to the fire.",
    "Added the garland. Untangling it took one pot of tea and two biscuits.",
    "Wrote the gift tags. My neatest writing says: To someone lovely.",
    "Counted the mugs. Then counted my friends. Put another mug out, just in case.",
    "Robin brought a berry for the table. I found our smallest plate.",
    "Tidied the biscuit tin. The biscuits are now much closer together.",
    "Wrapped the last parcels. One has ears. Rabbit says that is probably fine.",
    "Made a snowbadger. Gave him a scarf. He has not offered to return it.",
    "Put gifts beneath the tree. Tried very hard not to shake my own.",
    "Lit the burrow lights. Even the shadows look ready for Christmas.",
    "Baked biscuits for everyone. Quality control was a serious responsibility.",
    "Set the table. Saved the warmest chair for whoever arrives coldest.",
    "The star is on the tree. A treat is ready. Tonight, even I shall go to bed.",
    "My friends are here. The kettle is singing. This is my favourite present.",
    "Breakfast was leftovers. Lunch may be too. A beautifully simple plan.",
    "Found one last parcel behind the tree. It was the tea I bought myself.",
    "Opened my new book. Read three pages before the fire made me sleepy.",
    "A quiet day, a warm mug, and nowhere at all to hurry.",
    "Folded the spare blankets. Kept the softest one within easy reach.",
    "Another year nearly tucked away. I shall greet the next one after a nap.",
)
WINTER = (
    "A new year outside. The same good blanket inside.",
    "Dreamed of a very large biscuit. Woke up and checked the tin.",
    "Robin tapped on the window. I waved from under my blanket.",
    "The kettle and I are taking turns being quiet.",
    "Read another page. That is quite enough adventure for one afternoon.",
    "The burrow is peaceful. I think I shall leave it that way.",
    "One last winter nap. Tomorrow can find its own slippers.",
)
EVERYDAY = (
    "Walked to the old oak. It had no news, but listened very politely.",
    "Robin visited for a crumb. Stayed for the conversation.",
    "Found a smooth pebble. It has joined my collection of important pebbles.",
    "Rabbit waved from the path. I waved back with my entire cup of tea.",
    "Mended a pocket. Discovered why I had been losing biscuits.",
    "Hedgehog sent a note. The writing was small. The kindness was not.",
    "Put the kettle on before deciding what to do. A reliable first step.",
    "Heard rustling by the gate. A leaf was having a very busy morning.",
    "Moved my chair into a patch of sunshine. Excellent planning.",
    "Shared the last biscuit. Found another in my pocket. A very good day.",
    "Sorted the firewood by size. The smallest sticks seemed rather proud.",
    "Sat beside the window and watched the woodland get on with its day.",
)

GARDEN = (
    "Planted a row of seeds. Robin checked my spacing. Twice.",
    "Something ate my seedlings. Rabbit has offered to investigate.",
    "Watered the garden. Also watered my slippers. Both look refreshed.",
    "A new leaf appeared. I congratulated it quietly.",
    "Sat beside the vegetable patch. Growing things takes excellent patience.",
    "Robin borrowed the watering can as a lookout. I shall wait my turn.",
    "Found a worm in the soil. Thanked it for helping with the garden.",
    "The garden needed a little care. So did I. We both enjoyed the sunshine.",
)
APPLES = (
    "Collected twelve apples. Enough for a pie, if I stop checking how they taste.",
    "Hedgehog guarded the apple basket. A small guard with a serious expression.",
    "An apple landed beside me. The tree seems keen to help.",
    "Sorted apples into two piles: pie, and probably also pie.",
    "Took a basket along the path. Came home with apples and a beautiful leaf.",
    "Rabbit offered to taste the pie. Such a generous friend.",
    "The leaves are falling. I am leaving a cosy little pile for Hedgehog.",
    "Saved a good apple for Robin. He may need a smaller slice.",
)


def entry(dt):
    if dt[1] == 12:
        return DECEMBER[dt[2] - 1]
    if dt[1] == 1 and dt[2] <= 7:
        return WINTER[dt[2] - 1]
    if mushroom_day(dt):
        return "A mushroom appeared by the stump. I am fairly sure it was not there yesterday."
    if 3 <= dt[1] <= 8:
        return GARDEN[(ordinal(*dt[:3]) - 1) % len(GARDEN)]
    if 9 <= dt[1] <= 10:
        return APPLES[(ordinal(*dt[:3]) - 1) % len(APPLES)]
    return EVERYDAY[(ordinal(*dt[:3]) - 1) % len(EVERYDAY)]


SAYINGS_WINTER = (
    "Just one more log.",
    "My kettle is ready.",
    "A fine day to read.",
    "Warm paws, warm tea.",
    "I saved you a seat.",
    "Time for a biscuit.",
    "No need to hurry.",
    "My scarf suits me.",
)
SAYINGS_SPRING = (
    "A little rain helps.",
    "New leaves today.",
    "Mind the seedlings.",
    "Robin woke me early.",
    "A muddy sort of day.",
    "My garden is waking.",
    "Tea after digging.",
    "Small seeds, big plans.",
)
SAYINGS_SUMMER = (
    "A shady spot for tea.",
    "Let the bees pass.",
    "Bare paws in the grass.",
    "A picnic? Lovely.",
    "The beans look happy.",
    "Cloud watching today.",
    "One more ripe berry.",
    "I like the long days.",
)
SAYINGS_AUTUMN = (
    "An apple for my pie.",
    "Leaves in my pockets.",
    "A good day for soup.",
    "My scarf is back.",
    "More logs for later.",
    "A biscuit? Or two?",
    "Mind the crunchy leaf.",
    "Come in. Kettle is on.",
)
SAYINGS_FESTIVE = (
    "A ribbon for Robin.",
    "I hid the good biscuits.",
    "Room for one more.",
    "A little more sparkle.",
    "Who moved my ribbon?",
    "Save a seat for Rabbit.",
    "The tree looks happy.",
    "A parcel for a friend.",
)


def daily_saying(dt):
    month, day = dt[1:3]
    if (month, day) == (12, 25):
        return "Merry Christmas!"
    pool = (
        SAYINGS_WINTER
        if month < 3
        else SAYINGS_SPRING
        if month < 6
        else SAYINGS_SUMMER
        if month < 9
        else SAYINGS_AUTUMN
        if month < 12
        else SAYINGS_FESTIVE
    )
    return pool[(ordinal(*dt[:3]) - 1) % len(pool)]


def surprise(dt):
    n = ordinal(*dt[:3])
    n = ((n ^ (n >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
    n = ((n ^ (n >> 16)) * 0x45D9F3B) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    if n % 8 or mushroom_day(dt):
        return None
    background, pose, _ = SCENES[scene_id(dt)]
    if pose == "sleeping":
        return None
    choices = ("crumbs", "letter")
    if 3 <= dt[1] <= 8:
        choices += ("butterfly",)
    if 9 <= dt[1] <= 10:
        choices += ("fallen_apple",)
    if dt[1] == 12 and dt[2] <= 24 and background == "burrow":
        choices += ("rabbit_gift",)
    return choices[(n >> 8) % len(choices)]


def draw_surprise(r, dt):
    kind = surprise(dt)
    if kind is None:
        return
    if kind == "crumbs":
        r.draw("crumbs", 76, 149)
    elif kind == "letter":
        r.draw("friend_robin", 219, 80)
        r.draw("letter", 229, 101)
    elif kind == "butterfly":
        r.draw("butterfly", 145, 66)
    elif kind == "fallen_apple":
        r.draw("fallen_apple", 148, 155)
    else:
        r.draw("rabbit_gift", 86, 132)
