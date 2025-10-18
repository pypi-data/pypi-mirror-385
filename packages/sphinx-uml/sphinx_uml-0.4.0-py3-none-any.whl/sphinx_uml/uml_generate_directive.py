import argparse
from pathlib import Path
from docutils import nodes
from docutils.parsers.rst import directives
from pylint.pyreverse.main import writer
from pylint.pyreverse.diagrams import (
    ClassDiagram,
    PackageDiagram,
)
from sphinx.ext.graphviz import (
    figure_wrapper,
    graphviz,
)
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec
from typing import ClassVar


class UmlNode(graphviz):
    """
    Defines a UML ``docutils`` node.
    We populate its attribute so that we can rely on the
    default ``graphviz`` node.
    """
    @classmethod
    def from_dot(cls, dotcode: str) -> "UmlNode":
        """
        Builds a :py:class:`UmlNode` instance from a Graphviz
        dot string.

        Args:
            dotcode (str): A Graphviz dot string.
                *Example:* ``digraph G {0 -> 1}``

        Returns:
            The resulting :py:class:`UmlNode` instance.
        """
        node = cls()
        node["code"] = dotcode
        node["options"] = {"graphviz_dot": "dot"}

        # We rely on sphinx.ext.inheritance_diagram CSS classes
        # to be responsive to dark/light themes.
        # TODO: improve this!
        node["classes"] = ["inheritance"]
        return node

    @classmethod
    def to_dot(
        cls,
        diagram: ClassDiagram | PackageDiagram,
        config: argparse.Namespace
    ) -> str:
        """
        Exports a diagram definition obtained from ``pyreverse``
        to a Graphviz dot string.

        Args:
            diagram (ClassDiagram | PackageDiagram): The diagram
                that must be exported.
            config (argparse.Namespace): The configuration
                obtained from the Sphinx configuration file.

        Returns:
            The resulting :py:class:`UmlNode` instance.
        """
        from .pyreverse import DotPrinter, SphinxHtmlProxy
        dwriter = writer.DiagramWriter(config)
        dwriter.printer_class = DotPrinter
        # TODO Build xrefs as in
        # /usr/lib/python3/dist-packages/sphinx/ext/inheritance_diagram.py?
        dwriter.api_doc = SphinxHtmlProxy()
        dwriter.api_doc.sphinx_html_dir = config.sphinx_html_dir
        dwriter.write([diagram])
        return "\n".join(dwriter.printer.lines)

    @classmethod
    def from_pyreverse(
        cls,
        diagram: ClassDiagram | PackageDiagram,
        config: argparse.Namespace
    ) -> "UmlNode":
        """
        Builds a :py:class:`UmlNode` from a diagram definition
        obtained from ``pyreverse``.

        Args:
            diagram (ClassDiagram | PackageDiagram): The diagram
                that must be exported.
            config (argparse.Namespace): The configuration
                obtained from the Sphinx configuration file.

        Returns:
            The resulting :py:class:`UmlNode` instance.
        """
        return cls.from_dot(cls.to_dot(diagram, config))


def guess_svg_basename(options: dict, code: str) -> str:
    """
    Infers the svg filename of an UML diagram
    See ``/usr/lib/python3/dist-packages/sphinx/ext/graphviz.py``.

    Args:
        options (dict): The options passed to the
            :py:func:`graphviz.ext.render_dot` function.
        code (str): A graphviz string, passed to the
            :py:func:`graphviz.ext.render_dot` function.

    Returns:
        The corresponding SVG basename
    """
    from hashlib import sha1
    graphviz_dot = options.get("graphviz_dot", None)
    hashkey = (code + str(options) + str(graphviz_dot) + "()").encode()
    svg_basename = (
        f'graphviz-{sha1(hashkey, usedforsecurity=False).hexdigest()}.svg'
    )
    return svg_basename


