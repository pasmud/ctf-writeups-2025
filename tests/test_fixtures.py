import csv
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "fixtures.py"
FIXTURE_DIGESTS = {
    "archive-intake/bin-014.dat": "d8500a6a365777aef8a2521eff0a03b85134e7993d737257a76d18b767d85537",
    "archive-intake/bin-027.txt": "7277064ede230053f982c9e0ebf4056d1452cbf179ba0b77fbd161647e59ffc0",
    "archive-intake/bin-031.pgm": "fb19bbe5e1d1047e8be03ac1584cd714084314d147b4d4240d6069fdcfcc7d39",
    "archive-intake/intake.json": "50364a31ada872564f8e0b23c46f0d52c729fad2dc347530ff686b6613262778",
    "tray-timeline/events.csv": "7d2ed2d8e04a350264a3ede7bb698a25ed6ac3c3f07ef87baa10a02bc4798c7e",
}


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.workspace = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def generate(self, name: str = "evidence") -> Path:
        result = self.cli(name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, f"Generated fixtures in {name}\n")
        self.assertEqual(result.stderr, "")
        return self.workspace / name

    def assert_output_error(self, result: subprocess.CompletedProcess[str]):
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("fixtures: could not generate output:", result.stderr)

    def test_successful_runs_reproduce_exact_inventory_and_bytes(self):
        first = snapshot(self.generate())
        second = snapshot(self.generate("another output"))
        self.assertEqual(first, second)
        digests = {name: sha256(data).hexdigest() for name, data in first.items()}
        self.assertEqual(digests, FIXTURE_DIGESTS)

    def test_archive_needs_digest_to_distinguish_valid_images(self):
        archive = self.generate() / "archive-intake"
        record = json.loads((archive / "intake.json").read_text(encoding="ascii"))
        candidates = {path.name: path.read_bytes() for path in archive.glob("bin-*")}
        self.assertEqual(record["expected_bytes"], 23)
        self.assertEqual({len(data) for data in candidates.values()}, {23})
        images = {name: data for name, data in candidates.items() if data.startswith(b"P5\n")}
        self.assertEqual(set(images), {"bin-027.txt", "bin-031.pgm"})
        matches = [
            name for name, data in candidates.items()
            if sha256(data).hexdigest() == record["sha256"]
        ]
        self.assertEqual(matches, ["bin-027.txt"])
        reference = images["bin-027.txt"]
        other = images["bin-031.pgm"]
        magic, dimensions, maximum, raster = reference.split(b"\n", 3)
        self.assertEqual((magic, dimensions, maximum), (b"P5", b"4 3", b"255"))
        self.assertEqual(len(raster), 4 * 3)
        self.assertEqual(reference[:-1], other[:-1])
        self.assertEqual((reference[-1], other[-1]), (255, 254))

    def test_timeline_filters_tray_and_excludes_interval_endpoint(self):
        path = self.generate() / "tray-timeline" / "events.csv"
        with path.open(encoding="ascii", newline="") as source:
            rows = {row["event_id"]: row for row in csv.DictReader(source)}

        def time_for(event_id, field="recorded_at"):
            return datetime.fromisoformat(rows[event_id][field]).astimezone(UTC)

        start = time_for("E101")
        end = time_for("E104")
        self.assertEqual(start.isoformat(), "2025-12-09T23:58:00+00:00")
        self.assertEqual(end.isoformat(), "2025-12-10T00:03:00+00:00")
        self.assertEqual(time_for("E105"), end)
        in_window = {event_id for event_id in rows if start < time_for(event_id) < end}
        self.assertEqual(in_window, {"E102", "E103"})
        same_tray = {event_id for event_id in in_window if rows[event_id]["tray"] == "07"}
        self.assertEqual(same_tray, {"E102"})
        self.assertEqual(bytes.fromhex(rows["E102"]["note_hex"]).decode("ascii"), "blue folder")
        self.assertLess(time_for("E104", "ingested_at"), time_for("E101", "ingested_at"))

    def test_help_does_not_create_output(self):
        result = self.cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("destination", result.stdout)
        self.assertEqual(list(self.workspace.iterdir()), [])

    def test_invalid_arguments_do_not_create_output(self):
        for args in ((), ("output", "extra"), ("--unknown", "output")):
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn("usage:", result.stderr)
                self.assertEqual(list(self.workspace.iterdir()), [])

    def test_missing_parent_is_not_created(self):
        self.assert_output_error(self.cli("missing/evidence"))
        self.assertEqual(list(self.workspace.iterdir()), [])

    def test_existing_file_is_not_overwritten(self):
        path = self.workspace / "evidence"
        path.write_bytes(b"keep this")
        self.assert_output_error(self.cli(path.name))
        self.assertEqual(path.read_bytes(), b"keep this")

    def test_existing_empty_directory_is_not_populated(self):
        path = self.workspace / "evidence"
        path.mkdir()
        self.assert_output_error(self.cli(path.name))
        self.assertEqual(list(path.iterdir()), [])

    def test_existing_evidence_is_not_regenerated(self):
        output = self.generate()
        (output / "tray-timeline" / "events.csv").write_bytes(b"local edits\n")
        before = snapshot(output)
        self.assert_output_error(self.cli(output.name))
        self.assertEqual(snapshot(output), before)

    def test_dangling_destination_symlink_is_not_followed(self):
        link = self.workspace / "evidence"
        target = self.workspace / "uncreated"
        try:
            link.symlink_to(target, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("Creating symlinks is not supported in this environment")
        self.assert_output_error(self.cli(link.name))
        self.assertTrue(link.is_symlink())
        self.assertFalse(target.exists())
