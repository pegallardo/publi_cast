from abc import ABC, abstractmethod
import win32file
import pywintypes


DEFAULT_RETRY_ATTEMPTS = 5
DEFAULT_RETRY_DELAY = 1  # seconds

class Pipe(ABC):
    @abstractmethod
    def write(self, message: str):
        pass

    @abstractmethod
    def read(self) -> str:
        pass


  

class NamedPipe(Pipe):

    def __init__(self, pipe_to_audacity, pipe_from_audacity, logger):
        self.pipe_to_audacity = pipe_to_audacity
        self.pipe_from_audacity = pipe_from_audacity
        self.pipe_in = None
        self.pipe_out = None
        self.logger = logger
        self.logger.info(f"Initialized NamedPipe with to={pipe_to_audacity}, from={pipe_from_audacity}")

    def open(self):
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
