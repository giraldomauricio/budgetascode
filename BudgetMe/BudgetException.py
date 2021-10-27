class BudgetAccountParametersInvalid(Exception):

    """
    Exception to throw during validation
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class BudgetAccountNotFound(Exception):

    """
    Exception to throw during validation
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)