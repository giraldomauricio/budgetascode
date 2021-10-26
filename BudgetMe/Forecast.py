import  uuid

class Forecast:
    """
    Forecast is a transaction for an account.
    """

    def __init__(self, month, day, amount, note="", previous=0):
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, 'bac'))
        self.month = month
        self.day = day
        self.amount = amount
        self.planned = amount
        self.previous = previous  # Balance transfer from previous month
        self.note = ""

    def asdict(self):
        return {"id": self.id, "month": self.month, "day": self.day, "amount": self.amount, "planned": self.planned, "previous": self.previous, "note": self.note}