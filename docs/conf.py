# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os,sys;
sys.path.insert(0, os.path.abspath('../')); 

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SCINT'
copyright = '2023, R. Alvárez, A. de la Torre, S. Manthey, L. Pérez'
author = 'R. Alvárez, A. de la Torre, S. Manthey, L. Pérez'
release = '1.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser', 'sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.napoleon', 'sphinxemoji.sphinxemoji', 'sphinx_copybutton', 'nbsphinx', "sphinx_plotly_directive",]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'furo'
html_static_path = ['_static']
html_theme = "sphinx_book_theme"
html_css_files = ['css/rtd_dark.css',]
# html_logo = "_static/logo-wide.svg"
# html_favicon = "_static/logo-square.svg"
html_title = "SCINT DOCUMENTATION"
html_theme_options = {
    "home_page_in_toc": True,
    "repository_url": "https://github.com/CIEMAT-Neutrino/SCINT",
    "repository_branch": "master",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
}

myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 2
myst_footnote_transition = True
myst_dmath_double_inline = True
myst_enable_checkboxes = True