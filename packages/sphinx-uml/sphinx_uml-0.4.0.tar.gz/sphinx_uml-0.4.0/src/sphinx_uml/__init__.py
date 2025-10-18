__author__ = "Marc-Olivier Buob"
__maintainer__ = "Marc-Olivier Buob"
__email__ = "marc-olivier.buob@nokia-bell-labs.com"
__license__ = "BSD-3"
__version__ = "0.4.0"
__all__ = ["UMLGenerateDirective"]


import os
from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata
from .uml_generate_directive import UMLGenerateDirective


def setup(app: Sphinx) -> ExtensionMetadata:
    """Setup directive"""
    app.setup_extension("sphinx.ext.graphviz")

    # Allow override of the directive, defaulting to "uml"
    directive_name_to_use = os.environ.get("SPHINX_UML_DIRECTIVE", "uml")
    app.add_directive(directive_name_to_use, UMLGenerateDirective)

    # sphinx.ext.inheritance_diagram-like options
    # app.add_config_value("uml_graph_attrs", {}, "")
    # app.add_config_value("uml_node_attrs", {}, "")
    # app.add_config_value("uml_edge_attrs", {}, "")
    # app.add_config_value("uml_alias", {}, "")

    # pylint.pyreverse-like options
    app.add_config_value("uml_filter_mode", default=None, rebuild="env")
    app.add_config_value("uml_class", default=None, rebuild="env")
    app.add_config_value("uml_show_ancestors", default=None, rebuild="env")
    app.add_config_value("uml_all_ancestors", default=None, rebuild="env")
    app.add_config_value("uml_show_associated", default=None, rebuild="env")
    app.add_config_value("uml_all_associated", default=None, rebuild="env")
    app.add_config_value("uml_show_builtin", default=None, rebuild="env")
    app.add_config_value("uml_module_names", default=None, rebuild="env")
    app.add_config_value("uml_only_classnames", default=None, rebuild="env")
    app.add_config_value("uml_ignore", default=None, rebuild="env")
    app.add_config_value("uml_colorized", default=None, rebuild="env")

    return {
        "version": __version__,
        "parallel_read_safe": True
    }
