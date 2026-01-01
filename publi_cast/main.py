import sys
import time
import os
import tempfile

# Add parent directory to path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import soundfile as sf

from publi_cast import config
from publi_cast.config import AUDACITY_COMMANDS
from publi_cast.repositories.audacity_repository import NamedPipe
from publi_cast.services.audacity_service import AudacityAPI
from publi_cast.services.logger_service import LoggerService
from publi_cast.controllers.import_controller import ImportController
from publi_cast.controllers.export_controller import ExportController
from publi_cast.gui.main_window import MainWindow
from publi_cast.audio.dynamic_compressor import DynamicCompressor

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
    sys.exit('PubliCast Error: Python 3.7 or later required')


# Global references for GUI mode
_logger = None
_named_pipe = None
_audacity_api = None
_import_controller = None
_export_controller = None
_main_window = None


def init_services():
    """Initialize all services."""
    global _logger, _named_pipe, _audacity_api, _import_controller, _export_controller, _main_window

    _logger = LoggerService()

    # Add GUI handler if window exists
    if _main_window:
        _logger.add_handler(_main_window.get_log_handler())

    _named_pipe = NamedPipe(_logger)
    _audacity_api = AudacityAPI(_named_pipe, _logger)
    _import_controller = ImportController(_logger)
    _export_controller = ExportController(_audacity_api, _logger)


