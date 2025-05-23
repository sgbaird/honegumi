"""
    Dummy conftest.py for core.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest
import sys

# Monkeypatch numpy to add NaN (uppercase) as an alias for nan (lowercase)
# to fix compatibility issues with ax-platform on Python 3.9
if sys.version_info < (3, 10):
    import numpy
    if not hasattr(numpy, 'NaN'):
        numpy.NaN = numpy.nan
