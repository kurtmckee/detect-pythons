..
    This file is a part of the detect-pythons project.
    https://github.com/kurtmckee/detect-pythons
    Copyright 2023-2024 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT

Detect Python interpreters
##########################

*Robust cache-busting based on Python implementations, versions, and architectures.*

----

Purpose
=======

If you're caching Python virtual environments to speed up your CI runs,
you've likely encountered broken symlinks or missing libraries
when a new Python patch version was released.
This is particularly likely to happen
when using tox to test multiple Python versions simultaneously.

``detect-pythons`` provides that much-needed cache busting.

It detects all Python executables in every directory on the ``$PATH``
and identifies:

*   The Python interpreter (like CPython, PyPy, or GraalPy)
*   The Python version (like "3.12.1")
    or the Python ABI version (like "3.12")
*   The target architecture (like "x64")

In most cases, the path to the executable already contains this information
so it's not necessary to run the Python interpreter to extract any info.
That makes ``detect-pythons`` *fast*.

There are some exceptions, however;
these are covered in the "Implementation" section below.


Usage
=====

The following example demonstrates how ``detect-pythons`` can be used
when caching a Python virtual environment stored in ``.venv/``
and tox test environments stored in ``.tox/``.


..  START_README_EXAMPLE_BLOCK
..  code-block:: yaml

    - uses: "actions/setup-python@v5"
      with:
        python-version: |
          graalpy-23.1
          pypy-3.10
          3.12

    - uses: "kurtmckee/detect-pythons@v1"

    - uses: "actions/cache@v4"
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

``detect-pythons`` finds all Python interpreters available on the ``$PATH``
and ensures that critical information about each interpreter is included
in its output:

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

    "Linux", "``/opt/hostedtoolcache/Python/3.12.1/x64/bin``"
    "macOS", "``/Users/runner/hostedtoolcache/PyPy/3.10.13/x64/bin``"
    "Windows", "``C:\hostedtoolcache\windows\Python\3.12.1\x64``"


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


macOS runner variability
------------------------

At the time of writing, GitHub's macOS runners sometimes have CPython 2.7 pre-installed.
CPython 2.7 doesn't have an ``EXT_SUFFIX`` config value,
so ``detect-pythons`` constructs one.

..  csv-table::
    :header: "Platform", "Constructed ``EXT_SUFFIX`` equivalent"

    "macOS 12.6", "``.cpython-27-darwin-x86_64``"

Note that CPython 2.7 is only installed *sometimes*; sometimes it isn't.
This is because ``macos-latest`` is sometimes macOS 12.6, and sometimes it's macOS 12.7.
See `actions/runner-images#8642`_ for more information.

When using ``detect-pythons`` to help with cache-busting,
this variability means that you may see two caches appear in regular use
for your macOS-based workflows;
one that is valid when CPython 2.7 is pre-installed,
and another that is valid when it *isn't* installed.


..  Links
..  -----
..
..  _actions/runner-images#8642: https://github.com/actions/runner-images/issues/8642
