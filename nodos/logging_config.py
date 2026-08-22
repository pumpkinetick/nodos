import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler('nodos.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
