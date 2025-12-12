# 02 · Tray timeline — worked solution

**Finding:** The source records place tray `07`'s open interval between `2025-12-09 23:58:00 UTC` and `2025-12-10 00:03:00 UTC`. The only same-tray event strictly inside is `E102`, a `label_scan` with the note `blue folder`. `E105` ties the close time and is not inside the interval.

## Normalize the source times before comparing

From the repository root after generating `evidence`:

```sh
python3 - <<'PY'
import csv
from datetime import UTC, datetime
from pathlib import Path

with Path("evidence/tray-timeline/events.csv").open(encoding="ascii", newline="") as source:
    tray = [row for row in csv.DictReader(source) if row["tray"] == "07"]

def utc(row, field):
    return datetime.fromisoformat(row[field]).astimezone(UTC)

opened = next(row for row in tray if row["event"] == "seal_open")
closed = next(row for row in tray if row["event"] == "seal_close")
start = utc(opened, "recorded_at")
end = utc(closed, "recorded_at")
for row in sorted(tray, key=lambda row: utc(row, "recorded_at")):
    at = utc(row, "recorded_at")
    print(at.isoformat(), row["event_id"], row["event"])
    if start < at < end:
        note = bytes.fromhex(row["note_hex"]).decode("ascii")
        print(f"  inside interval; note={note!r}")

ingest_order = sorted(tray, key=lambda row: utc(row, "ingested_at"))
print("Ingest order:", *(row["event_id"] for row in ingest_order))
PY
```

```text
2025-12-09T23:58:00+00:00 E101 seal_open
2025-12-10T00:01:00+00:00 E102 label_scan
  inside interval; note='blue folder'
2025-12-10T00:03:00+00:00 E104 seal_close
2025-12-10T00:03:00+00:00 E105 camera_sync
Ingest order: E104 E105 E101 E102
```

## Interpret the result

- The interval crosses midnight UTC. Add four hours to `E101`'s `19:58` on December 9 and subtract five and a half hours from `E102`'s `05:31` on December 10. Sorting the raw strings would put `E102`'s `05:31` after the `00:03` close on the same date, even though its UTC time is earlier.
- `E103` falls within the same time window but belongs to tray `19`; it is irrelevant to the tray `07` finding. `E105` lands exactly on the upper boundary. Its position in the printed table does not resolve whether it occurred before or after `E104`.
- The collector received the close before the open. `ingested_at` therefore answers a different question from `recorded_at`. The records do not explain the ingest delays or establish clock accuracy.
- Hex is an encoding, not encryption or authentication. The note is the text the row supplies; it does not establish that a blue folder was physically present, moved, or handled by a particular person.

[Exercise brief](../labs/02-tray-timeline.md) · [Project home](../README.md)
