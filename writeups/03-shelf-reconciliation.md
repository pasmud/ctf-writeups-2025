# 03 · Shelf reconciliation — worked solution

Use `(cabinet, slot)` as the join key. Group accepted scans by that key, but retain the attempt IDs so each exception can be traced to its source row.

From the repository root after generating `evidence`:

```sh
python3 - <<'PY'
import csv
import json
from collections import defaultdict
from pathlib import Path

root = Path("evidence/shelf-reconciliation")

def location(row):
    return row["cabinet"], row["slot"]

with (root / "register.csv").open(encoding="ascii", newline="") as source:
    expected = {location(row) for row in csv.DictReader(source)}

accepted = defaultdict(list)
unreadable = defaultdict(list)
with (root / "scans.jsonl").open(encoding="ascii") as source:
    for line in source:
        row = json.loads(line)
        groups = {"accepted": accepted, "unreadable": unreadable}
        groups[row["result"]][location(row)].append(row["id"])

for pair in sorted(expected - accepted.keys()):
    print("No accepted scan:", *pair, *(unreadable.get(pair) or ["no attempt"]))
for pair in sorted(accepted.keys() - expected):
    print("Unexpected accepted scan:", *pair, *accepted[pair])
for pair, ids in sorted(accepted.items()):
    if len(ids) > 1:
        print("Repeated accepted scans:", *pair, *ids)
PY
```

```text
No accepted scan: A 02 S03
No accepted scan: B 03 no attempt
Unexpected accepted scan: A 03 S05
Repeated accepted scans: A 01 S01 S02
```

There are four expected locations and four accepted attempts, but those attempts cover only two expected locations (`A/01` and `B/01`). `S05` doesn't cover `B/03` just because both have slot code `03`. `S03` establishes that a scan of `A/02` was attempted and marked unreadable; the export records no attempt for `B/03`. Neither result establishes that the location was empty. Similarly, the repeated `A/01` records don't establish why it was scanned twice.

[Exercise brief](../labs/03-shelf-reconciliation.md) · [Project home](../README.md)
