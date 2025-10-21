# Configuration file for the Sphinx documentation builder.

extensions = []

project = 'Spin'
copyright = '2024- by Georg Brandl, Enrico Faulhaber, Alexander Zaft'  # noqa: A001
author = 'Georg Brandl, Enrico Faulhaber, Alexander Zaft'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

master_doc = 'index'
default_role = 'literal'
highlight_language = 'python'

html_theme = 'furo'
html_logo = '_static/logo.png'
html_theme_options = {
    'light_css_variables': {
        'font-stack': 'Open Sans, DejaVu Sans, sans-serif',
    },
}
html_static_path = ['_static']
