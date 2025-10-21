from .FlexiKitMath import math
from .FlexiKitTime import time
from .FlexiKitDLL import DLL
from .FlexiKitUI import UI

# Example package metadata
__version__ = "0.1.0"
__author__ = "Zachary Sherwood"

# The `__all__` list is good practice for controlling wildcard imports.
# In this case, you probably want to expose all your main classes.
__all__ = ["FlexiKitMath", "time", "DLL", "UI"]