class UMLGenerateDirective(SphinxDirective):
    """
    UML directive to generate a pyreverse diagram
    """

    # Sphinx stuff to control argument passing
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec: ClassVar[OptionSpec] = {
        "caption": directives.unchanged,
        "classes": directives.flag,
        "packages": directives.flag,
    }

    def _build_args(self) -> list[str]:
        args = list()
        config = self.config
        if config.uml_filter_mode:
            assert config.uml_filter_mode
            args.extend(("--filter-mode", config.uml_filter_mode))
        if config.uml_class:
            args.extend(("--class", config.uml_class))
        if config.uml_show_ancestors:
            args.extend(("--show-ancestors", config.uml_show_ancestors))
        if config.uml_all_ancestors:
            args.append("--all-ancestors")
        if config.uml_show_associated:
            args.extend(("--show-associated", config.uml_show_associated))
        if config.uml_all_associated:
            args.append("--all-associated")
        if config.uml_show_builtin:
            args.append("--show-builtin")
        if config.uml_module_names:
            args.extend(("--module-names", config.uml_module_names))
        if config.uml_only_classnames:
            args.append("--only-classnames")
        if config.uml_ignore:
            args.extend(("--ignore", config.uml_ignore))
        if config.uml_colorized:
            args.append("--colorized")
        return args

    def html_root_dir(self) -> Path:
        """
        Crafts the HTML prefix to move from the current HTML
        to the HTML root directory.

        Returns:
            The corresponding relative :py:class:`Path` instance.

        Example:
            Assume that:

            - the documentation is built in:
              ``"~/git/sphinx-uml/docs"``;
            - the current document is;
              ``"~/git/sphinx-uml/docs/users/examples.rst"``;

            Then, the returned value is ``"../"``.
            As the HTML hierarchy follows the RST hierarchy, we use
            this prefix to setup our :py:class:`SphinxHtmlProxy`.
        """
        doc = self.state.document
        env = doc.settings.env
        base_dir = Path(env.srcdir).absolute()
        cur_path = Path(doc.current_source)
        rel_path = str(cur_path.relative_to(base_dir).parent)
        if rel_path == ".":
            return Path(rel_path)
        n = len(rel_path.split("/"))
        return Path("/".join([".."] * n))

    def run(self):
        """
        To test this extension, as a developer:

        .. shell

            make install-sphinx-custom clean-doc docs

        To test this `pyreverse2`, called by this extension:

        .. shell

            pyreverse2 \\
               --output svg \\
               --project example.a \\
               --sphinx-html-dir docs/_html \\
               --output-directory docs/ \\
               -m y \\
               example.a
        """
        # ..uml: module_name
        module_name = self.arguments[0]

        # :classes:, :packages:, :caption:
        with_classes = "classes" in self.options
        with_packages = "packages" in self.options
        caption = self.options.get("caption")

        pyprocess_args = self._build_args() + [
            "--sphinx-html-dir", str(self.html_root_dir()),
            module_name
        ]

        # make install-sphinx-custom clean-doc docs
        from .pyreverse import Run, ParsePyreverseArgs

        parser = ParsePyreverseArgs(pyprocess_args)
        runner = Run(parser.config)
        diadefs = runner.diadefs(parser.remaining_args)

        # Craft the list of nodes to be appended to the doctree's AST.
        ret = list()
        for diagram in diadefs:
            # :classes: and :packages: switches
            if isinstance(diagram, PackageDiagram):
                if not with_packages:
                    continue
            elif isinstance(diagram, ClassDiagram):
                if not with_classes:
                    continue
            else:
                raise ValueError(f"Invalid type {type(diagram)}")

            # Build graphviz node
            code = UmlNode.to_dot(diagram, runner.config)
            node = UmlNode.from_dot(code)

            svg_basename = guess_svg_basename(node.attributes["options"], code)

            # Appends a link 'Open in a new tab'
            paragraph = nodes.paragraph(text="")
            paragraph += nodes.reference(
                # See the HTMLTranslator.visit_reference function in
                # /usr/lib/python3/dist-packages/docutils/writers/_html_base.py
                text="Open in a new tab",
                refuri=str(
                    self.html_root_dir() / "_images" / svg_basename
                ),
            )

            # Add caption
            if caption:
                node = figure_wrapper(self, node, caption)

            ret += [node, paragraph]

        return ret
