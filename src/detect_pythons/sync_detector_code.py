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


def sync(path: pathlib.Path) -> int:
    # Verify the paths are acceptable.
    if path != DETECTOR_SH and path != DETECTOR_PS1:
        print(f"{path} is not an acceptable file path.")
        return FILES_NOT_MODIFIED

    code = path.read_text().strip()
    # Strip leading comments.
    while code.startswith("#"):
        code = code[code.find("\n") + 1 :].lstrip()

    # Redirect outputs to GITHUB_OUTPUT.
    if path == DETECTOR_SH:
        code += ' > "$GITHUB_OUTPUT"'
    else:  # path == DETECTOR_PS1
        code += ' > "$env:GITHUB_OUTPUT"'

    # Determine the text boundaries of the source code in 'action.yml'.
    yaml = ACTION_YML.read_text()
    start_line = f"# START: {path.name}\n"
    end_line = f"# END: {path.name}"
    start = yaml.find(start_line) + len(start_line)
    end = yaml.rfind("\n", start, yaml.find(end_line, start))
    indent = yaml.find("run:", start) - start

    # Prepare the code for injection.
    block = textwrap.indent("run: |\n" + textwrap.indent(code, " " * 2), " " * indent)

    # Inject the source code and determine if 'action.yml' needs to be overwritten.
    new_yaml = yaml[:start] + block + yaml[end:]
    if new_yaml != yaml:
        ACTION_YML.write_text(new_yaml, newline="\n")
        return FILES_MODIFIED

    return FILES_NOT_MODIFIED


def main():
    if len(sys.argv) < 2:
        print("The path to 'detector.sh' or 'detector.ps1' must be provided.")
        sys.exit(FILES_NOT_MODIFIED)

    rc = FILES_NOT_MODIFIED
    for argument in sys.argv[1:]:
        rc |= sync(pathlib.Path(argument).resolve())

    sys.exit(rc)


if __name__ == "__main__":
    main()
