class ExploException(Exception):
    """ Base class for exceptions """
    pass

class ParserException(ExploException):
    """ Exception thrown when parsing an explo yaml file failed """
    pass

class ResultException(ExploException):
    """ Exception thrown when problems occur regarding the result """
    pass
