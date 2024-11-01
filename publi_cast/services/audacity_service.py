import subprocess
import time
import win32file
from config import AUDACITY_PATH, DEFAULT_RETRY_ATTEMPTS, DEFAULT_RETRY_DELAY

class AudacityAPI:
    def __init__(self, named_pipe, logger):
        self.named_pipe = named_pipe
        self.logger = logger
        self.pipe = None
        self.logger.info("Initialized AudacityAPI")

    def start_audacity(self, retry_attempts=DEFAULT_RETRY_ATTEMPTS, retry_delay=DEFAULT_RETRY_DELAY):
        for attempt in range(retry_attempts):
            try:
                self.logger.info(f"Starting Audacity... (Attempt {attempt + 1}/{retry_attempts})")
                process = subprocess.Popen(AUDACITY_PATH)
                time.sleep(retry_delay)
                
                # Verify process is running
                if process.poll() is None:
                    self.logger.info("Audacity started successfully")
                    return process
                
                self.logger.warning(f"Audacity failed to start on attempt {attempt + 1}")
                
            except subprocess.SubprocessError as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                continue
        
        error_message = f"Failed to start Audacity after {retry_attempts} attempts"
        self.logger.error(error_message)
        raise RuntimeError(error_message)

    def set_pipe(self, pipe):
        self.pipe = pipe
        self.logger.info("Pipe set for AudacityAPI")

    def run_command(self, command):
        if not self.pipe:
            error_msg = "Pipe not set"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            self.logger.info(f"Running Audacity command: {command}")
            encoded_command = (command + '\n').encode('utf-8')
            win32file.WriteFile(self.pipe.pipe_in, encoded_command)
            
            response = win32file.ReadFile(self.pipe.pipe_out, 4096)[1]
            decoded_response = response.decode('utf-8')
            self.logger.info(f"Command response received: {decoded_response}")
            
            return decoded_response
        except Exception as e:
            self.logger.error(f"Error running command: {e}")
            raise