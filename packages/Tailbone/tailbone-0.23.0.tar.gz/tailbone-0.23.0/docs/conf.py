# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version as get_version

project = 'Tailbone'
copyright = '2010 - 2024, Lance Edgar'
author = 'Lance Edgar'
release = get_version('Tailbone')

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
    'rattail': ('https://docs.wuttaproject.org/rattail/', None),
    'webhelpers2': ('https://webhelpers2.readthedocs.io/en/latest/', None),
    'wuttaweb': ('https://docs.wuttaproject.org/wuttaweb/', None),
    'wuttjamaican': ('https://docs.wuttaproject.org/wuttjamaican/', None),
}

# allow todo entries to show up
todo_include_todos = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None
#html_logo = 'images/rattail_avatar.png'

# Output file base name for HTML help builder.
#htmlhelp_basename = 'Tailbonedoc'
