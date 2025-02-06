import os
import sys

if sys.platform == 'win32':
    PIPE_TO_AUDACITY = '\\\\.\\pipe\\ToSrvPipe'
    PIPE_FROM_AUDACITY = '\\\\.\\pipe\\FromSrvPipe'
else:
    PIPE_BASE = '/tmp/audacity_script_pipe.'
    PIPE_TO_AUDACITY = PIPE_BASE + 'to.' + str(os.getuid())
    PIPE_FROM_AUDACITY = PIPE_BASE + 'from.' + str(os.getuid())

EOL = '\r\n\0' if sys.platform == 'win32' else '\n'

AUDACITY_PATH = "C:\\Program Files\\Audacity\\audacity.exe"

DEFAULT_RETRY_ATTEMPTS = 5
DEFAULT_RETRY_DELAY = 1  # seconds

# Compression settings
COMPRESSION_SETTINGS = {
    'compress_ratio': 0.8,
    'hardness': 0.879,
    'floor': -18,
    'noise_factor': 0,
    'scale_max': 0.99
}