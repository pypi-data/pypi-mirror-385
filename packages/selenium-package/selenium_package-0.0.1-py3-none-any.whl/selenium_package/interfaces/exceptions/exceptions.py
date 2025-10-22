class SeleniumBaseActionException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class SeleniumBaseGetterException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class MaximumAttemptsReachedException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class NoMorePagesException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)