# Student report · Lab 03 cabinet scan batch

**Scope:** Synthetic [register](evidence/shelf-reconciliation/register.csv) and [scan export](evidence/shelf-reconciliation/scans.jsonl), recorded in the [package manifest](manifest.json).

**Method:** Joined records on the exact `(cabinet, slot)` pair and counted only `accepted` rows toward coverage. Scan IDs below refer to rows in the scan export. The register lists four locations and the batch has four accepted attempts, covering only two registered locations: `A/01` and `B/01`.

```text
No accepted scan: A 02 S03
No accepted scan: B 03 no attempt
Unexpected accepted scan: A 03 S05
Repeated accepted scans: A 01 S01 S02
```

`A/02` and `B/03` are register rows. `S03` records an unreadable attempt for `A/02`; the complete scan export has no row for `B/03`. `S05` cannot stand in for `B/03`: it reports cabinet `A`.

**Follow-up:** Request a rescan of `A/02` and `B/03` and ask the batch owner to reconcile `S05` against the register. Neither export establishes an empty shelf, a mis-shelved item, or the reason for a repeat scan.
