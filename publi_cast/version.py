# -*- coding: utf-8 -*-
"""
PubliCast - Version information
"""

__version__ = "0.2.1"
__app_name__ = "PubliCast"
__description__ = "Audio processing application that automates audio enhancement using Audacity"

def get_version():
    """Get the application version."""
    return __version__

def get_app_name():
    """Get the application name."""
    return __app_name__

def get_full_version():
    """Get the full version string."""
    return f"{__app_name__} v{__version__}"
