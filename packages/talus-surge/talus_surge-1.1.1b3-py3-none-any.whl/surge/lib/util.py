# -*- coding: utf-8 -*-
import os


# Check whether is in debugging mode.
DEBUG_MODE: bool = os.environ.get("SURGE_DEBUG") == "1"
