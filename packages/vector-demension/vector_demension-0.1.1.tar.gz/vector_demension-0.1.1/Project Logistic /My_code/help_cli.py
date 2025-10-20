from __future__ import annotations

import sys
from pathlib import Path


def find_testing_guide() -> Path | None:
    # 1) Next to this module (development install)
    here = Path(__file__).resolve().parent
    cand = here / "TESTING_GUIDE.md"
    if cand.exists():
        return cand

    # 2) Data-files location (installed via setuptools data-files)
    share = Path(sys.prefix) / "share" / "hyce" / "TESTING_GUIDE.md"
    if share.exists():
        return share

    # 3) Project layout relative path (when running from repo root)
    repo = Path.cwd() / "Project Logistic /My_code/TESTING_GUIDE.md"
    if repo.exists():
        return repo

    return None


def main() -> None:
    path = find_testing_guide()
    if not path:
        sys.stderr.write("Could not locate TESTING_GUIDE.md.\n")
        sys.exit(1)
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:  # pragma: no cover
        sys.stderr.write(f"Failed to read {path}: {e}\n")
        sys.exit(1)
    sys.stdout.write(text)


if __name__ == "__main__":
    main()

