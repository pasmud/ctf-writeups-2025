# CTF Writeups 2025 · Offline Forensics

Four original CTF-style forensics labs built around a fictional archive. Each has a short brief, deterministic evidence, and a worked solution you can reproduce using Python's standard library. Start with the briefs if you want to solve them yourself: the writeups and fixture source contain spoilers.

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
├── copy-comparison/
│   ├── delivery/reading.txt
│   ├── review/reading.txt
│   └── staging/
│       ├── reading.txt
│       └── renamed.log
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
| **04 · Copy comparison** | Which exports are exact copies, which only differ in line endings, and which disagree on content? | [Brief](labs/04-copy-comparison.md) · [Writeup](writeups/04-copy-comparison.md) |

The writeup commands use POSIX shell syntax and assume the default `evidence` path. No packages, network access, or external data are required.

## Choose one lab

```sh
python3 fixtures.py --list
python3 fixtures.py --lab 03 evidence
```

`--list` takes no destination and writes nothing to disk. Each output line gives the stable two-digit lab ID, title, and brief path relative to the repository, separated by tabs. `--lab ID` writes only that lab's evidence, with the same paths and bytes as in a full run; the example creates just `evidence/shelf-reconciliation/`. The choice is optional: `python3 fixtures.py evidence` still generates every lab.

## Generator contract

- Generation accepts one output path. Its parent must already exist. Pick a **new** path for a rerun; the generator never overwrites an existing destination, including an empty directory or symlink.
- Successful runs produce identical relative paths and file bytes. Filesystem metadata such as modification times is outside that guarantee.
- Usage errors exit with status `2`; filesystem errors exit with status `1` and a diagnostic on standard error. A write failure after creating the destination can leave partial output. Treat it as incomplete and retry at a new path.

## Evidence integrity

After generating the evidence, record a baseline before examining or copying it:

```sh
python3 manifest.py create evidence evidence-manifest.json
python3 fixtures.py evidence-copy
python3 manifest.py verify evidence-copy evidence-manifest.json
```

The manifest is a deterministic JSON object mapping sorted, root-relative `/`-separated file paths to lowercase SHA-256 digests. Keep it outside the evidence directory; creation requires at least one evidence file and a new manifest path, and never overwrites an existing entry. A write failure may leave an incomplete manifest; retry with a new path. Verification checks the entire regular-file inventory and reports missing, unexpected, and changed files. Empty directories and filesystem metadata are not recorded. Successful commands exit `0`, invalid CLI syntax exits `2`, and mismatches or input/filesystem errors exit `1`.

Use the tool on stable local lab directories. It rejects symlinks and other non-regular entries in the evidence tree; the root itself cannot be a symlink. It doesn't protect against concurrent directory edits. Keep a trusted copy of the manifest: matching hashes show consistency with that baseline, not provenance or who handled the files.

## Verification

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

The offline tests cover the fixture bytes, the conclusions supported by the evidence, and CLI failure cases. CI runs the same Python test suite on 3.11 and 3.14.

## Limits

The fixtures contain only inert, invented data. The image exercise checks a known, simple PGM header and raster rather than implementing a general file parser. A checksum comparison assumes the intake record is trusted. The timeline describes what the records report; clock accuracy, delivery delays, and the identity or intent of any actor are not established by the data.

[MIT License](LICENSE)
