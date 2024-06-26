from .pipe import Pipe

class AudacityAPI:
    def __init__(self):
        self.pipe = None

    def set_pipe(self, pipe: Pipe):
        self.pipe = pipe

    def send_command(self, command: str):
        self.pipe.write(command)

    def get_response(self) -> str:
        return self.pipe.read()

    def run_command(self, command: str) -> str:
        self.send_command(command)
        return self.get_response()
