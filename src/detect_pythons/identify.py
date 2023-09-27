# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import print_function

import sysconfig


def main():
    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX")
    if ext_suffix is not None:
        print(ext_suffix)
    else:
        # Python 2.7 on GitHub macOS runners
        import platform

        print(
            "." + platform.python_implementation().lower(),
            sysconfig.get_config_var("py_version_nodot"),
            sysconfig.get_config_var("MACHDEP"),
            sep="-",
        )


if __name__ == "__main__":
    main()
