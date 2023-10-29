# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import pathlib
import sys
import textwrap

FILES_NOT_MODIFIED = 0
FILES_MODIFIED = 1

DETECTOR_SH = (pathlib.Path(__file__).parent / "detector.sh").resolve()
DETECTOR_PS1 = (pathlib.Path(__file__).parent / "detector.ps1").resolve()
ACTION_YML = (pathlib.Path(__file__).parent / "../../action.yml").resolve()


def main() -> int:
    # Read the YAML file once and double-assign it.
    new_yaml = yaml = ACTION_YML.read_text(encoding="utf-8")

    for path in (DETECTOR_SH, DETECTOR_PS1):
        code = path.read_text(encoding="utf-8").strip()
        # Strip leading comments.
        while code.startswith("#"):
            code = code[code.find("\n") + 1 :].lstrip()
        # Redirect final output to GITHUB_OUTPUT.
        if path is DETECTOR_SH:
            code += ' > "$GITHUB_OUTPUT"'
        else:  # path is DETECTOR_PS1
            code += ' > "$env:GITHUB_OUTPUT"'

        # Determine the text boundaries of the source code in 'action.yml'.
        start_line = f"# START: {path.name}\n"
        end_line = f"# END: {path.name}"
        start = new_yaml.find(start_line) + len(start_line)
        end = new_yaml.rfind("\n", start, new_yaml.find(end_line, start))
        indent = new_yaml.find("run:", start) - start

        # Prepare the code for injection.
        block = textwrap.indent(
            "run: |\n" + textwrap.indent(code, " " * 2), " " * indent
        )

        # Inject the source code into 'action.yml'.
        new_yaml = new_yaml[:start] + block + new_yaml[end:]

    # Overwrite 'action.yml' if needed.
    if new_yaml != yaml:
        ACTION_YML.write_text(new_yaml, newline="\n")
        return FILES_MODIFIED

    return FILES_NOT_MODIFIED


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
