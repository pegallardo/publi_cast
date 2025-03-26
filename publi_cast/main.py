import sys
import config
import time
from repositories.audacity_repository import NamedPipe
from services.audacity_service import AudacityAPI
from services.logger_service import LoggerService
from controllers.import_controller import ImportController
from controllers.export_controller import ExportController
from config import AUDACITY_COMMANDS

if sys.version_info[0] < 3 and sys.version_info[1] < 7:
    sys.exit('PipeClient Error: Python 3.7 or later required')

def main():
    logger = LoggerService()
    named_pipe = NamedPipe(logger)
    audacity_api = AudacityAPI(named_pipe, logger)
    import_controller = ImportController(logger)  
    export_controller = ExportController(audacity_api, logger)

    logger.info("Starting PubliCast application...")
    audacity_api.start_audacity()
    
    try:
        logger.info("Opening named pipe...")
        named_pipe.open()
        logger.info("Named pipe opened successfully")
    except Exception as e:
        logger.error(f"Error opening named pipe: {e}")
        return

    # Initialize Audacity pipe
    audacity_api.set_pipe(named_pipe)

    # Prompt for audio input file selection
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
    AUDACITY_COMMANDS['select_all'],
    config.build_filter_curve_command(),
    config.build_normalize_command(),
    config.build_compressor_command()
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

        # Prompt for audio output file selection
        try:
            output_path, format = export_controller.handle_export()
        except Exception as export_error:
            logger.error(f"Error handling export: {export_error}")
            output_path = None

        if output_path:
            try:
                if format == '.mp3':
                    response = audacity_api.run_command(f'Export2: Filename="{output_path}" Format=MP3 Bitrate=320 Quality=0 VarMode=0 JointStereo=1 ForceMono=0')
                else:
                    response = audacity_api.run_command(f'Export2: Filename="{output_path}" Format=WAV')        
                logger.info(f"Audio exported successfully to: {output_path}")
            except Exception as export_cmd_error:
                logger.error(f"Error exporting audio: {export_cmd_error}")
        else:
            logger.info("Export cancelled by user")

    except Exception as e:
        logger.error(f"Error during command execution loop: {e}")
    finally:
        try:
            response = audacity_api.run_command("RemoveTracks")
            time.sleep(1)
            audacity_api.close_audacity()
            named_pipe.close()
        except OSError as close_error:
            logger.error(f"Error closing named pipe: {close_error}")
        except Exception as unexpected_error:
            logger.error(f"Unexpected error closing named pipe: {unexpected_error}")
            
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger = LoggerService()
        logger.error(f"Unexpected error: {e}")
        print(e)