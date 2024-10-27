from abc import ABC, abstractmethod
import time

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
    def __init__(self, to_pipe_path: str, from_pipe_path: str, retry_attempts=DEFAULT_RETRY_ATTEMPTS, retry_delay=DEFAULT_RETRY_DELAY):
        self.to_pipe_path = to_pipe_path
        self.from_pipe_path = from_pipe_path
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.to_pipe = None
        self.from_pipe = None

    def open(self):
        """Attempt to open named pipes with retries."""
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                # Try to open the named pipes
                self.to_pipe = open(self.to_pipe_path, 'w')
                self.from_pipe = open(self.from_pipe_path, 'r')
                print("Named pipes successfully opened.")
                return  # Exit if pipes are successfully opened

            except FileNotFoundError:
                print(f"Attempt {attempts + 1}/{self.retry_attempts}: Named pipes not available.")
                time.sleep(self.retry_delay)
                attempts += 1

        raise RuntimeError("Failed to open named pipes after multiple attempts.")

    def close(self):
        if self.to_pipe:
            self.to_pipe.close()
        if self.from_pipe:
            self.from_pipe.close()

    def write(self, message: str):
        self.to_pipe.write(message + '\n')
        self.to_pipe.flush()

    def read(self) -> str:
        response = []
        while True:
            line = self.from_pipe.readline()
            if line.strip() == "End of Script":
                break
            response.append(line.strip())
        return "\n".join(response)
