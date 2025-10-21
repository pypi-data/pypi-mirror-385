import axiom_py
from axiom_py.logging import AxiomHandler
import dotenv
import logging
import os
import sys

dotenv.load_dotenv()

DEFAULT_LOGLEVEL_INT = logging.INFO
AXIOM_TOKEN = os.environ['AXIOM_TOKEN']
AXIOM_DATASET_NAME = os.environ.get('AXIOM_DATASET_NAME', 'pythonny-quest')
AXIOM_LOGLEVEL_INT = os.environ.get('AXIOM_LOGLEVEL', DEFAULT_LOGLEVEL_INT)


def add_global_axiom_handler(name=AXIOM_DATASET_NAME, level: str | int = AXIOM_LOGLEVEL_INT):
    """ Initialize a logger that outputs to the console.

    Args:
        name (str): The name of the logger. Defaults to the module name.
        level (str): The logging level. Defaults to "INFO".

    Returns:
        logging.Logger: A configured logger instance.
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), DEFAULT_LOGLEVEL_INT)
    client = axiom_py.Client()
    handler = AxiomHandler(client, dataset=name, level=level)
    logging.getLogger().addHandler(handler)


def get_logger(name: str = __name__, level: str | int = DEFAULT_LOGLEVEL_INT) -> logging.Logger:
    add_global_axiom_handler()

    logger = logging.getLogger(name)
    if isinstance(level, str):
        level = getattr(logging, level.upper(), DEFAULT_LOGLEVEL_INT)
    logger.setLevel(level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(pathname)s:%(lineno)s %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
