from BudgetMe.Forecast import Forecast

class Bank(object):
    """
    Basic bank object.
    """
    def __init__(self, name, initial_balance=0):
        self.name = name
        self.balance = initial_balance
        self.transactions = []

    def addTransaction(self, txn:Forecast):
        self.balance += txn.amount
        self.transactions.append({"id": txn.id, "amount": txn.amount})

    def asdict(self):
        return {"name": self.name, "balance": self.balance, "transactions": self.transactions}