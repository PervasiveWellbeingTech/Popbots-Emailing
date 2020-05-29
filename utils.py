import logging

def return_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)-4s %(message)s')

    file_handler = logging.FileHandler('logs/global.log')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)


    stream_handler = logging.StreamHandler()
    stream_handler_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    stream_handler.setFormatter(stream_handler_formatter)
    stream_handler.setLevel(logging.DEBUG)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


