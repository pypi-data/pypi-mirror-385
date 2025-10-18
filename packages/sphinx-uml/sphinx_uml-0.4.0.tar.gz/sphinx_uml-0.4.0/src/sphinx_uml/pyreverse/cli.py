#!/usr/bin/env python3

"""
Based on the :py:mod:`pylint.pyreverse.main` module.
Under Debian, see the
``/usr/lib/python3/dist-packages/pylint/__init__.py``
file.
"""

import sys
from .main import ParsePyreverseArgs, Run


def run_pyreverse2(args: list[str] = None):
    """
    ``pyreverse2`` entry point, which is used to draw
    UML diagrams by inspecting some python module.

    To display the help related to this program:

    .. code:: bash

        pyreverse2 --help

    To run this program:

    .. code:: bash

        pyreverse2 \\
            --output svg \\
            --project example.a \\
            --sphinx-html-dir docs/_html \\
            --output-directory docs/ \\
            -m y \\
            example.a

    Args:
        args (list[str]): The arguments passed to the script.
            *Example:* ``sys.argv[1]``.
    """
    args = args or sys.argv[1:]
    parser = ParsePyreverseArgs(args)
    runner = Run(parser.config)
    runner.run(parser.remaining_args)


if __name__ == "__main__":
    run_pyreverse2()
