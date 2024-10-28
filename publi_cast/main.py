import subprocess
import sys
import time
import os
from dialogs.audio_dialog import select_audio_file
from repositories.audacity_repository import NamedPipe
from services.audacity_service import AudacityAPI
from services.logger_service import LoggerService

if sys.version_info[0] < 3 and sys.version_info[1] < 7:
    sys.exit('PipeClient Error: Python 2.7 or later required')

AUDACITY_PATH = "C:\\Program Files\\Audacity\\audacity.exe"

# Platform specific constants
if sys.platform == 'win32':
    PIPE_TO_AUDACITY = '\\\\.\\pipe\\ToSrvPipe'
    PIPE_FROM_AUDACITY = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
else:
    # Linux or Mac
    PIPE_BASE = '/tmp/audacity_script_pipe.'
    PIPE_TO_AUDACITY = PIPE_BASE + 'to.' + str(os.getuid())
    PIPE_FROM_AUDACITY = PIPE_BASE + 'from.' + str(os.getuid())
    EOL = '\n'

# Initialize the logger at the top level
logger = LoggerService()

def start_audacity():
    try:
        logger.info("Starting Audacity...")
        subprocess.Popen(AUDACITY_PATH)
        time.sleep(5)
        logger.info("Audacity started successfully")
    except subprocess.SubprocessError as e:
        error_message = f"Error starting Audacity: {e}"
        logger.error(error_message)
        raise RuntimeError(error_message)

def main():
    # Initialize named pipe with logging support
    named_pipe = NamedPipe(PIPE_TO_AUDACITY, PIPE_FROM_AUDACITY, logger)

    # Check if pipe paths exist
    for pipe_path in [PIPE_TO_AUDACITY, PIPE_FROM_AUDACITY]:
        if not os.path.exists(pipe_path):
            logger.error(f"Pipe path {pipe_path} does not exist.")
            return

    try:
        logger.info("Opening named pipe...")
        named_pipe.open()
        logger.info("Named pipe opened successfully")
    except Exception as e:
        logger.error(f"Error opening named pipe: {e}")
        return

    # Initialize Audacity API and set pipe
    audacity_api = AudacityAPI()
    audacity_api.set_pipe(named_pipe)

    # Prompt for audio file selection
    try:
        logger.info("Prompting user to select audio file...")
        audio_file = select_audio_file(logger)
        logger.info(f"Selected audio file: {audio_file}")
    except Exception as e:
        logger.error(f"Error selecting audio file: {e}")
        return

    # Commands to be sent to Audacity
    commands = [
        f"Import2:Filename='{audio_file}'",
        "SelectAll",
        "Amplify:Ratio=2",
        "Normalize:PeakLevel=-3.0",
        "Echo:Delay=0.5 Decay=0.5",
        "BassAndTreble:BassGain=5 TrebleGain=-5",
        "Compressor:Threshold=-20 NoiseFloor=-40 Ratio=2.5 AttackTime=0.2 DecayTime=1.0",
        "Reverb:Reverb=50 RoomSize=100",
        "Export2:Filename='output.wav' NumChannels=2",
    ]

    # Execute each command and handle any command-specific errors
    try:
        logger.info("Starting command execution...")
        for command in commands:
            try:
                logger.info(f"Executing command: {command}")
                response = audacity_api.run_command(command)
                logger.info(f"Command response: {response}")
            except Exception as cmd_error:
                logger.error(f"Error executing command '{command}': {cmd_error}")
    except Exception as e:
        logger.error(f"Error during command execution loop: {e}")
    finally:
        # Attempt to close named pipe and log any issues
        try:
            named_pipe.close()
            logger.info("Named pipe closed successfully")
        except Exception as close_error:
            logger.error(f"Error closing named pipe: {close_error}")

if __name__ == "__main__":
    try:
        logger.info("Starting Publi_Cast application...")
        start_audacity()
        main()
        logger.info("Application completed successfully")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(e)
