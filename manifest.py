"""Create or verify a SHA-256 inventory of a synthetic evidence directory."""

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path


def valid_path(name: str) -> bool:
    return (
        not any(char in name for char in "\\:\0")
        and all(part not in {"", ".", ".."} for part in name.split("/"))
    )


def inventory(root: Path) -> dict[str, str]:
    entries = {}
    pending = [root]
    while pending:
        for path in pending.pop().iterdir():
            name = path.relative_to(root).as_posix()
            if not valid_path(name):
                raise ValueError(f"unsupported evidence path: {name!r}")
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                pending.append(path)
            elif stat.S_ISREG(mode):
                with path.open("rb") as source:
                    entries[name] = hashlib.file_digest(source, "sha256").hexdigest()
            else:
                raise ValueError(f"not a regular file or directory: {name!r}")
    return entries


def unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for name, digest in pairs:
        if name in result:
            raise ValueError(f"duplicate manifest path: {name!r}")
        result[name] = digest
    return result


def read_manifest(path: Path) -> dict[str, str]:
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("manifest must be a regular file")
    entries = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    if not isinstance(entries, dict) or not entries:
        raise ValueError("manifest must be a nonempty object of paths and SHA-256 digests")
    for name, digest in entries.items():
        if not valid_path(name):
            raise ValueError(f"invalid manifest path: {name!r}")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"invalid SHA-256 digest for {name!r}")
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("create", "verify"))
    parser.add_argument("root", type=Path, help="existing synthetic evidence directory")
    parser.add_argument("manifest", type=Path, help="JSON manifest outside the evidence directory")
    args = parser.parse_args()
    root, manifest = args.root, args.manifest
    try:
        if not stat.S_ISDIR(root.lstat().st_mode):
            raise ValueError("evidence root must be a directory, not a symlink")
        if Path(os.path.realpath(manifest.parent)).is_relative_to(root.resolve()):
            raise ValueError("manifest must be outside the evidence directory")
        if args.operation == "create":
            entries = inventory(root)
            if not entries:
                raise ValueError("evidence directory contains no regular files")
            data = json.dumps(entries, indent=2, sort_keys=True) + "\n"
            with manifest.open("xb") as output:
                output.write(data.encode("ascii"))
            print(f"Recorded {len(entries)} files in {manifest}")
        else:
            expected = read_manifest(manifest)
            actual = inventory(root)
            changed = {
                name for name in expected.keys() & actual.keys() if expected[name] != actual[name]
            }
            differences = [
                (label, name)
                for label, names in (
                    ("missing", expected.keys() - actual.keys()),
                    ("unexpected", actual.keys() - expected.keys()),
                    ("changed", changed),
                )
                for name in sorted(names)
            ]
            if differences:
                for label, name in differences:
                    print(f"manifest: {label}: {name!r}", file=sys.stderr)
                return 1
            print(f"Verified {len(expected)} files")
    except (OSError, ValueError) as error:
        print(f"manifest: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
