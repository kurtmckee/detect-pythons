# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023-2024 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

IDENTIFY_PY="${GITHUB_ACTION_PATH}/src/detect_pythons/identify.py"

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
            paths+=("$("${path}/python" "${IDENTIFY_PY}")")
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

echo "python-identifiers=${result}"
