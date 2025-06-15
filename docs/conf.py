import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

# -- General configuration ------------------------------------------------

project = 'goit-pythonweb-hw--12'
author = 'Maryna Korbet'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',   
    'sphinx.ext.napoleon',   
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -----------------------------------------------------

html_theme = 'alabaster'  
html_static_path = ['_static']