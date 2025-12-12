# 01 · Archive intake

Three files from a fictional archive intake were copied into `evidence/archive-intake/` under unreliable names. `intake.json` is the trusted reference for this exercise. It records the reference object's length in bytes and SHA-256 digest, but no filename.

Inspect the three `bin-*` files as bytes. Keep the evidence unchanged and write a short finding that answers:

1. Which file matches the intake record? Report the byte length and digest.
2. What file format, width, height, and maximum sample value does the matching file declare? Does the number of raster bytes agree with those fields for this file?
3. Why aren't the filename extension, length, or format signature sufficient on their own? Which candidate demonstrates why format alone isn't enough?

**Hint:** Compare lengths and the first few bytes before hashing the complete files. Binary PGM starts with `P5`; for these specific files the header contains three newline-terminated lines with no comments.

[Worked solution](../writeups/01-archive-intake.md) · [Project home](../README.md)
