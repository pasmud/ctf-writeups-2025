import json
import subprocess
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.workspace = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(REPO / script), *args], cwd=self.workspace,
            capture_output=True, text=True, timeout=10, check=False,
        )

    def checked(self, script, *args):
        result = self.cli(script, *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def test_manifest_reproduces_and_verifies_across_generated_roots(self):
        first = self.workspace / "baseline.json"
        second = self.workspace / "copy.json"
        self.checked("fixtures.py", "evidence")
        self.checked("fixtures.py", "evidence copy")
        self.checked("manifest.py", "create", "evidence", first.name)
        self.checked("manifest.py", "create", "evidence copy", second.name)
        self.assertEqual(first.read_bytes(), second.read_bytes())

        entries = json.loads(first.read_text(encoding="ascii"))
        files = [p for p in (self.workspace / "evidence").glob("*/*") if p.is_file()]
        self.assertEqual(list(entries), sorted(f"{p.parent.name}/{p.name}" for p in files))
        self.assertEqual(entries["tray-timeline/events.csv"],
                         sha256((self.workspace / "evidence/tray-timeline/events.csv")
                                .read_bytes()).hexdigest())
        self.assertEqual(self.checked("manifest.py", "verify", "evidence copy", first.name),
                         f"Verified {len(files)} files\n")

    def test_verify_reports_changed_missing_and_unexpected_files(self):
        self.checked("fixtures.py", "evidence")
        self.checked("manifest.py", "create", "evidence", "baseline.json")
        root = self.workspace / "evidence"
        (root / "shelf-reconciliation/register.csv").unlink()
        (root / "tray-timeline/events.csv").write_bytes(b"different bytes\n")
        (root / "extra note.txt").write_bytes(b"additional evidence\n")

        result = self.cli("manifest.py", "verify", "evidence", "baseline.json")
        self.assertEqual((result.returncode, result.stdout), (1, ""))
        self.assertEqual(result.stderr.splitlines(), [
            "manifest: missing: 'shelf-reconciliation/register.csv'",
            "manifest: unexpected: 'extra note.txt'",
            "manifest: changed: 'tray-timeline/events.csv'",
        ])

    def test_create_does_not_replace_existing_manifest_or_write_inside_root(self):
        self.checked("fixtures.py", "evidence")
        existing = self.workspace / "baseline.json"
        existing.write_bytes(b"previous inventory")
        result = self.cli("manifest.py", "create", "evidence", existing.name)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(existing.read_bytes(), b"previous inventory")

        result = self.cli("manifest.py", "create", "evidence", "evidence/baseline.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("outside the evidence directory", result.stderr)
        self.assertFalse((self.workspace / "evidence/baseline.json").exists())

    def test_verify_rejects_invalid_manifests(self):
        self.checked("fixtures.py", "evidence")
        digest = "0" * 64
        manifest = self.workspace / "baseline.json"
        for content, diagnostic in (
            ("{", "Expecting property name"),
            ("{}", "nonempty object"),
            (f'{{"../outside.txt":"{digest}"}}', "invalid manifest path"),
            ('{"file":"bad"}', "invalid SHA-256 digest"),
            (f'{{"file":"{digest}","file":"{digest}"}}', "duplicate manifest path"),
        ):
            with self.subTest(content=content):
                manifest.write_text(content, encoding="ascii")
                result = self.cli("manifest.py", "verify", "evidence", manifest.name)
                self.assertEqual((result.returncode, result.stdout), (1, ""))
                self.assertIn(diagnostic, result.stderr)

    def test_rejects_symlinks_in_evidence_or_as_root(self):
        self.checked("fixtures.py", "evidence")
        root = self.workspace / "evidence"
        self.checked("manifest.py", "create", "evidence", "baseline.json")
        alias = self.workspace / "alias"
        try:
            alias.symlink_to(root, target_is_directory=True)
            (root / "alias").symlink_to(alias, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("Creating symlinks is not supported in this environment")

        result = self.cli("manifest.py", "create", "alias", "alias.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("evidence root must be a directory", result.stderr)
        result = self.cli("manifest.py", "verify", "evidence", "baseline.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a regular file or directory: 'alias'", result.stderr)
        result = self.cli("manifest.py", "create", "evidence", "alias/inside.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("outside the evidence directory", result.stderr)
        self.assertFalse((root / "inside.json").exists())
