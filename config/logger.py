import logging  

#  returns logger object for the given name
def get_logger(name):
    # gets/ creates a logger with the provided name
    logger = logging.getLogger(name)  
    # setting the logger to handle the "critical/important" information 
    logger.setLevel(logging.INFO)  


