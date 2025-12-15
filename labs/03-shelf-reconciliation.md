# 03 · Shelf reconciliation

The archive is reviewing a cabinet scan batch. Reconcile two exports in `evidence/shelf-reconciliation/`:

- `register.csv` lists expected `(cabinet, slot)` pairs, one row per location. Slot codes are strings: keep their leading zeros. A slot code alone is not unique across cabinets.
- `scans.jsonl` contains one JSON object per scan attempt. `id` identifies the attempt. An `accepted` result counts as a recorded observation of the pair; `unreadable` records an attempt only. Multiple attempts can report the same pair.

1. List the expected pairs with no accepted scan. Distinguish an unreadable attempt from no attempt in the batch, citing scan IDs where available.
2. List accepted pairs absent from the register and cite their scan IDs.
3. Identify any pair with multiple accepted attempts and cite both IDs. Explain why equal numbers of expected locations and accepted attempts don't prove coverage.

Report what the exports establish, without assuming why an exception happened or whether something was physically missing.

[Worked solution](../writeups/03-shelf-reconciliation.md) · [Project home](../README.md)
