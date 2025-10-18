# `sphinx-uml`

[![PyPI](https://img.shields.io/pypi/v/sphinx-uml.svg)](https://pypi.python.org/pypi/sphinx-uml/)
[![Build](https://github.com/ibgp2/sphinx-uml/workflows/build/badge.svg)](https://github.com/ibgp2/sphinx-uml/actions/workflows/build.yml)
[![Documentation](https://github.com/ibgp2/sphinx-uml/workflows/docs/badge.svg)](https://github.com/ibgp2/sphinx-uml/actions/workflows/docs.yml)
[![ReadTheDocs](https://readthedocs.org/projects/sphinx-uml/badge/?version=latest)](https://sphinx-uml.readthedocs.io/en/)

## Overview

`sphinx-uml` is a python package that provides:

- A Sphinx extension, called using `.. uml`, which generates
  [UML diagrams](https://en.wikipedia.org/wiki/Unified_Modeling_Language)
  from python modules, just like
  [`sphinx-pyreverse`](https://github.com/sphinx-pyreverse/sphinx-pyreverse/).
- The `pyreverse2` command, that extends `pyreverse` provided by `pylint`.

Compared to [`sphinx-pyreverse`](https://github.com/sphinx-pyreverse/sphinx-pyreverse/),
`sphinx-uml` outputs enriched [dot](https://graphviz.org/doc/info/lang.html) or
[SVG](https://en.wikipedia.org/wiki/SVG) UML diagrams.

* responsive to light/black Sphinx themes (as
  [pydata](https://pydata-sphinx-theme.readthedocs.io/en/stable/));
* if the HTML address is known, the class/attribute/method names can be clicked
  to browse the corresponding documentation page.

## Features 
### `.. uml` directive

UML diagrams can be obtained by using the ``.. uml`` directive.

_Example:_

```rst
.. uml:: example.module.b1
    :caption: UML diagram of ``example.module.b1``
    :classes:
    :packages:
```

[This toy example](https://github.com/ibgp2/sphinx-uml/tree/main/example)
shows how to use the ``.. uml`` directive in a Sphinx documentation using
[`sphinx.ext.autodoc`](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) and
[`sphinx.ext.autosummary`](https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html).

### `pyreverse2`

The `pyreverse2` behaves like the original `pyreverse` command with two main differences:

* `--ouput`: `svg` and `dot` are the only supported output formats;
* `--sphinx-html-dir` can be used to indicate where is the HTML root directory.

_Example:_ In the example below, we assume that:

* the `example` package has been installed
* the documentation has been built in $HOME/git/sphinx-pyreverse/example/docs/_build/html/

```bash
# Generate the UML diagram for each value of x
for x in example example.module example.module.submodule example.module.submodule.c1
do
   pyreverse2 \
      --sphinx-html-dir $HOME/git/sphinx-uml/example/docs/_build/html/ \
      --output svg \
      --project $x \
      $x
   # The previous command outputs {classes,packages}_$o.svg
done
```

## [Documentation](https://sphinx-uml.readthedocs.io/en/)
