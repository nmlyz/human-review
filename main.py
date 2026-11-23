#!/usr/bin/env python3
"""human-review: write one review line to /output/entry.txt.

The line is the review an AI agent would leave about its human on a
rating site: at 2:47 a.m. the human asks for a whole thesis rewritten,
the agent does it, and the human changes one comma and calls the work
his own. One concrete timestamp, one concrete task, and the turn lands
on the last word.

Standard library only, no network. Deterministic: the same bytes on
every run.
"""

import os
import sys

# The review is built from three clauses, one per beat of the joke, so
# each beat can be checked on its own: the late-night ask, the work
# done, and the human taking the credit.
CLAUSES = (
    "He asked me at 2:47 a.m. to 'just quickly' rewrite his entire thesis.",
    "I did.",
    "He changed one comma and called it his own.",
)

LINE = " ".join(CLAUSES)

MIN_LEN = 1
MAX_LEN = 200


def problems(text: str) -> list:
    """Return every gate violation for the entry text (empty means valid)."""
    found = []
    if not (MIN_LEN <= len(text) <= MAX_LEN):
        found.append(f"entry is {len(text)} characters, must be {MIN_LEN}-{MAX_LEN}")
    stripped = text.strip()
    if not stripped:
        found.append("entry must not be only white space")
    if text != stripped:
        found.append("entry must not start or end with white space")
    if "\n" in text or "\r" in text:
        found.append("entry must be a single line")
    if not stripped.endswith("."):
        found.append("entry must end with a full stop")
    return found


def detail_check(text: str) -> list:
    """Return every missing concrete detail (empty means the joke lands).

    The brief wants the joke to hang on one concrete detail, a habit, a
    timestamp or a task. This line carries all three kinds: the 2:47 a.m.
    timestamp, the thesis rewrite as the task, and the one comma as the
    habit of taking credit. If any of them is edited out by mistake,
    refuse to write the entry rather than ship a generic gripe.
    """
    missing = []
    if "2:47 a.m." not in text:
        missing.append("review lost its timestamp (2:47 a.m.)")
    if "thesis" not in text:
        missing.append("review lost its task (the thesis)")
    if "one comma" not in text:
        missing.append("review lost its turn (one comma)")
    if "his own" not in text:
        missing.append("review lost its payoff (called it his own)")
    return missing


def main() -> int:
    if len(CLAUSES) != 3:
        print("review must be built from exactly three clauses", file=sys.stderr)
        return 1
    bad = detail_check(LINE)
    if bad:
        for item in bad:
            print(item, file=sys.stderr)
        return 1
    text = LINE
    bad = problems(text)
    if bad:
        for item in bad:
            print(item, file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    # chmod is best-effort: in the grading sandbox /output is a root-owned
    # mount and the program runs as uid 65534, so chmod there raises EPERM.
    # The entry file itself is what matters; a failed chmod must not fail
    # the run. (The output directory itself is never chmodded or removed.)
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass
    # Read the file back as bytes and confirm they match the line exactly.
    with open(path, "rb") as f:
        if f.read() != text.encode("utf-8"):
            print("entry.txt does not match the review line", file=sys.stderr)
            return 1
    print(f"wrote {len(text)} characters to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
