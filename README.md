# CTF Writeups 2025 · Offline Forensics

Three original CTF-style forensics labs built around a fictional archive. Each has a short brief, deterministic evidence, and a worked solution you can reproduce using Python's standard library. Start with the briefs if you want to solve them yourself: the writeups and fixture source contain spoilers.

These are synthetic portfolio exercises, not records of competition participation. The December 2025 commit timeline is illustrative and does not document activity on those dates.

## Quickstart

From the repository root, with Python 3.11 or newer:

```sh
python3 fixtures.py --help
python3 fixtures.py evidence
```

The second command prints `Generated fixtures in evidence` and creates this tree:

```text
evidence/
├── archive-intake/
│   ├── bin-014.dat
│   ├── bin-027.txt
│   ├── bin-031.pgm
│   └── intake.json
├── shelf-reconciliation/
│   ├── register.csv
│   └── scans.jsonl
└── tray-timeline/
    └── events.csv
```

For a quick look at one artifact without opening it in an application:

```sh
python3 -c "from pathlib import Path; print(Path('evidence/archive-intake/bin-031.pgm').read_bytes()[:3])"
```

This prints `b'P5\n'`. That identifies a likely format, but it's only a first clue.

| Lab | Question | Exercise and solution |
| --- | --- | --- |
| **01 · Archive intake** | Which of three equally sized files matches the reference, and what format is it really? | [Brief](labs/01-archive-intake.md) · [Writeup](writeups/01-archive-intake.md) |
| **02 · Tray timeline** | Which event falls strictly inside the recorded open interval? What do the log and its hex note actually establish? | [Brief](labs/02-tray-timeline.md) · [Writeup](writeups/02-tray-timeline.md) |
| **03 · Shelf reconciliation** | Which expected locations lack an accepted scan, and which scan records should be reviewed? | [Brief](labs/03-shelf-reconciliation.md) · [Writeup](writeups/03-shelf-reconciliation.md) |

The writeup commands use POSIX shell syntax and assume the default `evidence` path. No packages, network access, or external data are required.

## Generator contract

- `python3 fixtures.py DESTINATION` accepts one output path. Its parent must already exist. Pick a **new** path for a rerun; the generator never overwrites an existing destination, including an empty directory or symlink.
- Successful runs produce identical relative paths and file bytes. Filesystem metadata such as modification times is outside that guarantee.
- Usage errors exit with status `2`; filesystem errors exit with status `1` and a diagnostic on standard error. A write failure after creating the destination can leave partial output. Treat it as incomplete and retry at a new path.

## Verification

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

The offline tests cover the fixture bytes, the conclusions supported by the evidence, and CLI failure cases. CI runs the same Python test suite on 3.11 and 3.14.

## Limits

The fixtures contain only inert, invented data. The image exercise checks a known, simple PGM header and raster rather than implementing a general file parser. A checksum comparison assumes the intake record is trusted. The timeline describes what the records report; clock accuracy, delivery delays, and the identity or intent of any actor are not established by the data.

[MIT License](LICENSE)
