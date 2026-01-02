# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023-2026 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import pathlib
import sys
import textwrap

FILES_NOT_MODIFIED = 0
FILES_MODIFIED = 1

ROOT = pathlib.Path(__file__).parent.parent.parent
EXAMPLE_YAML = (ROOT / ".github/workflows/readme_example.yaml").resolve()
README_RST = (ROOT / "README.rst").resolve()


def main() -> int:
    # Extract the YAML example to embed in the README.
    yaml = EXAMPLE_YAML.read_text(encoding="utf-8")
    start_line = "# START_README_EXAMPLE_BLOCK\n"
    end_line = "# END_README_EXAMPLE_BLOCK"
    start = yaml.find(start_line) + len(start_line)
    end = yaml.rfind("\n", start, yaml.find(end_line, start))
    example = textwrap.dedent(yaml[start:end])

    # Prepare the example for injection.
    block = "..  code-block:: yaml\n\n" + textwrap.indent(example, " " * 4)

    # Determine the text boundaries of the source code in the README.
    rst = README_RST.read_text(encoding="utf-8")
    start_line = "..  START_README_EXAMPLE_BLOCK\n"
    end_line = "..  END_README_EXAMPLE_BLOCK"
    start = rst.find(start_line) + len(start_line)
    end = rst.rfind("\n", start, rst.find(end_line, start))

    # Inject the example and determine if the README needs to be overwritten.
    new_rst = rst[:start] + block + rst[end:]
    if new_rst != rst:
        README_RST.write_text(new_rst, encoding="utf-8", newline="\n")
        return FILES_MODIFIED

    return FILES_NOT_MODIFIED


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
