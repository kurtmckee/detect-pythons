import unittest.mock

import pytest

import detect_pythons.sync_readme_example

readme_template = """
abc
..  START_README_EXAMPLE_BLOCK
..  code-block:: yaml

    {}
..  END_README_EXAMPLE_BLOCK
def
"""

yaml_template = """
123
    # START_README_EXAMPLE_BLOCK
{}
    # END_README_EXAMPLE_BLOCK
456
"""


@pytest.mark.parametrize(
    "yaml_text, existing_readme_text, expected_readme_text, expected_rc",
    (
        ("unchanged", "unchanged", "unchanged", 0),
        ("    indent test", "indent test", "indent test", 0),
        ("new", "old", "new", 1),
        ("unchanged", "edited despite warnings", "unchanged", 1),
    ),
)
def test_sync(
    monkeypatch, yaml_text, existing_readme_text, expected_readme_text, expected_rc
):
    # Mock the YAML and README files.
    readme_mock = unittest.mock.Mock()
    readme_mock.read_text.return_value = readme_template.format(existing_readme_text)
    yaml_mock = unittest.mock.Mock()
    yaml_mock.read_text.return_value = yaml_template.format(yaml_text)
    monkeypatch.setattr("detect_pythons.sync_readme_example.README_RST", readme_mock)
    monkeypatch.setattr("detect_pythons.sync_readme_example.EXAMPLE_YAML", yaml_mock)

    # Synchronize the YAML into the README.
    assert detect_pythons.sync_readme_example.main() == expected_rc

    # Verify the README matches expectations.
    if expected_rc:
        assert readme_mock.write_text.call_count == 1
        expected_text = readme_template.format(expected_readme_text)
        assert readme_mock.write_text.call_args[0][0] == expected_text
