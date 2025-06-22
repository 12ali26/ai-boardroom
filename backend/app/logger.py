import logging
import os
from datetime import datetime
from typing import Optional


class AIBoardroomLogger:
    """Centralized logging configuration for AI Boardroom."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIBoardroomLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.setup_logging()
            self._initialized = True
    
    def setup_logging(self, log_level: str = "INFO", log_file: Optional[str] = None):
        """Setup centralized logging configuration."""
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Default log file with timestamp
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(log_dir, f"ai_boardroom_{timestamp}.log")
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # Console output
            ]
        )
        
        # Set specific logger levels
        loggers = {
            'ai_boardroom.openrouter': logging.INFO,
            'ai_boardroom.debate': logging.INFO,
            'ai_boardroom.database': logging.INFO,
            'ai_boardroom.ui': logging.INFO,
            'httpx': logging.WARNING,  # Reduce HTTP client noise
            'urllib3': logging.WARNING
        }
        
        for logger_name, level in loggers.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
        
        # Log startup
        main_logger = logging.getLogger('ai_boardroom.main')
        main_logger.info("AI Boardroom logging initialized")
        main_logger.info(f"Log file: {log_file}")
        main_logger.info(f"Log level: {log_level}")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance with the AI Boardroom prefix."""
        return logging.getLogger(f'ai_boardroom.{name}')


# Initialize logging on import
logger_instance = AIBoardroomLogger()

# Convenience function for getting loggers
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return AIBoardroomLogger.get_logger(name)