from __future__ import annotations

import sys
from importlib.resources import files


def main() -> None:
    try:
        data = files(__package__).joinpath("TESTING_GUIDE.md").read_text(encoding="utf-8")
    except Exception as e:  # pragma: no cover
        sys.stderr.write(f"Failed to load TESTING_GUIDE.md from package: {e}\n")
        sys.exit(1)
    sys.stdout.write(data)


if __name__ == "__main__":
    main()

