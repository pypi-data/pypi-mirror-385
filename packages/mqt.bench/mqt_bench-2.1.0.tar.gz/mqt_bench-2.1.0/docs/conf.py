# Copyright (c) 2023 - 2025 Chair for Design Automation, TUM
# Copyright (c) 2025 Munich Quantum Software Company GmbH
# All rights reserved.
#
# SPDX-License-Identifier: MIT
#
# Licensed under the MIT License

"""Sphinx configuration file."""

from __future__ import annotations

import warnings
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING

import pybtex.plugin
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.template import field, href

ROOT = Path(__file__).parent.parent.resolve()


try:
    version = metadata.version("mqt.bench")
except ModuleNotFoundError:
    msg = (
        "Package should be installed to produce documentation! "
        "Assuming a modern git archive was used for version discovery."
    )
    warnings.warn(msg, stacklevel=1)

    from setuptools_scm import get_version

    version = get_version(root=str(ROOT), fallback_root=ROOT)

# Filter git details from version
release = version.split("+")[0]
if TYPE_CHECKING:
    from pybtex.database import Entry
    from pybtex.richtext import HRef

project = "MQT Bench"
author = "Chair for Design Automation, TUM & Munich Quantum Software Company"
language = "en"
project_copyright = "2023 - 2025 Chair for Design Automation, TUM & 2025 Munich Quantum Software Company"
# -- General configuration ---------------------------------------------------

master_doc = "index"

templates_path = ["_templates"]

extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxext.opengraph",
    "sphinx.ext.viewcode",
    "sphinxcontrib.bibtex",
]

pygments_style = "colorful"

modindex_common_prefix = ["mqt.bench."]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "typing_extensions": ("https://typing-extensions.readthedocs.io/en/latest/", None),
    "qiskit": ("https://docs.quantum.ibm.com/api/qiskit", None),
    "mqt": ("https://mqt.readthedocs.io/en/latest/", None),
}

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "substitution",
    "deflist",
    "dollarmath",
]

nb_execution_mode = "cache"
nb_execution_raise_on_error = True

autosectionlabel_prefix_document = True

exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "**.jupyter_cache",
    "jupyter_execute/**",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]


class CDAStyle(UnsrtStyle):
    """Custom style for including PDF links."""

    def format_url(self, _e: Entry) -> HRef:
        """Format URL field as a link to the PDF.

        Returns:
            The formatted URL field.
        """
        url = field("url", raw=True)
        return href()[url, "[PDF]"]


pybtex.plugin.register_plugin("pybtex.style.formatting", "cda_style", CDAStyle)

bibtex_bibfiles = ["refs.bib"]
bibtex_default_style = "cda_style"

copybutton_prompt_text = r"(?:\(venv\) )?(?:\[.*\] )?\$ "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"

autosummary_generate = True

autoapi_dirs = ["../src/mqt"]
autoapi_python_use_implicit_namespaces = True
autoapi_root = "api"
autoapi_add_toctree_entry = False
autoapi_ignore = [
    "*/**/_version.py",
]
autoapi_options = [
    "members",
    "imported-members",
    "show-inheritance",
    "special-members",
    "undoc-members",
]
autoapi_keep_files = True
add_module_names = False
toc_object_entries_show_parents = "hide"
python_use_unqualified_type_names = True
typehints_use_rtype = False
napoleon_use_rtype = False
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = [
    "custom.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
]
html_theme_options = {
    "light_logo": "mqt_dark.png",
    "dark_logo": "mqt_light.png",
    "source_repository": "https://github.com/munich-quantum-toolkit/bench/",
    "source_branch": "main",
    "source_directory": "docs/",
    "navigation_with_keys": True,
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/munich-quantum-toolkit/bench/",
            "html": "",
            "class": "fa-brands fa-solid fa-github fa-2x",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/mqt-bench/",
            "html": "",
            "class": "fa-brands fa-solid fa-python fa-2x",
        },
    ],
}
