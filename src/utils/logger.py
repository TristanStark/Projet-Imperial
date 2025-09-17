import logging
from functools import wraps

logger = logging.getLogger("pnj")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

def log_function_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Appel de la fonction : {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
