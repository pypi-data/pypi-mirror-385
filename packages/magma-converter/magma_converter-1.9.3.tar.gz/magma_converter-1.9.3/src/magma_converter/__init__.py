#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pkg_resources import get_distribution

from .convert import Convert
from .plotly_calplot import calplot

__version__ = get_distribution("magma-converter").version
__author__ = "Martanto"
__author_email__ = "martanto@live.COM"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2024, MAGMA Indonesia"
__url__ = "https://github.com/martanto/cvghm-multigas"

__all__ = [
    "Convert",
    "calplot",
]
