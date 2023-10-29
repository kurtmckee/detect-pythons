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


def main() -> int:
    code = IDENTIFY_PY.read_text().strip()
    # Strip leading comments.
    while code.startswith("#"):
        code = code[code.find("\n") + 1 :].lstrip()

    # Determine the text boundaries of the source code in 'detector.sh'.
    sh = DETECTOR_SH.read_text()
    tag = "identify.py_SOURCE_CODE"
    start = sh.find("\n", sh.find(tag)) + 1
    end = sh.rfind("\n", start, sh.find(tag, start))

    # Inject the source code and determine if 'detector.sh' needs to be overwritten.
    new_sh = sh[:start] + code + sh[end:]
    if new_sh != sh:
        DETECTOR_SH.write_text(new_sh, newline="\n")
        return FILES_MODIFIED

    return FILES_NOT_MODIFIED


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
