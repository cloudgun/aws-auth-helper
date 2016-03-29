import os

extensions = [
    'sphinx.ext.autodoc',
]
templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'
project = u'aws-auth-helper'
copyright = u'2016, Drew J. Sonne'

author = u'Drew J. Sonne'
version = u'1.4'
release = u'1.4.0'
language = 'en'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
html_title = u'aws-auth-helper v1.4.0'
html_static_path = ['_static']
htmlhelp_basename = 'aws-auth-helperdoc'
latex_elements = {}
latex_documents = [
    (master_doc, 'aws-auth-helper.tex', u'aws-auth-helper Documentation',
     u'Drew J. Sonne', 'manual'),
]
man_pages = [
    (master_doc, 'aws-auth-helper', u'aws-auth-helper Documentation',
     [author], 1)
]

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
