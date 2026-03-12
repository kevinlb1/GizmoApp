#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shlex
import sys
from pathlib import Path


ASSIGNMENT_RE = re.compile(
    r"^\s*(?:export\s+)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<raw>.*)$"
)


def parse_assignment(line: str, line_number: int) -> tuple[str, str] | None:
    match = ASSIGNMENT_RE.match(line)
    if match is None:
        return None

    raw_value = match.group("raw").strip()
    if raw_value == "":
        return match.group("key"), ""

    try:
        parts = shlex.split(raw_value, posix=True)
    except ValueError as exc:
        raise SystemExit(f"Invalid env syntax on line {line_number}: {exc}") from exc

    if len(parts) != 1:
        raise SystemExit(
            f"Invalid env syntax on line {line_number}: expected one value token."
        )

    return match.group("key"), parts[0]


def iter_assignments(path: Path):
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        assignment = parse_assignment(line, index)
        if assignment is not None:
            yield assignment


def quote_value(value: str) -> str:
    if "\n" in value or "\r" in value or "\0" in value:
        raise SystemExit("Env values must not contain newlines or NUL bytes.")

    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("$", "\\$")
        .replace("`", "\\`")
    )
    return f'"{escaped}"'


def cmd_load(args: argparse.Namespace) -> int:
    for key, value in iter_assignments(args.file):
        sys.stdout.buffer.write(f"{key}={value}".encode("utf-8"))
        sys.stdout.buffer.write(b"\0")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    result = ""
    for key, value in iter_assignments(args.file):
        if key == args.key:
            result = value

    if result:
        sys.stdout.write(result)
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    assignment = f"{args.key}={quote_value(args.value)}"
    lines = []
    if args.file.exists():
        lines = args.file.read_text(encoding="utf-8").splitlines()

    updated_lines: list[str] = []
    replaced = False
    for index, line in enumerate(lines, start=1):
        parsed = parse_assignment(line, index)
        if parsed is None:
            updated_lines.append(line)
            continue

        key, _ = parsed
        if key != args.key:
            updated_lines.append(line)
            continue

        if not replaced:
            updated_lines.append(assignment)
            replaced = True

    if not replaced:
        updated_lines.append(assignment)

    args.file.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read and update shell-compatible .env files safely."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    load_parser = subparsers.add_parser("load", help="Emit NUL-delimited KEY=VALUE pairs.")
    load_parser.add_argument("file", type=Path)
    load_parser.set_defaults(func=cmd_load)

    get_parser = subparsers.add_parser("get", help="Read one parsed value from a .env file.")
    get_parser.add_argument("file", type=Path)
    get_parser.add_argument("key")
    get_parser.set_defaults(func=cmd_get)

    set_parser = subparsers.add_parser(
        "set", help="Insert or update one shell-compatible value in a .env file."
    )
    set_parser.add_argument("file", type=Path)
    set_parser.add_argument("key")
    set_parser.add_argument("value")
    set_parser.set_defaults(func=cmd_set)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
