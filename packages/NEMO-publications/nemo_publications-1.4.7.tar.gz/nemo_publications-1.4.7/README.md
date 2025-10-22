[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/NEMO-Publications?label=python)](https://www.python.org/downloads/release/python-3110/)
[![PyPI](https://img.shields.io/pypi/v/nemo-publications?label=pypi%20version)](https://pypi.org/project/NEMO-Publications/)
<img src="https://img.shields.io/pypi/dm/nemo-publications?color=blue&label=pypi%20downloads">

# NEMO Publications

This plugin for NEMO adds the ability to manage Publications.
* Search and add publication using DOI
* Link publications to authors (NEMO Users), Tools and Projects

# Compatibility:

### NEMO-Publications >= 1.0.0
* NEMO >= 4.7.0
* NEMO-CE >= 1.7.0

# Installation

`pip install NEMO-publications`

# Add NEMO Publications

in `settings.py` add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    '...',
    'NEMO_publications',
    '...'
    'NEMO',
    '...'
]
```

# Usage
Add choice to "Landing page choices" in Detailed Administration
* Set URL to `/publications/`
* Use suggested icon located in `resources/icons/publications.png`

For the publication jumbotron, you can use the URL `/publications/jumbotron/`

# Customizations
Go to `Customization -> Publications` to enable the landing page widget and set parameters for the carousel like interval time and number of recent publications to display. 

# Settings
The following settings are used by default:

```python
PUBLICATION_SETTINGS = {
    "timeout": 15,
    "doi_search_url": "http://dx.doi.org/{}",
    "headers": [
        {"Accept": "application/x-bibtex"}, 
        {"Accept": "text/bibliography; style=bibtex"}
    ]
}
```

To override any of them, simply add the ones you want to replace in `settings.py` as follows:
```python
PUBLICATION_SETTINGS = {
    "timeout": 45, # Increase timeout to 45s
}
```