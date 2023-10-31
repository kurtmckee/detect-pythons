# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

# Do not modify the Python code below.
# It is copied from 'identify.py' by a pre-commit hook.
python_code=$(
cat <<'identify.py_SOURCE_CODE'
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
identify.py_SOURCE_CODE
)

# Search paths in $PATH for Python interpreters.
IFS=: read -r -a all_paths <<< "$PATH"

# Detect Python interpreters.
paths=()
for path in "${all_paths[@]}"; do
    # Interpreters in RUNNER_TOOL_CACHE have directory names that include:
    #
    # * The implementation (like "Python" or "PyPy")
    # * A version (like "3.10.12")
    # * The architecture (like "x64")
    #
    # In such cases, the path can be used as the identifier.
    if [[ "${path/#${RUNNER_TOOL_CACHE}/}" != "${path}" ]]; then
        # Check for bin/python first;
        # this results in duplicate paths which are later removed.
        if [[ -x "${path}/bin/python" ]]; then
            paths+=("${path}/bin")
        elif [[ -x "${path}/python" ]]; then
            paths+=("${path}")
        fi
    else
        # System Pythons (e.g. /usr/bin/python) have nothing unique in the path.
        # In such cases, it's necessary to run the executable to get something unique.
        if [[ -x "${path}/python" ]]; then
            paths+=("${path}")
            paths+=("$(echo "${python_code}" | "${path}/python" -)")
        fi
    fi
done

# Sort the paths, ensure each path is unique, and create the output result.
result="$(
    echo "${paths[*]}" \
    | tr ' ' '\n' \
    | sort \
    | uniq \
    | tr '\n' ':'
)"

# Trim trailing colons.
result="${result%:}"

# Output path information.
# This must be the final line because it will be automatically transformed to:
#
#     echo "python-identifiers=${result}" > "$GITHUB_OUTPUT"
#
echo "python-identifiers=${result}"
