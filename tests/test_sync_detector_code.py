# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import unittest.mock

import pytest

import detect_pythons.sync_detector_code

sh_template = """
# abc

# def

{}
"""

ps1_template = """
# ghi

# jkl

{}
"""

yaml_template = """
      123
        # START: detector.sh
        run: |
          {} > "$GITHUB_OUTPUT"
        # END: detector.sh

        # START: detector.ps1
        run: |
          {} > "$env:GITHUB_OUTPUT"
        # END: detector.ps1
      456
"""


@pytest.mark.parametrize(
    "sh_text, ps1_text, yaml_text, expected_yaml_text, expected_rc",
    (
        # No changes
        ("oldsh", "oldps1", ("oldsh", "oldps1"), ("oldsh", "oldps1"), 0),
        # Source files updated
        ("newsh", "oldps1", ("oldsh", "oldps1"), ("newsh", "oldps1"), 1),
        ("newsh", "newps1", ("oldsh", "oldps1"), ("newsh", "newps1"), 1),
        ("oldsh", "newps1", ("oldsh", "oldps1"), ("oldsh", "newps1"), 1),
        # 'action.yml' incorrectly updated
        ("oldsh", "oldps1", ("newsh", "oldps1"), ("oldsh", "oldps1"), 1),
        ("oldsh", "oldps1", ("newsh", "newps1"), ("oldsh", "oldps1"), 1),
        ("oldsh", "oldps1", ("oldsh", "newps1"), ("oldsh", "oldps1"), 1),
    ),
)
def test_sync(
    monkeypatch, sh_text, ps1_text, yaml_text, expected_yaml_text, expected_rc
):
    # Mock the script files and the YAML file.
    sh_mock = unittest.mock.Mock()
    sh_mock.read_text.return_value = sh_template.format(sh_text)
    sh_mock.name = detect_pythons.sync_detector_code.DETECTOR_SH.name
    ps1_mock = unittest.mock.Mock()
    ps1_mock.read_text.return_value = ps1_template.format(ps1_text)
    ps1_mock.name = detect_pythons.sync_detector_code.DETECTOR_PS1.name
    yaml_mock = unittest.mock.Mock()
    yaml_mock.read_text.return_value = yaml_template.format(*yaml_text)

    monkeypatch.setattr("detect_pythons.sync_detector_code.DETECTOR_SH", sh_mock)
    monkeypatch.setattr("detect_pythons.sync_detector_code.DETECTOR_PS1", ps1_mock)
    monkeypatch.setattr("detect_pythons.sync_detector_code.ACTION_YML", yaml_mock)

    # Synchronize the Python code into the shell script.
    assert detect_pythons.sync_detector_code.main() == expected_rc

    # Verify the shell script matches expectations.
    if expected_rc:
        assert yaml_mock.write_text.call_count == 1
        expected_text = yaml_template.format(*expected_yaml_text)
        assert yaml_mock.write_text.call_args[0][0] == expected_text
