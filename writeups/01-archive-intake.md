# 01 · Archive intake — worked solution

**Finding:** `bin-027.txt` matches intake record `INT-042`. It is a 23-byte binary PGM image, 4 pixels wide by 3 pixels high, with a maximum sample value of 255. The `.txt` extension is misleading.

## Compare the full candidate bytes

From the repository root after generating `evidence`, read the reference record, then compare the candidates' byte counts, leading bytes, and SHA-256 digests:

```sh
python3 - <<'PY'
from hashlib import sha256
import json
from pathlib import Path

root = Path("evidence/archive-intake")
record = json.loads((root / "intake.json").read_text(encoding="ascii"))
matches = []
for path in sorted(root.glob("bin-*")):
    data = path.read_bytes()
    digest = sha256(data).hexdigest()
    match = len(data) == record["expected_bytes"] and digest == record["sha256"]
    print(path.name, len(data), repr(data[:3]), digest[:12], match)
    if match:
        matches.append((path, data, digest))

if len(matches) != 1:
    raise SystemExit(f"Expected one matching candidate, found {len(matches)}")
path, data, digest = matches[0]
print(f"SHA-256 for {path.name}: {digest}")

# The exercise uses a simple three-line PGM header with no comments.
magic, dimensions, maximum, raster = data.split(b"\n", 3)
width, height = map(int, dimensions.split())
maximum = int(maximum)
print(magic.decode("ascii"), f"{width}x{height}", f"max={maximum}",
      f"raster={len(raster)} bytes (expected {width * height} at one byte per sample)")
PY
```

Output (the candidate table displays only the first 12 hex digits; the comparison uses the full digests):

```text
bin-014.dat 23 b'Sca' d8500a6a3657 False
bin-027.txt 23 b'P5\n' 7277064ede23 True
bin-031.pgm 23 b'P5\n' fb19bbe5e1d1 False
SHA-256 for bin-027.txt: 7277064ede230053f982c9e0ebf4056d1452cbf179ba0b77fbd161647e59ffc0
P5 4x3 max=255 raster=12 bytes (expected 12 at one byte per sample)
```

## Interpret the result

All three candidates have the right length. Two even share the same PGM header, but the last raster sample is `255` in `bin-027.txt` and `254` in `bin-031.pgm`. Both values are valid for the format. Only one complete file matches the trusted digest.

For this PGM, each of the `4 × 3` pixels occupies one byte because the maximum sample value is 255. The raster has exactly 12 bytes after the three-line header. Splitting at most three times matters: a newline byte in pixel data would be a sample, not a header delimiter. This shortcut is specific to the fixture, not a general PGM validator.

The matching digest supports byte-for-byte identification against the reference. It doesn't independently establish who supplied the file or whether the intake record itself is authentic.

[Exercise brief](../labs/01-archive-intake.md) · [Project home](../README.md)
