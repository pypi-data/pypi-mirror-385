from pathlib import Path
from ..singleton import Singleton


class SphinxHtmlProxy(metaclass=Singleton):
    """
    The :py:class:`SphinxHtmlProxy` is a singleton in charge of returning
    the path of an HTML file corresponding to a class of the project being
    pyreversed.
    """
    def __init__(self):
        """
        Constructor. The attributes are set by the calling code,
        depending on the context.
        """
        self.sphinx_html_dir: str  # The HTML Spring address or directory
        self.module_name: str      # The module being processed
        self.class_name: str       # The class being processed

    def set_sphinx_html_dir(self, sphinx_html_dir: Path | str):
        """
        Set the HTML Sphinx documentation directory.

        Args:
            sphinx_html_dir (Path | str): The input directory.
                *Example:* ``~/git/unext/docs/_build/html``.
        """
        # assert Path(sphinx_html_dir).exists(), sphinx_html_dir
        self.sphinx_html_dir = sphinx_html_dir

    def url(self, name: str = "") -> str:
        """
        Crafts an Sphinx URL depending on:

        - the HTML Sphinx directory (:py:attr:`sphinx_html_dir`);
        - the current module (:py:attr:`module_name`);
        - the current class (:py:attr:`class_name`);
        - the current method/attribute if any (see ``name``).

        Args:
            name (str): The current method/attribute name if any,
                ``""`` otherwise.

        Returns:
            The resulting URL if any, ``None`` otherwise.
        """
        if not self.sphinx_html_dir:
            # HTML documentation directory not set.
            return None
        if ":" in name:
            name = name[:name.find(":")]
        return (
            # File
            f"{self.sphinx_html_dir}/{self.module_name}.html"
            # Anchor (class)
            f"#{self.module_name}.{self.class_name}"
        ) + (
            # Anchor (attr / method)
            f".{name}" if name
            else ""
        )
