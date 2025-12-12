# 02 · Tray timeline

An export from a fictional archive's tray monitor is saved as `evidence/tray-timeline/events.csv`. Reconstruct the events around the open interval for tray `07`.

| Column | Meaning in this exercise |
| --- | --- |
| `event_id` | Row identifier, with no guaranteed ordering semantics |
| `recorded_at` | Timestamp supplied by the source device, including its UTC offset |
| `ingested_at` | Timestamp assigned when the collector received the row |
| `tray` | Tray identifier; leading zeros are part of the ID |
| `event` | Event label supplied by the source device |
| `note_hex` | Optional note encoded as hexadecimal ASCII; blank means no note was supplied |

1. Normalize tray `07`'s source timestamps to UTC and report its open and close times.
2. Which event for tray `07` falls *strictly* between those boundaries? Decode its note.
3. Which row is tied with the close time after normalization? Explain what the timestamps leave unresolved and why using the collector's ingest time would change the story.

**Hint:** Parse timestamps with their offsets before sorting. Filter by tray before deciding what falls inside the interval.

[Worked solution](../writeups/02-tray-timeline.md) · [Project home](../README.md)
