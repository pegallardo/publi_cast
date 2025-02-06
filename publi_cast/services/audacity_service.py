import subprocess
import time
import threading
import queue
import sys
import os
from config import AUDACITY_PATH, DEFAULT_RETRY_ATTEMPTS, DEFAULT_RETRY_DELAY, EOL

class AudacityAPI:
    def __init__(self, named_pipe, logger):
        self.named_pipe = named_pipe
        self.logger = logger
        self.pipe = None
        self.logger.info("Initialized AudacityAPI")
        
        # Queue to store pipe responses
        self.response_queue = queue.Queue()
        self.read_thread = None

    def start_audacity(self, retry_attempts=DEFAULT_RETRY_ATTEMPTS, retry_delay=DEFAULT_RETRY_DELAY):
        for attempt in range(retry_attempts):
            try:
                self.logger.info(f"Starting Audacity... (Attempt {attempt + 1}/{retry_attempts})")
                
                # Start Audacity depending on the OS
                if sys.platform == "win32":
                    process = subprocess.Popen(AUDACITY_PATH)
                else:
                    process = subprocess.Popen([AUDACITY_PATH])

                time.sleep(retry_delay)
                
                # Check if process is running
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
        
        # Start non-blocking read thread
        self.read_thread = threading.Thread(target=self._read_pipe_thread, daemon=True)
        self.read_thread.start()

    def _read_pipe_thread(self):
        """Thread to continuously read the pipe and store responses in the queue."""
        while True:
            if self.pipe:
                response = self.pipe.read()
                if response:
                    self.response_queue.put(response)
            time.sleep(0.1)  # Pause to reduce CPU usage

    def run_command(self, command, timeout=5):
        if not self.pipe:
            error_msg = "Pipe not set"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            self.logger.info(f"Running Audacity command: {command}")
            self.pipe.write(command + EOL)

            start_time = time.time()

            # Wait for response or timeout
            while True:
                try:
                    # Get response from queue with timeout to avoid blocking
                    decoded_response = self.response_queue.get(timeout=timeout)
                    print("Received response:", decoded_response)
                    break
                except queue.Empty:
                    if time.time() - start_time > timeout:
                        print("Timeout: no response.")
                        decoded_response = None
                        break
                time.sleep(0.1)  # Pause to avoid CPU overload
            
            # Check response for specific errors
            if decoded_response and ("FileNotFound" in decoded_response or "Error:" in decoded_response):
                error_msg = f"Audacity command failed: {decoded_response}"
                self.logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            self.logger.info(f"Command response received: {decoded_response}")
            return decoded_response
            
        except FileNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error running command: {e}")
            raise


# Named Pipe Class for Cross-Platform Pipe Handling
class NamedPipe:
    def __init__(self, logger):
        self.logger = logger
        if sys.platform == "win32":
            import win32file
            import pywintypes
            self.win32file = win32file
            self.pywintypes = pywintypes
        self.pipe_in = None
        self.pipe_out = None
        self.logger.info("Initialized NamedPipe")

    def open(self, pipe_to_audacity, pipe_from_audacity):
        if sys.platform == "win32":
            # Windows named pipe handling
            try:
                self.pipe_in = self.win32file.CreateFile(
                    pipe_to_audacity,
                    self.win32file.GENERIC_WRITE,
                    0,
                    None,
                    self.win32file.OPEN_EXISTING,
                    0,
                    None
                )
                self.pipe_out = self.win32file.CreateFile(
                    pipe_from_audacity,
                    self.win32file.GENERIC_READ,
                    0,
                    None,
                    self.win32file.OPEN_EXISTING,
                    0,
                    None
                )
                self.logger.info("Pipes opened successfully on Windows")
            except self.pywintypes.error as e:
                self.logger.error(f"Failed to open pipes: {e}")
                raise
        else:
            # Unix-based systems (macOS, Linux) FIFO handling
            if not os.path.exists(pipe_to_audacity):
                os.mkfifo(pipe_to_audacity)
            if not os.path.exists(pipe_from_audacity):
                os.mkfifo(pipe_from_audacity)
                
            self.pipe_in = open(pipe_to_audacity, 'w')
            self.pipe_out = open(pipe_from_audacity, 'r')
            self.logger.info("Pipes opened successfully on Unix-based system")

    def close(self):
        try:
            self.logger.info("Closing pipes...")
            if self.pipe_in:
                self.pipe_in.close()
            if self.pipe_out:
                self.pipe_out.close()
            self.logger.info("Pipes closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing pipes: {e}")
            raise

    def write(self, message: str):
        if sys.platform == "win32":
            self.win32file.WriteFile(self.pipe_in, message.encode() + b'\n')
        else:
            self.pipe_in.write(message + '\n')
            self.pipe_in.flush()

    def read(self) -> str:
        if sys.platform == "win32":
            result, data = self.win32file.ReadFile(self.pipe_out, 4096)
            return data.decode().strip() if result == 0 else ""
        else:
            return self.pipe_out.readline().strip()
