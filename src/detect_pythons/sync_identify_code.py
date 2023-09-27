# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import pathlib
import sys

FILES_NOT_MODIFIED = 0
FILES_MODIFIED = 1

IDENTIFY_PY = (pathlib.Path(__file__).parent / "identify.py").resolve()
DETECTOR_SH = (pathlib.Path(__file__).parent / "detector.sh").resolve()


def sync(path: pathlib.Path) -> int:
    # Verify the paths are acceptable.
    if path != IDENTIFY_PY:
        print(f"{path} is not an acceptable file path.")
        return FILES_NOT_MODIFIED

    code = path.read_text().strip()
    # Strip leading comments.
    while code.startswith("#"):
        code = code[code.find("\n") + 1 :].lstrip()

    # Determine the text boundaries of the source code in 'action.yml'.
    sh = DETECTOR_SH.read_text()
    tag = f"{IDENTIFY_PY.name}_SOURCE_CODE"
    start = sh.find("\n", sh.find(tag)) + 1
    end = sh.rfind("\n", start, sh.find(tag, start))

    # Inject the source code and determine if 'action.yml' needs to be overwritten.
    new_sh = sh[:start] + code + sh[end:]
    if new_sh != sh:
        DETECTOR_SH.write_text(new_sh, newline="\n")
        return FILES_MODIFIED

    return FILES_NOT_MODIFIED


def main():
    if len(sys.argv) < 2:
        print(f"The path to a modified '{IDENTIFY_PY.name}' must be provided.")
        sys.exit(FILES_NOT_MODIFIED)

    rc = sync(pathlib.Path(sys.argv[-1]).resolve())
    sys.exit(rc)


if __name__ == "__main__":
    main()
