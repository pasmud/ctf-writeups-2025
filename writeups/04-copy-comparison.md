# 04 · Copy comparison — worked solution

Compare raw bytes first. Normalize CRLF to LF only if the raw bytes differ. Reading as text with Python's default newline handling can hide the very change you're investigating.

From the repository root after generating `evidence`:

```sh
python3 - <<'PY'
from pathlib import Path

root = Path("evidence/copy-comparison")
reference = root / "delivery/reading.txt"
baseline = reference.read_bytes()

def normalize(data):
    return data.replace(b"\r\n", b"\n")

def fields(data):
    return dict(line.split("=", 1) for line in normalize(data).decode("ascii").splitlines())

for path in sorted(root.glob("*/*")):
    if path == reference:
        continue
    data = path.read_bytes()
    if data == baseline:
        relation = "byte-identical"
    elif normalize(data) == normalize(baseline):
        relation = "line endings only"
    else:
        relation = "different content"
    print(f"{path.relative_to(root).as_posix()} ({len(data)} bytes): {relation}")
    if relation == "different content":
        before, after = fields(baseline), fields(data)
        for field in sorted(before.keys() | after.keys()):
            if before.get(field) != after.get(field):
                print(f"  {field}: {before.get(field)!r} -> {after.get(field)!r}")
PY
```

```text
review/reading.txt (30 bytes): line endings only
staging/reading.txt (28 bytes): different content
  label: 'blue folder' -> 'gray folder'
staging/renamed.log (28 bytes): byte-identical
```

The reference is 28 bytes. The review copy has a carriage return before each of its two line feeds, adding two bytes. The staging `reading.txt` has the same name and length as the reference, but its label differs. The file with a different name and extension is the exact match. That establishes byte equality for those two files; it does not identify an original, a copy direction, or which label is accurate.

[Exercise brief](../labs/04-copy-comparison.md) · [Project home](../README.md)
