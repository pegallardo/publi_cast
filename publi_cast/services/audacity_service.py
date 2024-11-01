import subprocess
import time
import threading
import queue
from config import AUDACITY_PATH, DEFAULT_RETRY_ATTEMPTS, DEFAULT_RETRY_DELAY, EOL

class AudacityAPI:
    def __init__(self, named_pipe, logger):
        self.named_pipe = named_pipe
        self.logger = logger
        self.pipe = None
        self.logger.info("Initialized AudacityAPI")
        
        # Queue pour stocker les réponses du pipe
        self.response_queue = queue.Queue()
        self.read_thread = None

    def start_audacity(self, retry_attempts=DEFAULT_RETRY_ATTEMPTS, retry_delay=DEFAULT_RETRY_DELAY):
        for attempt in range(retry_attempts):
            try:
                self.logger.info(f"Starting Audacity... (Attempt {attempt + 1}/{retry_attempts})")
                process = subprocess.Popen(AUDACITY_PATH)
                time.sleep(retry_delay)
                
                # Vérifie que le processus est en cours d'exécution
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
        
        # Démarre un thread de lecture non-bloquant
        self.read_thread = threading.Thread(target=self._read_pipe_thread, daemon=True)
        self.read_thread.start()

    def _read_pipe_thread(self):
        """Thread pour lire le pipe en continu et stocker les réponses dans la file d'attente."""
        while True:
            if self.pipe:
                response = self.pipe.read()
                if response:
                    self.response_queue.put(response)
            time.sleep(0.1)  # Pause pour réduire l'utilisation du CPU

    def run_command(self, command, timeout=5):
        if not self.pipe:
            error_msg = "Pipe not set"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            self.logger.info(f"Running Audacity command: {command}")
            self.pipe.write(command + EOL)

            start_time = time.time()

            # Attendre une réponse ou un timeout
            while True:
                try:
                    # Récupère la réponse depuis la queue, avec un délai d'attente pour éviter le blocage
                    decoded_response = self.response_queue.get(timeout=timeout)
                    print("Received response:", decoded_response)
                    break
                except queue.Empty:
                    if time.time() - start_time > timeout:
                        print("Timeout: no response.")
                        decoded_response = None
                        break
                time.sleep(0.1)  # Pause pour éviter la surcharge CPU
            
            # Vérification de la réponse pour des erreurs spécifiques
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
