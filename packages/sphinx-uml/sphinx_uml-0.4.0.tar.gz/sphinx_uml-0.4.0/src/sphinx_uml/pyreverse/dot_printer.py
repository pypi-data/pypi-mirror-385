"""
Based on the :py:mod:`pyreverse.dot_printer` module.
Under Debian, see the
``/usr/lib/python3/dist-packages/pylint/pyreverse/dot_printer.py``
file.
"""

# Inherited imports
from pylint.pyreverse.dot_printer import (
    NodeProperties,
    nodes,
    get_annotation_label,
    NodeType,
    SHAPES
)

# Custom imports
from pylint.pyreverse.dot_printer import DotPrinter as _DotPrinter
from .sphinx_html_proxy import SphinxHtmlProxy


class DotPrinter(_DotPrinter):
    """
    Overloads the :py:class:`pylint.pyreverse.dot_printer.DotPrinter` class
    to export an UML diagram using Graphviz and crafting links in the output
    file to map each class/method/attribute name with the corresponding Sphinx
    HTML page/anchor.
    """
    def _open_graph(self) -> None:
        super()._open_graph()
        self.emit("bgcolor=transparent")

    def _build_label_for_node(  # noqa: C901 func too-complex
        self,
        properties: NodeProperties
    ) -> str:
        if not properties.label:
            return ""

        # Attribute and method display
        # HTML tags supported by Graphviz:
        # https://graphviz.org/doc/info/shapes.html#html
        # NB: A node can embed at most one <table> tag.
        # Several links in a single node: https://stackoverflow.com/a/48029398

        def vstack(**kwargs: dict) -> str:
            text = kwargs.pop("text", None)
            if not text:
                return ""
            if "tooltip" not in kwargs:
                kwargs["tooltip"] = ""
            if "href" in kwargs and kwargs["href"] is None:
                kwargs.pop("href")
            attrs = " ".join([
                f'{k}="{v}"'
                for k, v in kwargs.items()
            ])
            return f"\n\t<tr><td {attrs}>{text}</td></tr>"

        def escape_string(s: str) -> str:
            return s.replace('"', '\\"')

        proxy = SphinxHtmlProxy()
        class_name = properties.label
        label = (
            f'<table border="0" align="left" tooltip="{class_name}" '
            'width="0" cellpadding="0">'
        )
        class_url = proxy.url()

        # Class name
        label += vstack(
            border=1,
            href=class_url,
            tooltip=escape_string(class_name),
            target="_top",
            text=f"<b>{class_name}</b>"
        )

        # Only class names
        if properties.attrs is None and properties.methods is None:
            return label + "</table>"

        attrs: list[str] = properties.attrs or []
        methods: list[nodes.FunctionDef] = properties.methods or []

        # Add class attributes
        if attrs:
            label += vstack(
                align="left",
                text="<b>Attributes:</b>"
            )
        for attr in attrs:
            attr_url = proxy.url(attr)
            attr_label = attr.replace("|", r"\|")
            label += vstack(
                align="left",
                href=attr_url,
                target="_top",
                tooltip=escape_string(f"{class_name}.{attr_label}"),
                text=attr_label
            )

        # Add class methods
        if methods:
            label += vstack(
                align="left",
                text="<b>Methods:</b>"
            )
        for func in methods:
            args = (
                ", "
                .join(self._get_method_arguments(func))
                .replace("|", r"\|")
            )
            method_name = func.name
            method_url = proxy.url(func.name)
            prototype = rf"{method_name}({args})"
            if func.returns:
                annotation_label = get_annotation_label(func.returns)
                prototype += (
                    ": " + self._escape_annotation_label(annotation_label)
                )
            if func.is_abstract():
                prototype = f"<i>{prototype}</i>"
            label += vstack(
                align="left",
                href=method_url,
                target="_top",
                tooltip=escape_string(f"{class_name}.{func.name}"),
                text=prototype
            )

        label += "</table>"
        # >>
        return label

    def emit_node(
        self,
        name: str,
        type_: NodeType,
        properties: NodeProperties | None = None,
    ) -> None:
        proxy = SphinxHtmlProxy()
        i = name.rfind(".")
        if i > 0:
            proxy.module_name = name[: i]
            proxy.class_name = name[i + 1:]
        else:
            proxy.module_name = name
            proxy.class_name = None

        if properties is None:
            properties = NodeProperties(label=name)
        shape = SHAPES[type_]
        color = (
            properties.color if properties.color is not None
            else self.DEFAULT_COLOR
        )
        style = "filled" if color != self.DEFAULT_COLOR else "solid"
        label = self._build_label_for_node(properties)
        label_part = f", label=<{label}>" if label else ""
        fontcolor_part = (
            f', fontcolor="{properties.fontcolor}"' if properties.fontcolor
            else ""
        )

        # URLs in Graphviz: https://graphviz.org/docs/attrs/URL/
        # https://talk.observablehq.com/t/hyperlink-in-graphviz-node-doesnt-work/4775/2
        # Example:
        # dot`digraph { b [URL="https://google.com" target="_top"]; a -> b; }`
        url = proxy.url()
        self.emit(
            f'"{name}" [' + ", ".join([
                f'color="{color}"{fontcolor_part}{label_part}',
                f'shape="{shape}"',
                f'style="{style}"',
                f'URL="{url}"',
            ]) + "];"
        )
