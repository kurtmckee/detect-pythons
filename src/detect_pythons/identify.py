# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023-2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import print_function

import sysconfig


def main():
    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX")
    if ext_suffix is not None:
        print(ext_suffix, end="")
    else:
        # Python 2.7 is still pre-installed on GitHub macOS runners.
        import platform

        implementation = platform.python_implementation().lower()
        implementation_version = "".join(platform.python_version_tuple()[:2])
        platform_system = platform.system().lower()
        platform_machine = platform.machine().lower()

        print(
            "." + implementation,
            implementation_version,
            platform_system,
            platform_machine,
            sep="-",
            end="",
        )


if __name__ == "__main__":  # pragma: no cover
    main()
