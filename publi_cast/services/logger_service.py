import logging
import os
from datetime import datetime

class LoggerService:
    def __init__(self):
        log_directory = "logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        self.clear_logs()
            
        log_filename = f"publi_cast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_filepath = os.path.join(log_directory, log_filename)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filepath),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    # Clear logs at startup
    def clear_logs(self):
        log_directory = "logs"
        current_time = datetime.now()
        deleted_count = 0
        
        for filename in os.listdir(log_directory):
            if filename.endswith(".log"):
                file_path = os.path.join(log_directory, filename)
                file_age = current_time - datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_age.days > 7:
                    os.remove(file_path)
                    deleted_count += 1
        
    def info(self, message):
        self.logger.info(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def warning(self, message):
        self.logger.warning(message)
