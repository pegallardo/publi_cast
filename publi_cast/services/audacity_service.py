import time
from repositories.audacity_repository import Pipe

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
        try:
            # Send command to Audacity
            self.send_command(command)
            print(f"Command sent: {command}")

            # Attempt to get response from Audacity
            response = self.get_response()
            time.sleep(1)  # Give Audacity time to respond
            # Validate the response
            if not response:
                raise ValueError("No response received from Audacity.")
            
            print(f"Response received: {response}")
            return response
        
        except Exception as e:
            print(f"Error executing command '{command}': {e}")
            return f"Error: {e}"
