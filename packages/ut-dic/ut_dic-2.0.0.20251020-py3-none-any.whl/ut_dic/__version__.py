"""Version module
Attributes:
    __title__: package title
    __description__: package description
    __url__: project url
    __version__: package version
    __build__: package build id
    __author__: package author
    __author_email__: email of package author
    __license__: package license
    __copyright__: package copyright
    __cake__: package cake
"""
from datetime import datetime
_now = datetime.now().strftime("%Y%m%d")

__title__ = 'ut_dic'
__description__ = 'Utilities for Dictionaries.'
__url__ = 'https://ut_dic.readthedocs.io/en/latest'
__version__ = f'2.0.0.{_now}'
__build__ = _now
__author__ = 'Bernd Stroehle'
__author_email__ = 'bernd.stroehle@gmail.com'
__license__ = 'GPL-3.0-only WITH Classpath-Exception-2.0 OR BSD-3-Clause'
__copyright__ = 'Copyright 2025 Bernd Stroehle'
__cake__ = u'\u2728 \U0001f370 \u2728'
