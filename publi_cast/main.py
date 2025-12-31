import sys
import time
import os

from publi_cast import config
from publi_cast.config import AUDACITY_COMMANDS
from publi_cast.repositories.audacity_repository import NamedPipe
from publi_cast.services.audacity_service import AudacityAPI
from publi_cast.services.logger_service import LoggerService
from publi_cast.controllers.import_controller import ImportController
from publi_cast.controllers.export_controller import ExportController

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
    sys.exit('PubliCast Error: Python 3.7 or later required')

def main():
    logger = LoggerService()
    named_pipe = NamedPipe(logger)
    audacity_api = AudacityAPI(named_pipe, logger)
    import_controller = ImportController(logger)  
    export_controller = ExportController(audacity_api, logger)

    logger.info("Starting PubliCast application...")
    
    # First, try to start Audacity
    try:
        audacity_api.start_audacity()
    except Exception as e:
        logger.error(f"Error starting Audacity: {e}")
        return
    
    # Run diagnostic to check pipe availability
    logger.info("Running pipe diagnostic...")
    pipes_available = False
    
    try:
        # List all available pipes
        available_pipes = named_pipe.list_available_pipes()
        logger.info(f"Available pipes: {available_pipes}")
        
        # Check if any Audacity-related pipes exist
        audacity_pipes = [p for p in available_pipes if 'audacity' in p.lower() or 'tosrv' in p.lower() or 'fromsrv' in p.lower()]
        if audacity_pipes:
            logger.info(f"Found potential Audacity pipes: {audacity_pipes}")
            pipes_available = True
        else:
            logger.warning("No Audacity pipes found in system")
    except Exception as e:
        logger.error(f"Error checking pipe availability: {e}")
    
    # Try to open the pipe if pipes are available
    if pipes_available:
        try:
            logger.info("Opening named pipe...")
            named_pipe.open()
            logger.info("Named pipe opened successfully")
            
            # Initialize Audacity pipe
            audacity_api.set_pipe(named_pipe)
        except Exception as e:
            logger.error(f"Error opening named pipe: {e}")
            # Continue with fallback approach
            pipes_available = False
    
    # If pipes are not available, show a warning
    if not pipes_available:
        logger.warning("Audacity pipes not available. Please ensure mod-script-pipe is enabled in Audacity preferences.")
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askquestion(
            "Pipe Connection Failed",
            "Could not connect to Audacity via pipes. This may be due to:\n\n"
            "1. mod-script-pipe not being enabled in Audacity\n"
            "2. A compatibility issue with your version of Audacity\n\n"
            "Would you like to continue with manual processing?\n"
            "(This will require you to manually apply effects in Audacity)"
        )
        root.destroy()
        
        if result != 'yes':
            logger.info("User chose to exit application")
            return

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
        
        if pipes_available:
            # Use pipe API if available
            for command in commands:
                try:
                    logger.info(f"Executing command: {command}")
                    response = audacity_api.run_command(command)
                    logger.info(f"Command response: {response}")
                except Exception as cmd_error:
                    logger.error(f"Error executing command '{command}': {cmd_error}")
        else:
            # Manual fallback - just import the file and let user know what to do
            logger.info("Using manual fallback approach...")
            
            # Import the file
            import subprocess
            try:
                subprocess.Popen([config.AUDACITY_PATH, audio_file])
                logger.info(f"Opened audio file in Audacity: {audio_file}")
                
                # Show instructions to the user
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo(
                    "Manual Processing Required",
                    "Please perform the following steps in Audacity:\n\n"
                    "1. Select All (Ctrl+A)\n"
                    "2. Apply Filter Curve EQ (Effect > Filter Curve EQ)\n"
                    "3. Apply Normalize (Effect > Normalize)\n"
                    "4. Apply Compressor (Effect > Compressor)\n\n"
                    "When finished, click OK to continue to export."
                )
                root.destroy()
            except Exception as e:
                logger.error(f"Error opening audio file in Audacity: {e}")
                return

        # Prompt for audio output file selection
        try:
            output_path, format = export_controller.handle_export()
        except Exception as export_error:
            logger.error(f"Error handling export: {export_error}")
            output_path = None

        if output_path:
            try:
                if pipes_available:
                    # Use pipe API if available
                    if format == '.mp3':
                        response = audacity_api.run_command(f'Export2: Filename="{output_path}" Format=MP3 Bitrate=320 Quality=0 VarMode=0 JointStereo=1 ForceMono=0')
                    else:
                        response = audacity_api.run_command(f'Export2: Filename="{output_path}" Format=WAV')
                    logger.info(f"Audio exported successfully to: {output_path}")
                else:
                    # Manual fallback - instruct user to export
                    import tkinter as tk
                    from tkinter import messagebox
                    
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showinfo(
                        "Manual Export Required",
                        f"Please export the audio in Audacity:\n\n"
                        f"1. File > Export > Export as {format[1:].upper()}\n"
                        f"2. Save to: {output_path}\n\n"
                        f"When finished, click OK to continue."
                    )
                    root.destroy()
                    logger.info(f"User instructed to export audio to: {output_path}")
            except Exception as export_cmd_error:
                logger.error(f"Error exporting audio: {export_cmd_error}")
        else:
            logger.info("Export cancelled by user")

    except Exception as e:
        logger.error(f"Error during command execution loop: {e}")
    finally:
        try:
            if pipes_available:
                response = audacity_api.run_command("RemoveTracks")
                time.sleep(1)
                audacity_api.close_audacity()
                named_pipe.close()
            else:
                # Just show a message to close Audacity
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo(
                    "Processing Complete",
                    "Processing is complete. You can now close Audacity."
                )
                root.destroy()
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
