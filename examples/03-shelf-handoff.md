# Student-to-reviewer handoff · Lab 03

**Case:** Cabinet scan batch, synthetic training evidence. See the [exercise brief](../labs/03-shelf-reconciliation.md) for field definitions. The submitted package pairs the [completed student report](03-shelf-handoff-report.md) with the two source exports and their SHA-256 manifest. The report's links refer to paths in the finished package.

## Student: prepare the package

From the repository root, use a new `handoff-03` directory. Record the manifest before inspecting the evidence. The final command copies this completed example report into the package.

```sh
mkdir handoff-03 &&
python3 fixtures.py --lab 03 handoff-03/evidence &&
python3 manifest.py create handoff-03/evidence handoff-03/manifest.json &&
cp examples/03-shelf-handoff-report.md handoff-03/report.md
```

## Reviewer: verify, then reproduce

Use the received package, represented here by `handoff-03`. From the repository root, copy it into a new `review-03` directory for examination. In this example the [repository baseline](03-shelf-handoff-manifest.json) is the reviewer's independently held copy of the expected manifest. Compare it with the submitted manifest before verifying the received evidence:

```sh
mkdir review-03 &&
cp -R handoff-03/. review-03/ &&
cmp examples/03-shelf-handoff-manifest.json review-03/manifest.json &&
python3 manifest.py verify review-03/evidence review-03/manifest.json
```

Expect `Verified 2 files`. If either check fails, stop the findings review and record the discrepancy before requesting a fresh transfer. Do not create a replacement manifest from the received evidence to make the check pass. A match establishes consistency with the expected synthetic evidence, not custody or authorship of the report.

From inside `review-03`, run the Python block in the [worked solution](../writeups/03-shelf-reconciliation.md). Its paths now point to the verified copy. Compare its four finding lines with `report.md` and confirm that every cited scan ID resolves to the stated cabinet, slot, and result. An example reviewer disposition is: **Both artifacts verified; all four findings reproduced. Physical inventory status remains unverified.**
