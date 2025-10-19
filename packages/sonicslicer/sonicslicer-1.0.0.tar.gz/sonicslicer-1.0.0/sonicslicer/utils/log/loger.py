import logging


def get_logger():
    # Configure logging at the module level
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
    logger = logging.getLogger("_sonicslicer_")

    return logger
