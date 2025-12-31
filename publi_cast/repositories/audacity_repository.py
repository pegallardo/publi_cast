from abc import ABC, abstractmethod
import os
import sys
import time
import threading
import queue
import win32file
import pywintypes

from publi_cast import config
from publi_cast.config import PIPE_TO_AUDACITY, PIPE_FROM_AUDACITY
from publi_cast.services.logger_service import LoggerService

logger = LoggerService()

class Pipe(ABC):
    @abstractmethod
    def open(self) -> str:
        pass

    @abstractmethod
    def close(self) -> str:
        pass

    @abstractmethod
    def write(self, message: str):
        pass

    @abstractmethod
    def read(self) -> str:
        pass

class NamedPipe(Pipe):
    def __init__(self, logger):
        self.pipe_to_audacity = PIPE_TO_AUDACITY
        self.pipe_from_audacity = PIPE_FROM_AUDACITY
        self.pipe_in = None
        self.pipe_out = None
        self.logger = logger
        self.response_queue = queue.Queue()
        self.read_thread = None
        self.running = False
        self.logger.info(f"Initialized NamedPipe with to={self.pipe_to_audacity}, from={self.pipe_from_audacity}")

    def is_open(self):
        """Check if the pipe is already open and connected."""
        return self.pipe_in is not None and self.pipe_out is not None and self.running

    def open(self):
        # Skip if already open
        if self.is_open():
            self.logger.info("Pipe already open, reusing existing connection")
            return

        # Active wait for pipes to be created (max 30 seconds, check every 0.5s)
        self.logger.info("Waiting for Audacity pipes to be created...")
        max_wait_seconds = 30
        check_interval = 0.5
        elapsed = 0

        while elapsed < max_wait_seconds:
            all_pipes = self.list_available_pipes()
            audacity_pipes = [p for p in all_pipes if 'audacity' in p.lower() or 'tosrv' in p.lower() or 'fromsrv' in p.lower()]

            if audacity_pipes:
                self.logger.info(f"Audacity pipes detected after {elapsed:.1f}s")
                break

            time.sleep(check_interval)
            elapsed += check_interval

            # Log progress every 5 seconds
            if elapsed % 5 < check_interval:
                self.logger.info(f"Still waiting for pipes... ({elapsed:.0f}s / {max_wait_seconds}s)")

        all_pipes = self.list_available_pipes()
        
        # Try all possible pipe naming conventions
        pipe_pairs = [
            (self.pipe_to_audacity, self.pipe_from_audacity),
            (config.ALT_PIPE_TO_AUDACITY, config.ALT_PIPE_FROM_AUDACITY) if hasattr(config, 'ALT_PIPE_TO_AUDACITY') else (None, None),
            (config.WIN11_PIPE_TO_AUDACITY, config.WIN11_PIPE_FROM_AUDACITY) if hasattr(config, 'WIN11_PIPE_TO_AUDACITY') else (None, None)
        ]
        
        for to_pipe, from_pipe in pipe_pairs:
            if to_pipe and from_pipe:
                self.logger.info(f"Trying pipe pair: {to_pipe}, {from_pipe}")
                try:
                    if self.try_connect_pipes(to_pipe, from_pipe):
                        self.logger.info(f"Successfully connected to pipes: {to_pipe}, {from_pipe}")
                        return
                except Exception as e:
                    self.logger.error(f"Error connecting to pipes {to_pipe}, {from_pipe}: {e}")
        
        # If we get here, try a more aggressive approach - look for ANY pipes
        self.logger.info("Trying to find ANY available pipes...")
        for pipe in all_pipes:
            if 'audacity' in pipe.lower() or 'pipe' in pipe.lower():
                full_pipe = r'\\.\pipe\\' + pipe
                self.logger.info(f"Trying to connect to pipe: {full_pipe}")
                try:
                    # Try this as both input and output
                    self.pipe_in = win32file.CreateFile(
                        full_pipe,
                        win32file.GENERIC_WRITE,
                        0, None, win32file.OPEN_EXISTING, 0, None
                    )
                    self.logger.info(f"Successfully connected to pipe as input: {full_pipe}")
                    break
                except Exception as e:
                    self.logger.error(f"Failed to connect to pipe as input: {e}")
        
        # If we still can't connect, raise an error with detailed information
        self.logger.error("Failed to connect to any Audacity pipes")
        error_message = (
            "Could not connect to Audacity pipes. Please ensure:\n"
            "1. Audacity is running\n"
            "2. mod-script-pipe is enabled in Preferences > Modules\n"
            "3. You've restarted Audacity after enabling mod-script-pipe\n"
            "4. You're running this application with the same privileges as Audacity\n"
            f"Available pipes: {all_pipes}"
        )
        raise RuntimeError(error_message)

    def try_connect_pipes(self, to_pipe, from_pipe):
        try:
            self.logger.info(f"Opening pipes to Audacity: {to_pipe}, {from_pipe}")
            self.pipe_in = win32file.CreateFile(
                to_pipe,
                win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            self.pipe_out = win32file.CreateFile(
                from_pipe,
                win32file.GENERIC_READ,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            self.logger.info("Pipes opened successfully")
            
            # Start a background thread to read from pipe_out continuously
            self.running = True
            self.read_thread = threading.Thread(target=self._read_pipe_thread, daemon=True)
            self.read_thread.start()
            return True
        except pywintypes.error as e:
            self.logger.error(f"Failed to open pipes: {e}")
            return False

    def close(self):
        # Skip if already closed
        if not self.is_open():
            self.logger.info("Pipes already closed")
            return

        try:
            self.logger.info("Closing pipes...")
            # Stop the reading thread first
            self.running = False

            # Wait for read thread to stop (with timeout)
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=1.0)

            # Now close the handles
            if self.pipe_in:
                win32file.CloseHandle(self.pipe_in)
                self.pipe_in = None
            if self.pipe_out:
                win32file.CloseHandle(self.pipe_out)
                self.pipe_out = None

            self.read_thread = None
            self.logger.info("Pipes closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing pipes: {e}")
            # Reset state even on error
            self.pipe_in = None
            self.pipe_out = None
            self.running = False

    def write(self, message: str):
        self.logger.info(f"Writing message to pipe: {message}")
        win32file.WriteFile(self.pipe_in, message.encode() + b'\n')

    def read(self, timeout=5, silent=False) -> str:
        """Non-blocking read from the response queue with a timeout.

        Args:
            timeout: Maximum seconds to wait for response
            silent: If True, don't log warning on timeout (useful for polling)
        """
        try:
            # Try to get a response from the queue with a timeout
            response = self.response_queue.get(timeout=timeout)
            return response
        except queue.Empty:
            if not silent:
                self.logger.warning("Timeout waiting for response from pipe.")
            return "Timeout"

    def _read_pipe_thread(self):
        """Continuously reads from pipe_out and stores responses in the queue."""
        while self.running:
            try:
                if not self.pipe_out:
                    break
                result, data = win32file.ReadFile(self.pipe_out, 4096)
                if result == 0:
                    line = data.decode().strip()
                    self.logger.info(f"Read line from pipe: {line}")
                    if line:
                        self.response_queue.put(line)
            except pywintypes.error as e:
                # Error 109 = pipe closed, exit silently
                if e.winerror == 109:
                    self.logger.info("Pipe closed, stopping read thread")
                    break
                elif self.running:
                    self.logger.error(f"Error reading from pipe: {e}")
            time.sleep(0.1)  # Slight delay to prevent excessive CPU usage

    def wait_for_pipe(self, pipe_path, max_attempts=30, delay=2):
        for attempt in range(max_attempts):
            if os.path.exists(pipe_path):
                self.logger.info(f"Pipe {pipe_path} found on attempt {attempt + 1}")
                return True
            self.logger.info(f"Waiting for pipe {pipe_path}, attempt {attempt + 1}/{max_attempts}")
            time.sleep(delay)
        return False

    def list_available_pipes(self):
        """List all available named pipes in the system"""
        if sys.platform == 'win32':
            try:
                import subprocess
                cmd = "powershell -Command \"[System.IO.Directory]::GetFiles('\\\\.\\pipe\\') | ForEach-Object { $_.Substring(9) }\""
                result = subprocess.run(cmd, capture_output=True, text=True)
                pipes = result.stdout.strip().split('\n')
                return pipes
            except Exception as e:
                self.logger.error(f"Error listing pipes: {e}")
                return []
        else:
            # For Unix-like systems
            try:
                import glob
                pipes = glob.glob('/tmp/audacity_script_pipe.*')
                return pipes
            except Exception as e:
                self.logger.error(f"Error listing pipes: {e}")
                return []

    def _force_audacity_pipes(self):
        """Try to force Audacity to create pipes by sending keyboard shortcuts"""
        try:
            import pyautogui
            # Try to focus Audacity window
            self.logger.info("Attempting to focus Audacity window...")
            
            # Try to find Audacity window
            import pygetwindow as gw
            audacity_windows = gw.getWindowsWithTitle('Audacity')
            
            if audacity_windows:
                audacity_window = audacity_windows[0]
                audacity_window.activate()
                time.sleep(1)
                
                # Send keyboard shortcut to open preferences
                self.logger.info("Sending keyboard shortcut to open preferences...")
                pyautogui.hotkey('ctrl', 'p')
                time.sleep(1)
                
                # Navigate to Modules section (may need adjustment based on Audacity version)
                self.logger.info("Navigating to Modules section...")
                pyautogui.press('tab', presses=10, interval=0.1)  # Navigate to category list
                
                # Type "modules" to jump to that section
                pyautogui.write('modules')
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # Find and enable mod-script-pipe
                pyautogui.press('tab', presses=5, interval=0.1)  # Navigate to module list
                pyautogui.write('mod-script-pipe')
                time.sleep(0.5)
                pyautogui.press('space')  # Toggle the module
                time.sleep(0.5)
                
                # Apply changes
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # Restart Audacity (this is a drastic measure)
                self.logger.info("Attempting to restart Audacity...")
                audacity_window.close()
                time.sleep(2)
                
                # Start Audacity again
                import subprocess
                subprocess.Popen([config.AUDACITY_PATH])
                time.sleep(15)  # Wait for Audacity to start and create pipes
                
                self.logger.info("Audacity restarted, pipes should be created now")
            else:
                self.logger.warning("Could not find Audacity window")
        except Exception as e:
            self.logger.error(f"Error forcing Audacity pipes: {e}")
