import  uuid

class Forecast:
    """
    Forecast is a transaction for an account.
    """

    def __init__(self, month, day, amount, note="", previous=0, account=""):
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'bac'))
        self.month = month
        self.day = day
        self.amount = amount
        self.planned = amount
        self.previous = previous  # Balance transfer from previous month
        self.note = ""
        self.confirmed = False # A transaction is caused when it's confirmed. Before that is just a prediction in the forecast.
        self.account = account

    def asdict(self):
        return {"id": self.id, "month": self.month, "day": self.day, "amount": self.amount, "planned": self.planned, "previous": self.previous, "note": self.note, "caused": self.confirmed, "account": self.account}