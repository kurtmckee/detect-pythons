..
    This file is a part of the detect-pythons project.
    https://github.com/kurtmckee/detect-pythons
    Copyright 2023 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT

Detect Python interpreters
##########################

*Robust cache-busting based on Python implementations, versions, and architectures.*

----

Purpose
=======

If you're caching Python virtual environments, or tox environments,
or even build artifacts that depend on a particular Python version,
you need robust cache busting to ensure that your caches are invalidated
when a new Python version is released.

``detect-pythons`` provides that much-needed cache busting.

It detects all Python executables in every directory on the ``$PATH``
and identifies:

*   The Python interpreter (CPython, PyPy, or GraalPy)
*   The Python version (like "3.12.0")
    or the Python ABI version (like "3.12")
*   The target architecture (like "x64")

In most cases, the path to the executable already contains this information
so it's not necessary to run the Python interpreter to extract any info.
There are some exceptions, however;
these are covered in the "Implementation" section below.


Usage
=====

The following example demonstrates how ``detect-pythons`` can be used
when caching a Python virtual environment stored in ``.venv/``
and tox test environments stored in ``.tox/``.


..  START_README_EXAMPLE_BLOCK
..  code-block:: yaml

    - uses: "actions/setup-python@v4"
      with:
        python-version: |
          pypy3.10
          3.11

    - uses: "kurtmckee/detect-pythons@v1"

    - uses: "actions/cache@v3"
      id: "restore-cache"
      with:
        # You may need to augment the list of files to hash.
        # For example, you might add 'requirements/*.txt' or 'pyproject.toml'.
        key: "${{ hashFiles('.python-identifiers') }}"
        path: |
          .tox/
          .venv/

    - name: "Identify .venv path"
      shell: "bash"
      run: "echo 'venv-path=.venv/${{ runner.os == 'Windows' && 'Scripts' || 'bin' }}' >> $GITHUB_ENV"

    - name: "Create a virtual environment"
      if: "steps.restore-cache.outputs.cache-hit == false"
      run: |
        python -m venv .venv
        ${{ env.venv-path }}/python -m pip install --upgrade pip setuptools wheel

        # You may need to customize what gets installed next.
        # However, tox is able to run test suites against multiple Pythons,
        # so it's a helpful tool for efficient testing.
        ${{ env.venv-path }}/pip install tox

    - name: "Run the test suite against all installed Pythons"
      run: "${{ env.venv-path }}/tox"
..  END_README_EXAMPLE_BLOCK


Inputs
======

By default, the action writes to a file named ``.python-identifiers``,
which can then be passed to GitHub's ``hashFiles`` function
for convenient cache-busting.

You can customize the path and filename
by modifying the input variable ``identifiers-filename``:

..  code-block:: yaml

    - uses: "kurtmckee/detect-pythons@v1"
      with:
        identifiers-filename: "favored_filename.txt"

To prevent writing a file at all,
set ``identifiers-filename`` to an empty string:

..  code-block:: yaml

    - uses: "kurtmckee/detect-pythons@v1"
      with:
        identifiers-filename: ""


Outputs
=======

In addition to writing to a file,
the action creates an output named ``python-identifiers``.
This may be useful in other contexts.


Implementation
==============

The action tries to find all Python interpreters available on the ``$PATH``
and ensure that critical information about each interpreter is included
in the action output:

*   Implementation
*   Version
*   Architecture


Cached Python interpreters
--------------------------

GitHub runners have common CPython and PyPy versions pre-installed.
These are installed under ``$RUNNER_TOOL_CACHE`` in informative directory paths,
so the paths are used without executing the interpreters.

..  csv-table::
    :header: "Platform", "Sample path under ``$RUNNER_TOOL_CACHE``"

    "Linux", "``/opt/hostedtoolcache/Python/3.11.6/x64/bin``"
    "macOS", "``/Users/runner/hostedtoolcache/PyPy/3.10.13/x64/bin``"
    "Windows", "``C:\hostedtoolcache\windows\Python\3.11.6\x64``"


System CPython interpreters
---------------------------

GitHub's Linux and macOS runners have system CPython interpreters installed.
These are available at paths like ``/usr/bin/python``,
which contains no useful information.

For these interpreters, the interpreter is executed
and the value of ``sysconfig.get_config_var("EXT_SUFFIX")`` is extracted.
This results in a value like the following:

..  csv-table::
    :header: "Platform", "Sample ``EXT_SUFFIX`` value"

    "Linux", "``.cpython-310-x86_64-linux-gnu.so``"
    "macOS", "``.cpython-311-darwin.so``"


...other
--------

At the time of writing, GitHub's current macOS runner has CPython 2.7 pre-installed
and available on the ``$PATH``.
It doesn't have an ``EXT_SUFFIX`` config value, so this action constructs one.

..  csv-table::
    :header: "Platform", "Constructed ``EXT_SUFFIX`` equivalent"

    "macOS", "``.cpython-27-darwin-x86_64``"
