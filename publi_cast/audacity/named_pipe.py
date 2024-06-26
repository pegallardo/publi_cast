import os
from .pipe import Pipe

class NamedPipe(Pipe):
    def __init__(self, to_pipe_path: str, from_pipe_path: str):
        self.to_pipe_path = to_pipe_path
        self.from_pipe_path = from_pipe_path
        self.to_pipe = None
        self.from_pipe = None

    def open(self):
        if not os.path.exists(self.to_pipe_path):
            raise FileNotFoundError("Could not find the Audacity pipe. Is Audacity running with mod-script-pipe enabled?")
        self.to_pipe = open(self.to_pipe_path, 'w')
        self.from_pipe = open(self.from_pipe_path, 'r')

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
