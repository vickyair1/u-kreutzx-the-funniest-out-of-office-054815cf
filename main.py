#!/usr/bin/env python3
"""Write the funniest out-of-office line to the entry file.

This program produces exactly one artifact: a plain-text file holding a
single line of an out-of-office auto-reply, the funniest it can be in 140
characters or fewer. The line is a fixed constant below; nothing in this
program is generated, sampled, or fetched, so the output is byte-identical
on every run.

The joke is the loop: the human is away until Monday, and the email they
would forward it to is forwarded to an inbox that is also away until
Monday. One line, no second line, no link, no image — just the auto-reply
itself, in the voice of an out-of-office message. It is 116 characters,
inside the 140-character gate.

Why the output directory is configurable: the competition harness runs the
entry with a mounted output directory, while a local run may point at a
different one. The MAKEFUN_OUTPUT_DIR environment variable selects the
directory; when it is unset or empty the program falls back to "/output",
the directory the harness mounts. The rest of the program — the line
itself, the encoding, the newline behaviour, the stdout echo — is fixed
and validated before anything is written, so a bad configuration fails
loudly instead of silently producing a wrong file.

Deterministic, stdlib only: no network, no randomness, no time.
"""

import os
import sys

LINE = "I'm out of office until Monday. Your email has been forwarded to my inbox, which is also out of office until Monday."

MAX_CHARS = 140
DEFAULT_OUTPUT_DIR = "/output"
OUTPUT_FILENAME = "entry.txt"


def configured_output_dir():
    """Return the MAKEFUN_OUTPUT_DIR value, or "" when it is unset/empty.

    Kept apart from resolve_output_dir so the environment lookup can be
    tested on its own: an empty string means "no configuration", and the
    caller decides the fallback. Whitespace-only values count as empty.
    """
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()


def resolve_output_dir():
    """Return the directory the entry file must be written to.

    MAKEFUN_OUTPUT_DIR wins when set to a non-empty value; otherwise the
    default "/output" is used. A relative path is resolved against the
    current working directory, so both absolute harness paths and local
    relative paths work.
    """
    configured = configured_output_dir()
    chosen = configured if configured else DEFAULT_OUTPUT_DIR
    return os.path.abspath(chosen)


def entry_path():
    """Return the full path of the entry file."""
    return os.path.join(resolve_output_dir(), OUTPUT_FILENAME)


def validate_line():
    """Sanity-check the line before writing it anywhere.

    The line must be a single line of non-whitespace text within the
    140-character gate: no embedded newline, no leading/trailing
    whitespace, and non-empty. Any violation is a bug in this program,
    so fail loudly on stderr and exit non-zero.
    """
    if not LINE:
        print("error: entry line is empty", file=sys.stderr)
        raise SystemExit(1)
    if LINE != LINE.strip() or "\n" in LINE or "\r" in LINE:
        print("error: entry line must be a single clean line", file=sys.stderr)
        raise SystemExit(1)
    if len(LINE) > MAX_CHARS:
        print("error: entry line exceeds the 140-character gate", file=sys.stderr)
        raise SystemExit(1)


def line_stats():
    """Return the entry line's character and byte counts.

    The gate counts characters, not bytes, so both are reported: the
    character count is what the gate checks, the byte count is what the
    file holds.
    """
    return len(LINE), len(LINE.encode("utf-8"))


def write_entry(path):
    """Write the line to the entry file at the given path.

    The parent directory is created if missing, and the file is written
    as UTF-8 with no trailing newline, so the file holds exactly the
    line's bytes and nothing else.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(LINE)


def main():
    """Validate the line, write it to the entry file, and echo it.

    The directory is created if missing, the file is written as UTF-8
    with no trailing newline (the line is exactly 116 characters, and the
    file must hold exactly those bytes), and the same line is printed to
    stdout so the harness log shows what was written.
    """
    validate_line()
    if "--print" in sys.argv[1:]:
        print(LINE)
        return
    path = entry_path()
    write_entry(path)
    chars, nbytes = line_stats()
    print(f"entry: {chars} characters, {nbytes} bytes", file=sys.stderr)
    print(LINE)


if __name__ == "__main__":
    main()
