from abc import ABC, abstractmethod
import os
import sys
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

    def __init__(self):
        self.pipe_to_audacity = PIPE_TO_AUDACITY
        self.pipe_from_audacity = PIPE_FROM_AUDACITY
        self.pipe_in = None
        self.pipe_out = None
        self.logger = logger
        self.logger.info(f"Initialized NamedPipe with to={self.pipe_to_audacity}, from={self.pipe_from_audacity}")

    def open(self):
        try:
            # Check if pipe paths exist
            for pipe_path in [self.pipe_to_audacity, self.pipe_from_audacity]:
                if not os.path.exists(pipe_path):
                    self.logger.error(f"Pipe path {pipe_path} does not exist.")
                    return

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
