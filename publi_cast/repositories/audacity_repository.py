from abc import ABC, abstractmethod
import os
import sys
import time
import win32file
import pywintypes
from services.logger_service import LoggerService
from config import PIPE_TO_AUDACITY, PIPE_FROM_AUDACITY

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
        self.logger.info(f"Initialized NamedPipe with to={self.pipe_to_audacity}, from={self.pipe_from_audacity}")

    def open(self):
        if not self.wait_for_pipe(self.pipe_to_audacity) or not self.wait_for_pipe(self.pipe_from_audacity):
            raise RuntimeError("Pipes not available after maximum attempts")

        try:
            self.logger.info("Opening pipes to Audacity...")
            self.pipe_in = win32file.CreateFile(
                self.pipe_to_audacity,
                win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            self.pipe_out = win32file.CreateFile(
                self.pipe_from_audacity,
                win32file.GENERIC_READ,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            self.logger.info("Pipes opened successfully")
        except pywintypes.error as e:
            self.logger.error(f"Failed to open pipes: {e}")
            raise

    def close(self):
        try:
            self.logger.info("Closing pipes...")
            if self.pipe_in:
                win32file.CloseHandle(self.pipe_in)
            if self.pipe_out:
                win32file.CloseHandle(self.pipe_out)
            self.logger.info("Pipes closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing pipes: {e}")
            raise

    def write(self, message: str):
        win32file.WriteFile(self.pipe_in, message.encode() + b'\n')

    def read(self) -> str:
        response = []
        while True:
            result, data = win32file.ReadFile(self.pipe_out, 4096)
            if result == 0:
                line = data.decode().strip()
                if line == "End of Script":
                    break
                response.append(line)
        return "\n".join(response)

    def wait_for_pipe(self, pipe_path, max_attempts=10, delay=1):
        for attempt in range(max_attempts):
            if os.path.exists(pipe_path):
                self.logger.info(f"Pipe {pipe_path} found on attempt {attempt + 1}")
                return True
            self.logger.info(f"Waiting for pipe {pipe_path}, attempt {attempt + 1}/{max_attempts}")
            time.sleep(delay)
        return False