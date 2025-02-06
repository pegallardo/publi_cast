import sys
import pygetwindow as gw
from repositories.audacity_repository import NamedPipe
from services.audacity_service import AudacityAPI
from services.logger_service import LoggerService
from services.compressor_service import Compressor
from controllers.import_controller import ImportController
from controllers.export_controller import ExportController

from config import COMPRESSION_SETTINGS

if sys.version_info[0] < 3 and sys.version_info[1] < 7:
    sys.exit('PipeClient Error: Python 3.7 or later required')

def main():
    logger = LoggerService()
    named_pipe = NamedPipe(logger)
    audacity_api = AudacityAPI(named_pipe, logger)
    import_controller = ImportController(logger)  
    export_controller = ExportController(audacity_api, logger)
    compressor = Compressor(**COMPRESSION_SETTINGS)

    logger.info("Starting Publi_Cast application...")
    audacity_api.start_audacity()
    # Minimize the window
    audacity_window = gw.getWindowsWithTitle('Audacity')
    if audacity_window:
        audacity_window[0].minimize()
    else:
        print("Audacity window not found.")
        logger.info("Application completed successfully")

    try:
        logger.info("Opening named pipe...")
        named_pipe.open()
        logger.info("Named pipe opened successfully")
    except Exception as e:
        logger.error(f"Error opening named pipe: {e}")
        return

    # Initialize Audacity pipe
    audacity_api.set_pipe(named_pipe)

    # Prompt for audio file selection
    try:
        logger.info("Prompting user to select audio file...")
        audio_file = import_controller.select_audio_file()
        if not audio_file:
            logger.info("Audio file selection cancelled")
            return
        logger.info(f"Selected audio file: {audio_file}")
    except Exception as e:
        logger.error(f"Error selecting audio file: {e}")
        return

    # Commands to be sent to Audacity
    commands = [
        f'Import2:Filename="{audio_file}"',
        'SelectAll',
        'Filter Curve EQ:FilterType=Draw Points="20 15; 100 12; 500 6; 1000 0; 10000 0; 20000 -3"',
        'Normalize:RemoveDcOffset=True PeakLevel=-1.0 NormalizeStereo=False'
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

        try:
            logger.info("Applying compression...")
            # See config.py for compression settings
            response = compressor.process_direct(response)
            logger.info(f"Command response after compression: {response}")
            
        except ValueError as ve:
            logger.error(f"Invalid values for compression: {ve}")
        except TypeError as te:
            logger.error(f"Invalid data type for compression: {te}")
        except Exception as e:
            logger.error(f"Unexpected error during compression: {e}")
        
        # Handle export with dialog
        output_path = export_controller.handle_export()
        if output_path:
            logger.info(f"Audio exported successfully to: {output_path}")
        else:
            logger.info("Export cancelled by user")

    except Exception as e:
        logger.error(f"Error during command execution loop: {e}")
    finally:
        try:
            named_pipe.close()
            logger.info("Named pipe closed successfully")
        except Exception as close_error:
            logger.error(f"Error closing named pipe: {close_error}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger = LoggerService()
        logger.error(f"Unexpected error: {e}")
        print(e)