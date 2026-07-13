import logging  
# import Python's logging module so we can create and configure loggers

#  function that returns a logger object for the given name
def get_logger(name):
    # this gets/ creates a logger with the provided name
    logger = logging.getLogger(name)  
    # set the logger to only handle INFO messages and above (critical errors)
    logger.setLevel(logging.INFO)  
    return logger  