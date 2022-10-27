from logging import getLogger, DEBUG, FileHandler, Formatter

def get_module_logger(module=__name__, filepath="./mercari.log"):
    logger = getLogger(module)
    logger.setLevel(DEBUG)
    handler = FileHandler(filepath)
    handler.setLevel(DEBUG)
    formatter = Formatter('%(levelname)s  %(asctime)s  [%(name)s - %(funcName)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger