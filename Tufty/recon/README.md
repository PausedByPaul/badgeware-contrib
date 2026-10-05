# Recon

A WiFi and Bluetooth scanner that tells you what things *are* rather than
listing MAC addresses.

![dashboard](https://raw.githubusercontent.com/jgamblin/tufty-recon/main/shots/recon.png)
![detail](https://raw.githubusercontent.com/jgamblin/tufty-recon/main/shots/recon-detail.png)

Carried around for an evening it logged 214 access points and named 86% of them
by manufacturer, plus 93% of the Bluetooth devices it heard. It picks out
cable-company gateways, Tile trackers, AirPods, smart-home hubs and a
garage-door opener by name.

Everything is passive. It never associates, transmits or captures traffic;
every beacon and advertisement it reads is a public broadcast.

Needs badgeware firmware **v3.1.0 or newer**.

## Views

- **BILLBOARD** is one big number, readable from a couple of metres, for
  wearing the badge facing outward. The app opens here.
- **DASH** counts what is around you by kind: access points, phones, computers,
  wearables, audio/TV, trackers, Find My, other. Pick a row and press **A** to
  see just those.
- **LIVE** lists everything in range, strongest first.
- **DETAIL** shows the MAC, vendor, channel, security or protocol for one
  device.
- **FLAGS** surfaces open networks, WEP, rogue APs, possible evil twins and
  trackers.
- **VENDORS** ranks the hardware in the room.
- **LOG** shows the persistent tally and how full the log is.
- **SHARE** shows a QR code and the URL of the source, for when someone asks.

## Buttons

| Button | Does |
| --- | --- |
| **B** | next view |
| **A** | drill into a dashboard row / open detail / back |
| **UP / DOWN** | scroll |
| **C** | clear the drill-down, or cycle all / wifi / ble |
| **UP+DOWN** | hold two seconds on LOG to erase the log |

## How it identifies things

`data/` holds two databases compiled to sorted fixed-width binaries and
searched with a binary search on the badge:

- 39,877 IEEE MA-L prefixes → hardware manufacturer
- 3,988 Bluetooth SIG company IDs → chipset and brand

plus hand-written tables in `identify.py` for Apple Continuity subtypes, GAP
appearance values, notable service UUIDs, and SSID naming conventions.

The 195KB key index is read into RAM at startup, which takes a lookup from 11ms
on flash to 1.8ms. Devices are identified lazily, two per frame, so a crowded
room never stalls the display.

## The log

Every access point and stable device is written to `/state/recon_*.bin` as
fixed-width binary, de-duplicated against what is already on disk at startup.
It takes a 560KB budget of the filesystem and stops there rather than filling
it, and the LOG view shows a capacity meter.

Pull it off as CSV with
[`tools/export_log.py`](https://github.com/jgamblin/tufty-recon/blob/main/tools/export_log.py).

## Notes on counting

**Bluetooth addresses rotate.** Phones and watches re-randomise roughly every
15 minutes, so only stable addresses count as devices and rotating ones are
reported separately as an inflated upper bound.

The address bits alone are not enough. Apple's Find My beacons derive their
address from a key that rotates about every 15 minutes but present as *static
random*, which by the bits looks permanent. In one two-hour outing that meant
356 distinct Find My addresses in 96 minutes, roughly 55 real devices. Rotation
is decided from the payload as well as the address.

**Find My is not a tracker count**, since every iPhone and Mac with Find My
enabled emits it. It gets its own bucket; only dedicated trackers (Tile,
SmartTag) count as trackers.

**Virtual BSSIDs** are recovered by trying the eight candidates that share the
first octet's top five bits, because vendors derive them differently (Google
flips the locally-administered bit, Netgear sets three). The ones that still
miss are left unknown rather than guessed.

**WiFi and BLE share one radio.** With BLE holding a continuous scan,
`wlan.scan()` returns access points with every RSSI as 0, so the BLE listen is
paused for the couple of seconds a WiFi scan takes.

## Source

[jgamblin/tufty-recon](https://github.com/jgamblin/tufty-recon),
which also has the database builder, CSV exporter, and an on-device stress test.
