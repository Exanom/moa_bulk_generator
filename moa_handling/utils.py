import subprocess
import logging
from pathlib import Path

log_path = Path(__file__).resolve().parent.parent
logging.basicConfig(
    filename=str(log_path) +'/log.txt',
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def execute_command( command: str):
    """
    Executes a given command using subprocess library. In case of error in the result of the command will raise an exception. Every command ran is logged into log.txt file.

    Parameters:
        command (str): String containing the command to be run
    """
    logger.info(f'Running command {command}')
    result = subprocess.run(command, capture_output=True)
    if "error" in str(result.stdout).lower():
        logger.error(f'Error detected: {str(result.stdout)}')
        raise Exception()
    
