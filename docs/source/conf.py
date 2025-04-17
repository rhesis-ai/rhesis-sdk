# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

project = 'rhesis-sdk'
copyright = '2024, Engineering Team'
author = 'Engineering Team'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings
extensions = [
    'sphinx.ext.autodoc',  # Required for automodule directives
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'myst_parser', # TODO: implement link from README.md to index.rst
]

# Mock imports for modules that might not be available at build time are no longer needed
# since we removed references to these modules

templates_path = ['_templates']
exclude_patterns = []

# Add this to your existing conf.py
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'special-members': '__init__',
}

# This tells autodoc to skip the module contents section
autodoc_default_flags = ['no-modules']

# This will prevent duplicate warnings
suppress_warnings = [
    'autodoc.duplicate_object_description',
    'autodoc.import_object',
    'docutils.nodes.title_reference',
    'docutils',  # Suppress all docutils warnings
]

# Disable docutils warnings about title underlines for Sphinx 
nitpicky = False
nitpick_ignore = [
    ('py:.*', '.*'),  # Ignore all Python references
    ('.*', 'Title underline too short'),  # Ignore title underline warnings
]

# Set up a warning filter to ignore docutils warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='docutils')

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
