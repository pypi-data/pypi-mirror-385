# -*- coding: utf-8 -*-
import os

# Get the current module directory.
DIR_SURGE: str = os.path.dirname(os.path.dirname(__file__))
# Get the library used offline static files.
DIR_SURGE_STATIC: str = os.path.join(DIR_SURGE, 'static')