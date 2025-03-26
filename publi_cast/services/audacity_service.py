import subprocess
import time
import threading
import queue
import sys
import os
import soundfile as sf
import psutil
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
         # First, check if Audacity is already running and close it
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if 'audacity' in proc_name:
                    self.logger.info("Audacity is already running. Closing it...")
                    try:
                        # Try to close gracefully
                        proc.terminate()
                        
                        # Wait up to 5 seconds for the process to terminate
                        gone, alive = psutil.wait_procs([proc], timeout=5)
                        
                        # If still alive, force kill
                        if alive:
                            self.logger.warning("Audacity didn't close gracefully, forcing termination")
                            proc.kill()
                            # Wait a bit more to ensure it's fully closed
                            time.sleep(1)
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                        self.logger.error(f"Error closing Audacity: {e}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Wait a moment to ensure ports are freed
        time.sleep(2)
        
        for attempt in range(retry_attempts):
            try:
                self.logger.info(f"Starting Audacity... (Attempt {attempt + 1}/{retry_attempts})")
                
                # Start Audacity depending on the OS
                if sys.platform == "win32":
                    process = subprocess.Popen(AUDACITY_PATH)
                else:
                    process = subprocess.Popen([AUDACITY_PATH], shell=False)

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
    
    def get_audio_data(self):
        """
        Retrieves audio data from Audacity by exporting to a temporary file and reading it back.
        
        Returns:
            Return Tuple: audio_data: np.ndarray, - The audio samples
        
        Raises:
            RuntimeError: If export command fails
            FileNotFoundError: If temporary file cannot be accessed
            IOError: If there are issues reading the audio file
        """
        # Define temporary file path
        temp_file = "temp_audio.wav"
        
        try:        
            # Export current Audacity selection to temporary WAV file
            export_command = f'Export2: Filename="{temp_file}"'
            response = self.run_command(export_command)
            
            if not response or "Error" in response:
                raise RuntimeError(f"Failed to export audio: {response}")
                
            # Read the exported audio file
            audio_data, _ = sf.read(temp_file)
            
            return audio_data
            
        except FileNotFoundError:
            self.logger.error(f"Temporary file {temp_file} not found")
            raise
        except IOError as e:
            self.logger.error(f"Error reading audio file: {e}")
            raise
        finally:
            # Clean up temporary file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError as e:
                    self.logger.warning(f"Failed to remove temporary file: {e}")

    def close_audacity(self):
        """
        Closes the Audacity application gracefully if it's running.
        
        This method first checks if Audacity is running, and if so:
        1. Tries to send a command to close Audacity
        2. If that fails, finds and closes the Audacity window using pygetwindow
        3. Logs the outcome of the operation
        
        Returns:
            bool: True if Audacity was closed successfully or wasn't running, 
                False if it failed to close Audacity
        """
        
        time.sleep(1)
        
        # First check if Audacity is running via process name
        audacity_running = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'audacity' in proc.info['name'].lower():
                    audacity_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if not audacity_running:
            self.logger.info("Audacity is not running - no need to close")
            return True
        
        self.logger.info("Audacity is running - attempting to close...")
        
        try:
            # Try to close Audacity using a command
            response = self.run_command("Close")
            time.sleep(2)  # Wait longer to ensure it has time to close
            
            # Check if Audacity is still running via process
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'audacity' in proc.info['name'].lower():
                        # If still running, terminate the process
                        self.logger.info(f"Terminating Audacity process (PID: {proc.info['pid']})")
                        proc.terminate()
                        proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    self.logger.error(f"Error terminating Audacity: {e}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error while trying to close Audacity: {e}")
            return False