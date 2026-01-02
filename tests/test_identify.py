# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023-2026 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import platform
import sys
import sysconfig

import detect_pythons.identify


def test_main(capsys):
    detect_pythons.identify.main()

    stdout, _ = capsys.readouterr()
    assert stdout == sysconfig.get_config_var("EXT_SUFFIX")
    assert stdout == stdout.strip()


def test_main_ext_suffix_fallback(capsys, monkeypatch):
    all_variables = sysconfig.get_config_vars()
    monkeypatch.setattr(
        "sysconfig.get_config_var",
        lambda name: None if name == "EXT_SUFFIX" else all_variables.get(name),
    )

    detect_pythons.identify.main()

    implementation = platform.python_implementation().lower()
    version = str(sys.version_info[0]) + str(sys.version_info[1])

    stdout, _ = capsys.readouterr()
    assert implementation in stdout
    assert version in stdout
    assert stdout == stdout.strip()

    assert "none" not in stdout.lower()
