"""Generate the fixed, synthetic evidence for the offline labs."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

LABS = {
    "01": ("archive-intake", "Archive intake"),
    "02": ("tray-timeline", "Tray timeline"),
    "03": ("shelf-reconciliation", "Shelf reconciliation"),
    "04": ("copy-comparison", "Copy comparison"),
}


def _fixture_bytes() -> dict[str, bytes]:
    header = b"P5\n4 3\n255\n"
    raster = bytes((0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 255))
    reference = header + raster
    intake = {
        "record_id": "INT-042",
        "expected_bytes": len(reference),
        "sha256": hashlib.sha256(reference).hexdigest(),
    }
    intake_text = json.dumps(intake, indent=2, sort_keys=True) + "\n"
    events = (
        "event_id,recorded_at,ingested_at,tray,event,note_hex\n"
        "E104,2025-12-10T00:03:00Z,2025-12-10T00:03:01Z,07,seal_close,\n"
        "E101,2025-12-09T19:58:00-04:00,2025-12-10T00:05:00Z,07,seal_open,\n"
        "E105,2025-12-10T01:03:00+01:00,2025-12-10T00:03:03Z,07,camera_sync,\n"
        "E102,2025-12-10T05:31:00+05:30,2025-12-10T00:06:00Z,07,label_scan,"
        "626c756520666f6c646572\n"
        "E103,2025-12-10T00:00:00Z,2025-12-10T00:00:05Z,19,label_scan,\n"
    )
    register = "cabinet,slot\nA,01\nA,02\nB,01\nB,03\n"
    scans = (
        '{"id":"S01","cabinet":"A","slot":"01","result":"accepted"}\n'
        '{"id":"S02","cabinet":"A","slot":"01","result":"accepted"}\n'
        '{"id":"S03","cabinet":"A","slot":"02","result":"unreadable"}\n'
        '{"id":"S04","cabinet":"B","slot":"01","result":"accepted"}\n'
        '{"id":"S05","cabinet":"A","slot":"03","result":"accepted"}\n'
    )
    reading = b"drawer=07\nlabel=blue folder\n"
    return {
        "archive-intake/bin-014.dat": b"Scanner offline: retry\n",
        "archive-intake/bin-027.txt": reference,
        "archive-intake/bin-031.pgm": header + raster[:-1] + b"\xfe",
        "archive-intake/intake.json": intake_text.encode("ascii"),
        "tray-timeline/events.csv": events.encode("ascii"),
        "shelf-reconciliation/register.csv": register.encode("ascii"),
        "shelf-reconciliation/scans.jsonl": scans.encode("ascii"),
        "copy-comparison/delivery/reading.txt": reading,
        "copy-comparison/review/reading.txt": reading.replace(b"\n", b"\r\n"),
        "copy-comparison/staging/reading.txt": reading.replace(b"blue", b"gray"),
        "copy-comparison/staging/renamed.log": reading,
    }


def generate(destination: Path, *, lab_id: str | None = None) -> None:
    """Write all evidence, or one lab by stable ID, to a new directory."""
    fixtures = _fixture_bytes()
    if lab_id is not None:
        if lab_id not in LABS:
            raise ValueError(f"unknown lab ID: {lab_id!r}")
        slug, _ = LABS[lab_id]
        fixtures = {
            name: data for name, data in fixtures.items() if name.startswith(f"{slug}/")
        }
    destination.mkdir()
    for relative_path, data in fixtures.items():
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            output.write(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true", help="list available labs without writing")
    mode.add_argument("--lab", choices=LABS.keys(), metavar="ID", help="generate only this lab ID")
    parser.add_argument("destination", type=Path, nargs="?", help="new directory; its parent must exist")
    args = parser.parse_args()
    if args.list:
        if args.destination is not None:
            parser.error("--list does not take a destination")
        for lab_id, (slug, title) in sorted(LABS.items()):
            print(f"{lab_id}\t{title}\tlabs/{lab_id}-{slug}.md")
        return 0
    if args.destination is None:
        parser.error("a destination is required to generate fixtures")
    try:
        generate(args.destination, lab_id=args.lab)
    except OSError as error:
        print(f"fixtures: could not generate output: {error}", file=sys.stderr)
        return 1
    print(f"Generated fixtures in {args.destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
