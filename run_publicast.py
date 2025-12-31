# -*- coding: utf-8 -*-
"""
PubliCast - Entry point for PyInstaller
"""
import sys
import os

# Add the project root to the path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = os.path.dirname(sys.executable)
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)

# Now import and run the main module
from publi_cast.main import main

if __name__ == "__main__":
    main()

