from services.logger_service import LoggerService
import win32file

logger = LoggerService()

class AudacityAPI:
    def __init__(self):
        self.pipe = None
        logger.info("Initialized AudacityAPI")

    def set_pipe(self, pipe):
        self.pipe = pipe
        logger.info("Pipe set for AudacityAPI")

    def run_command(self, command):
        if not self.pipe:
            error_msg = "Pipe not set"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            # Replace backslashes with forward slashes and escape special characters
            if "Import2:Filename=" in command:
                file_path = command.split("Import2:Filename=")[1].strip("'")
                safe_path = file_path.replace("\\", "/").replace('"', '\\"')
                command = f'Import2:Filename="{safe_path}"'

            logger.info(f"Running Audacity command: {command}")
            encoded_command = (command + '\n').encode('utf-8')
            win32file.WriteFile(self.pipe.pipe_in, encoded_command)
            
            response = win32file.ReadFile(self.pipe.pipe_out, 4096)[1]
            decoded_response = response.decode('utf-8')
            logger.info(f"Command response received: {decoded_response}")
            
            return decoded_response
        except Exception as e:
            logger.error(f"Error running command: {e}")
            raise