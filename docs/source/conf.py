
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'charleston'
copyright = '2026, Charlie'
author = 'Charlie'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.todo',
]

autodoc_mock_imports = ['win32cred', 'win32con', 'pywintypes'] #windows only

autodoc_member_order = 'bysource'

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
html_static_path = ['_static']
