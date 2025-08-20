import subprocess
import logging
from pathlib import Path
import math
from shlex import split

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
    result = subprocess.run(split(command), capture_output=True)
    if("error" in str(result.stdout).lower() or "{M}assive {O}nline {A}nalysis" not in str(result.stderr)):
        logger.error(f'Error detected: std_out: {str(result.stdout)} std_err: {str(result.stderr)}')
        raise Exception()
    

def sigmoid(i, p, w):
    x = -4.0 * (i - p) / w
    
    if(x>=700):
        return 0
    return 1.0 / (1.0 + math.exp(x))
