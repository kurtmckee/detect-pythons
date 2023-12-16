# This file is a part of the detect-pythons project.
# https://github.com/kurtmckee/detect-pythons
# Copyright 2023 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

# Search paths in $PATH for Python interpreters.
$all_paths = $env:PATH -split ";"

# Detect Python interpreters.
$paths = @()
foreach ($path in $all_paths) {
    # Only consider paths in RUNNER_TOOL_CACHE.
    if ($path.StartsWith($env:RUNNER_TOOL_CACHE)) {
        if (Test-Path "$path\python.exe") {
            $paths += $path
        }
    }
}

# Sort the paths, ensure each path is unique, and create the output result.
$result = (
    $paths `
    | Sort-Object `
    | Get-Unique
) -join ";"

Write-Output "python-identifiers=$result"
