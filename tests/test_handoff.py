import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GUIDE = REPO / "examples/03-shelf-handoff.md"
REPORT = REPO / "examples/03-shelf-handoff-report.md"
BASELINE = REPO / "examples/03-shelf-handoff-manifest.json"
WRITEUP = REPO / "writeups/03-shelf-reconciliation.md"


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.workspace = Path(self.enterContext(tempfile.TemporaryDirectory()))
        package = self.workspace / "handoff-03"
        package.mkdir()
        self.run_python(REPO / "fixtures.py", "--lab", "03", "evidence", cwd=package)
        self.run_python(REPO / "manifest.py", "create", "evidence", "manifest.json", cwd=package)
        shutil.copyfile(REPORT, package / "report.md")
        self.received = self.workspace / "review-03"
        shutil.copytree(package, self.received)

    def run_python(self, *args, cwd):
        result = subprocess.run(
            [sys.executable, *args], cwd=cwd, capture_output=True, text=True,
            timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def test_received_evidence_verifies_against_the_pinned_baseline(self):
        self.assertEqual((self.received / "manifest.json").read_bytes(), BASELINE.read_bytes())
        output = self.run_python(
            REPO / "manifest.py", "verify", "evidence", "manifest.json", cwd=self.received,
        )
        self.assertEqual(output, "Verified 2 files\n")

    def check_links(self, doc, expected):
        content = doc.read_text(encoding="utf-8")
        links = {(doc.parent / link).resolve() for link in re.findall(r"\]\(([^)]+)\)", content)}
        self.assertEqual(links, {path.resolve() for path in expected})
        for link in links:
            self.assertTrue(link.is_file(), link)
        return content

    def test_report_links_resolve_and_findings_match_the_replayed_solution(self):
        self.check_links(GUIDE, {REPO / "labs/03-shelf-reconciliation.md", BASELINE, REPORT, WRITEUP})
        report = self.check_links(self.received / "report.md", {
            self.received / "evidence/shelf-reconciliation/register.csv",
            self.received / "evidence/shelf-reconciliation/scans.jsonl",
            self.received / "manifest.json",
        })
        writeup = WRITEUP.read_text(encoding="utf-8")
        code = writeup.split("python3 - <<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
        stated_findings = report.split("```text\n", 1)[1].split("```", 1)[0]
        self.assertEqual(self.run_python("-c", code, cwd=self.received), stated_findings)