def process_audio_file():
    """Process a single audio file - called from GUI."""
    global _logger, _named_pipe, _audacity_api, _import_controller, _export_controller

    # Initialize services if not already done
    if _logger is None:
        init_services()

    logger = _logger
    named_pipe = _named_pipe
    audacity_api = _audacity_api
    import_controller = _import_controller
    export_controller = _export_controller

    logger.info("Starting audio processing...")

    # First, try to start Audacity
    try:
        audacity_api.start_audacity()
    except Exception as e:
        logger.error(f"Error starting Audacity: {e}")
        return

    # Run diagnostic to check pipe availability
    logger.info("Checking pipe availability...")
    pipes_available = False

    try:
        # List all available pipes
        available_pipes = named_pipe.list_available_pipes()

        # Check if any Audacity-related pipes exist
        audacity_pipes = [p for p in available_pipes if 'audacity' in p.lower() or 'tosrv' in p.lower() or 'fromsrv' in p.lower()]
        if audacity_pipes:
            logger.info(f"Found {len(audacity_pipes)} Audacity pipe(s)")
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
            pipes_available = False

    # If pipes are not available, show a warning
    if not pipes_available:
        logger.warning("Audacity pipes not available. Continuing with manual processing.")

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

    # Temporary files for processing
    temp_eq_normalized_file = None
    temp_compressed_file = None
    use_python_compressor = config.COMPRESSOR_TYPE == "python"

    # Step 1: Commands for EQ and Normalize in Audacity (always first)
    # Order: Import → EQ → Normalize → (then compression)
    commands = [
        f'Import2:Filename="{audio_file}"',
        AUDACITY_COMMANDS['select_all'],
        config.build_filter_curve_command(),
        config.build_normalize_command(),
    ]

    # Add Audacity compressor only if NOT using Python compressor
    if not use_python_compressor:
        commands.append(config.build_compressor_command())
    
    # Execute each command and handle any command-specific errors
    try:
        logger.info("Starting command execution...")
        logger.info(f"Processing order: EQ → Normalize → {'Python Compressor' if use_python_compressor else 'Audacity Compressor'}")

        if pipes_available:
            # Use pipe API if available
            for command in commands:
                try:
                    logger.info(f"Executing command: {command}")
                    response = audacity_api.run_command(command)
                    logger.info(f"Command response: {response}")
                except Exception as cmd_error:
                    logger.error(f"Error executing command '{command}': {cmd_error}")

            # If using Python compressor, export from Audacity, apply compression, then re-export
            if use_python_compressor:
                try:
                    # Export EQ+Normalized audio from Audacity to temp file
                    temp_dir = tempfile.gettempdir()
                    base_name = os.path.splitext(os.path.basename(audio_file))[0]
                    temp_eq_normalized_file = os.path.join(temp_dir, f"{base_name}_eq_norm.wav")

                    logger.info("Exporting EQ+Normalized audio from Audacity...")
                    response = audacity_api.run_command(f'Export2: Filename="{temp_eq_normalized_file}" Format=WAV')
                    logger.info(f"Exported to: {temp_eq_normalized_file}")

                    # Wait a moment for file to be written
                    time.sleep(1)

                    # Load the EQ+Normalized audio
                    logger.info("Applying Python dynamic compressor...")
                    audio_data, sample_rate = sf.read(temp_eq_normalized_file)
                    logger.info(f"Loaded audio: {len(audio_data)} samples, {sample_rate}Hz")

                    # Create compressor with settings from config
                    compressor = DynamicCompressor(
                        compress_ratio=config.DYNAMIC_COMPRESSOR_SETTINGS['compress_ratio'],
                        hardness=config.DYNAMIC_COMPRESSOR_SETTINGS['hardness'],
                        floor=config.DYNAMIC_COMPRESSOR_SETTINGS['floor'],
                        noise_factor=config.DYNAMIC_COMPRESSOR_SETTINGS['noise_factor'],
                        scale_max=config.DYNAMIC_COMPRESSOR_SETTINGS['scale_max'],
                        sample_rate=sample_rate
                    )

                    # Apply compression
                    compressed_audio = compressor.process(audio_data, sample_rate)

                    # Save compressed audio to temp file
                    temp_compressed_file = os.path.join(temp_dir, f"{base_name}_compressed.wav")
                    sf.write(temp_compressed_file, compressed_audio, sample_rate)
                    logger.info(f"Python compression complete, saved to: {temp_compressed_file}")

                    # Remove current tracks and import compressed audio
                    audacity_api.run_command("RemoveTracks")
                    audacity_api.run_command(f'Import2:Filename="{temp_compressed_file}"')
                    audacity_api.run_command(AUDACITY_COMMANDS['select_all'])
                    logger.info("Compressed audio imported back into Audacity")

                except Exception as e:
                    logger.error(f"Error applying Python compressor: {e}")
                    logger.info("Audio remains with EQ and Normalize only (no compression)")
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

                # Build instruction message based on compressor type
                if use_python_compressor:
                    instructions = (
                        "Please perform the following steps in Audacity:\n\n"
                        "1. Select All (Ctrl+A)\n"
                        "2. Apply Filter Curve EQ (Effect > Filter Curve EQ)\n"
                        "3. Apply Normalize (Effect > Normalize)\n\n"
                        "NOTE: Python compression will be applied after export.\n"
                        "When finished, click OK to continue to export."
                    )
                else:
                    instructions = (
                        "Please perform the following steps in Audacity:\n\n"
                        "1. Select All (Ctrl+A)\n"
                        "2. Apply Filter Curve EQ (Effect > Filter Curve EQ)\n"
                        "3. Apply Normalize (Effect > Normalize)\n"
                        "4. Apply Compressor (Effect > Compressor)\n\n"
                        "When finished, click OK to continue to export."
                    )

                messagebox.showinfo("Manual Processing Required", instructions)
                root.destroy()
            except Exception as e:
                logger.error(f"Error opening audio file in Audacity: {e}")
                return

        # Prompt for audio output file selection (use input filename as default)
        try:
            output_path, format = export_controller.handle_export(audio_file)
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

                    if use_python_compressor:
                        # For manual mode with Python compressor, we need to apply it after export
                        messagebox.showinfo(
                            "Manual Export Required",
                            f"Please export the audio in Audacity as WAV first:\n\n"
                            f"1. File > Export > Export as WAV\n"
                            f"2. Save to a temporary location\n\n"
                            f"Python compression will be applied next."
                        )
                        root.destroy()

                        # Let user select the exported file
                        temp_export = import_controller.select_audio_file()
                        if temp_export:
                            # Apply Python compression
                            audio_data, sample_rate = sf.read(temp_export)
                            compressor = DynamicCompressor(
                                compress_ratio=config.DYNAMIC_COMPRESSOR_SETTINGS['compress_ratio'],
                                hardness=config.DYNAMIC_COMPRESSOR_SETTINGS['hardness'],
                                floor=config.DYNAMIC_COMPRESSOR_SETTINGS['floor'],
                                noise_factor=config.DYNAMIC_COMPRESSOR_SETTINGS['noise_factor'],
                                scale_max=config.DYNAMIC_COMPRESSOR_SETTINGS['scale_max'],
                                sample_rate=sample_rate
                            )
                            compressed_audio = compressor.process(audio_data, sample_rate)
                            sf.write(output_path, compressed_audio, sample_rate)
                            logger.info(f"Python compression applied and saved to: {output_path}")
                    else:
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
        # Only remove tracks, keep pipes open for next file
        try:
            if pipes_available:
                response = audacity_api.run_command("RemoveTracks")
            logger.info("Processing complete! Ready for next file.")
        except Exception as e:
            logger.error(f"Error removing tracks: {e}")

        # Cleanup temporary files
        for temp_file in [temp_eq_normalized_file, temp_compressed_file]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    logger.info(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Could not remove temporary file: {e}")


_cleanup_done = False

def cleanup():
    """Cleanup function called when exiting the program."""
    global _named_pipe, _audacity_api, _logger, _cleanup_done

    # Prevent double cleanup
    if _cleanup_done:
        return
    _cleanup_done = True

    if _logger:
        _logger.info("Closing application...")

    # First stop the pipe read thread (before closing Audacity)
    try:
        if _named_pipe:
            _named_pipe.close()
            if _logger:
                _logger.info("Pipes closed")
    except Exception as e:
        if _logger:
            _logger.error(f"Error closing pipes: {e}")

    # Then close Audacity
    try:
        if _audacity_api:
            _audacity_api.close_audacity()
            if _logger:
                _logger.info("Audacity closed")
    except Exception as e:
        if _logger:
            _logger.error(f"Error closing Audacity: {e}")


def main():
    """Main entry point - launches the GUI."""
    global _main_window, _logger

    # Create the main window with cleanup callback
    _main_window = MainWindow(process_audio_file, on_exit_callback=cleanup)

    # Initialize services
    init_services()

    # Run the GUI
    _main_window.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        cleanup()
