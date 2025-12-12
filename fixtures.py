"""Generate the fixed, synthetic evidence for the two offline labs."""

import argparse
import hashlib
import json
import sys
from pathlib import Path


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
    return {
        "archive-intake/bin-014.dat": b"Scanner offline: retry\n",
        "archive-intake/bin-027.txt": reference,
        "archive-intake/bin-031.pgm": header + raster[:-1] + b"\xfe",
        "archive-intake/intake.json": intake_text.encode("ascii"),
        "tray-timeline/events.csv": events.encode("ascii"),
    }


def generate(destination: Path) -> None:
    """Write evidence to a new directory whose parent already exists."""
    fixtures = _fixture_bytes()
    destination.mkdir()
    for relative_path, data in fixtures.items():
        target = destination / relative_path
        target.parent.mkdir(exist_ok=True)
        with target.open("xb") as output:
            output.write(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new directory; its parent must exist")
    args = parser.parse_args()
    try:
        generate(args.destination)
    except OSError as error:
        print(f"fixtures: could not generate output: {error}", file=sys.stderr)
        return 1
    print(f"Generated fixtures in {args.destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
