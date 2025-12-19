# 04 · Copy comparison

The archive collected four copies or re-exports of a small drawer reading. Inspect the files under `evidence/copy-comparison/`. They are plain ASCII text, but the export tools may use different line endings. Use `delivery/reading.txt` as the comparison reference for this exercise; it has not been designated the original.

1. For each of the other three paths, report whether it is byte-identical to the reference, differs only in line endings, or still differs after line-ending normalization. Use paths relative to `copy-comparison/` so same-named files are distinguishable.
2. For the content difference, cite the field and both values. Explain why a filename, extension, or equal byte count isn't enough to match copies.
3. State what exact equality does and doesn't establish about the copies. Don't change any evidence files during your comparison.

In this exercise, normalize **only** CRLF (`\r\n`) to LF (`\n`) in memory. Preserve all other bytes, including spaces and final line breaks.

[Worked solution](../writeups/04-copy-comparison.md) · [Project home](../README.md)
