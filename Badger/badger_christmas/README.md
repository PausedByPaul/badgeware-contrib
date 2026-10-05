# Oswin Thistle’s Woodland Christmas

Version 1.0

I wanted a little Christmas countdown I could leave sitting on my Badger. Then
I thought, why not give him his own woodland home and let things change through
the year? That became Oswin Thistle.

He has a garden, friends who stop by, a diary, and a biscuit stash he probably
thinks nobody knows about. There’s a daily saying and the occasional little
surprise, too. Keep an eye out for the mushroom.

I also wanted this to show what the Badger can do. It’s a little woodland world
that changes throughout the year. You can enjoy it as it is, or look through the
code and see how it works. Hopefully, it gives you some ideas for your own apps.

This is for the **Badger 2350 running Badgeware v3**. It works offline.

## What he gets up to

There’s gardening in spring and summer, apples in autumn, and Christmas
preparations when November comes around. The weekly scenes turn into daily
scenes near Christmas. Afterward, there are leftovers and a well-earned nap.

If you don’t want to wait all year to see it, try **Oswin’s year**. From the
countdown, press **DOWN**, **A**, then **C**. It plays through 12 scenes. A/C
skips backward or forward, and B brings you back to today. It leaves the real
clock alone.

## Put it on your Badger

1. Connect the badge and double-tap RESET so its drive appears.
2. Copy `Badger/badger_christmas` into the drive’s `apps` folder.
3. Eject the drive and open the app from the badge menu.

Copy the whole app folder. The artwork and other files need to stay together.

## The buttons

| Button | What it does |
| --- | --- |
| A / C | Browse earlier or later scenes |
| B | Back to today |
| UP | Settings |
| DOWN | Today’s little task; A there opens the diary |
| Hold A + C | Start the biscuit hunt |
| HOME | Back to the badge menu |

In settings, UP/DOWN selects a field, A/C changes it, and B saves. HOME cancels
unsaved edits. After five idle minutes, unsaved edits are canceled and the
badge sleeps. If a partial save is reported, check the time before leaving;
HOME cannot undo clock changes that have already happened.

## Getting the time right

The app treats the hardware clock as UTC. In **Timezone**, pick your whole-hour
offset and switch **DST** on or off yourself. For Eastern time, use UTC-05:00
with DST on during daylight saving time. The choices are remembered next time.

It doesn’t fetch NTP time or change DST automatically. You can set the local
date and time on the same settings page. The hardware date range is
2025–2099 UTC. Half-hour and quarter-hour timezones aren’t supported.

## Keeping it small

I didn’t want this taking up a bunch of space on the badge. The pictures use
four shades and share one compressed artwork file. The app sleeps between
scheduled changes, and the little surprises don’t need extra wake-ups.

## Have a look at how it works

There’s quite a bit you can learn from a little countdown: fitting pictures
into limited space, putting the badge to sleep between updates, responding to
buttons, and remembering settings. Oswin’s year lets you see the seasonal
changes without waiting months for them.

If you want to look through the code, these are good places to start inside
`badger_christmas`:

- `story.py` decides which scene, diary entry, and saying to show.
- `clock.py` handles the time, timezone, and saved settings.
- `view.py` keeps the artwork index and draws the pictures and text.
- `controller.py` connects the screens and button actions.
- `__init__.py` handles buttons and screen updates, brings it all together, and
  puts the badge to sleep when it can.

## License

Copyright © 2026 Chris Parrish.
The code, documentation, and packaged artwork are **MIT licensed**. You can
use them, change them, and share them, including in other projects or commercial
work. Just keep the copyright and license notices with copies or substantial
portions you redistribute.

See [LICENSE](LICENSE).
