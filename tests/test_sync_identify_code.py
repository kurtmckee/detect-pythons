import unittest.mock

import pytest

import detect_pythons.sync_identify_code

py_template = """
# abc

# def

{}
"""

sh_template = """
123
cat <<'identify.py_SOURCE_CODE'
{}
identify.py_SOURCE_CODE
456
"""


@pytest.mark.parametrize(
    "existing_py_text, existing_sh_text, expected_sh_text, expected_rc",
    (
        ("unchanged", "unchanged", "unchanged", 0),
        ("new", "old", "new", 1),
        ("unchanged", "edited despite warnings", "unchanged", 1),
    ),
)
def test_sync(
    monkeypatch, existing_py_text, existing_sh_text, expected_sh_text, expected_rc
):
    # Mock the Python and shell script files.
    python_mock = unittest.mock.Mock()
    python_mock.read_text.return_value = py_template.format(existing_py_text)
    sh_mock = unittest.mock.Mock()
    sh_mock.read_text.return_value = sh_template.format(existing_sh_text)
    monkeypatch.setattr("detect_pythons.sync_identify_code.IDENTIFY_PY", python_mock)
    monkeypatch.setattr("detect_pythons.sync_identify_code.DETECTOR_SH", sh_mock)

    # Synchronize the Python code into the shell script.
    assert detect_pythons.sync_identify_code.main() == expected_rc

    # Verify the shell script matches expectations.
    if expected_rc:
        assert sh_mock.write_text.call_count == 1
        expected_text = sh_template.format(expected_sh_text)
        assert sh_mock.write_text.call_args[0][0] == expected_text
