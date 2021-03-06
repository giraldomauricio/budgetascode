from datetime import date

from BudgetMe.BudgetException import BudgetAccountParametersInvalid
from BudgetMe.Empty import EmptyObject
from BudgetMe.Forecast import Forecast
import xlsxwriter

"""
BudgetMe is an approach to BaC (Budget as Code).
Author: Mauricio Giraldo <mgiraldo@gmail.com> 
"""


# TODO: mark periodicals.
# TODO: web migration.
# TODO: iOS migration.


class Account:
    """
    Account is the base of any money movement in a year.
    Child Accounts (With a Parent Account) only count in the balance if transfer_balance is set to True
    """

    def __init__(self, account="", year=None, category="", frequency=1, start=1, bank=None, periodical=False,
                 txn_mode="Required", budget_start=1, budget_end=12, parent=None):
        self.name = account
        if (not year or type(year) != int):
            todays_date = date.today()
            self.year = todays_date.year
        else:
            self.year = year
        self.forecast_array = []
        self.account = account
        self.days = []
        self.category = category
        self.frequency = frequency
        self.start = start
        self.bank = bank
        self.periodical = periodical
        self.txn_mode = txn_mode
        self.budget_start = budget_start
        self.budget_end = budget_end
        self.parent = parent
        if(parent):
            self.transfer_balance = True
        else:
            self.transfer_balance = False
        self.balance = 0

    def validate(self) -> bool:
        """
        Validates if all the input values for an Account are valid.
        :return: True if the values are valid, False if not.
        """
        valid_types = ["Debit", "Credit"]
        valid_modes = ["Required", "Optional"]
        if (type(self.year) is not int):
            raise ("Year (%s) must be a number. Is %s" % (self.year, type(self.year)))
        if (type(self.frequency) is not int):
            raise BudgetAccountParametersInvalid(
                "Frequency (%s) must be a number. Is %s" % (self.frequency, type(self.frequency)))
        if (type(self.start) is not int):
            raise BudgetAccountParametersInvalid("Start (%s) must be a number. Is %s" % (self.start, type(self.start)))
        if (not self.txn_mode in valid_modes):
            raise BudgetAccountParametersInvalid("Transaction mode must be one of the valid ones (%s)." % valid_modes)
        for day in self.days:
            if (type(day) is not float and type(day) is not int):
                raise BudgetAccountParametersInvalid("Day (%s) must be a number. Is %s" % (day, type(day)))
        # if self.start < self.budget_start:
        #         raise BudgetAccountParametersInvalid("The Account starts in a month (%s) before the Budget starts (%s)" % (self.start, self.budget_start))
        return True

    def asdict(self):
        """
        Converts the object variables into a dictionary
        :return:
        dict
        """
        if (not self.bank):
            self.bank = EmptyObject()
        forecast_array = []
        for forecast in self.forecast_array:
            forecast_array.append(forecast.asdict())
        return {"name": self.name, "year": self.year, "forecast_array": forecast_array, "account": self.account,
                "days": self.days, "category": self.category, "frequency": self.frequency, "start": self.start,
                "bank": self.bank.asdict(), "periodical": self.periodical, "txn_mode": self.txn_mode,
                "budget_start": self.budget_start, "budget_end": self.budget_end,
                "parent": self.parent, "transfer_balance": self.transfer_balance, "balance": self.balance}

    def init_single_month(self, month):
        self.init(range_start=month, range_end=month)

    def init(self, range_start=1, range_end=12):
        """
        Initializes an account, filling the year with transactions based on the start, end and frequency.
        :param range_start: Month where the transactions start.
        :param range_end: Month where the transactions end.
        :return: None
        """
        self.validate()
        if (range_start > range_end or range_end < 1 or range_end > 12):
            raise Exception("The range is incorrect.")
        frequency_counter = 0
        for i in range(self.budget_start, self.budget_end + 1):
            if (i >= range_start and i <= range_end):
                if (frequency_counter == self.frequency):
                    frequency_counter = 0
                if (i >= self.start):
                    frequency_counter += 1
                if (frequency_counter == 1):
                    for j in range(1, len(self.days) + 1):
                        forecast = Forecast(month=i, day=j, amount=self.days[j - 1],
                                            previous=self.getBalancePreviousMonth(i),account=self.name)
                        self.forecast_array.append(forecast)
                        if (self.bank):
                            self.bank.addTransaction(forecast)
                    # frequency_counter = 0
                else:
                    for j in range(1, len(self.days) + 1):
                        forecast = Forecast(month=i, day=j, amount=0, previous=self.getBalancePreviousMonth(i), account=self.name)
                        self.forecast_array.append(forecast)
            else:
                for j in range(1, len(self.days) + 1):
                    forecast = Forecast(month=i, day=j, amount=0, previous=self.getBalancePreviousMonth(i),account=self.name)
                    self.forecast_array.append(forecast)

    def getBalancePreviousMonth(self, month) -> float:
        """
        Gets the running balance of the previous month.
        :param month:
        :return: Float
        """
        balance = 0
        if (month > 1):
            for i in range(1, month):
                balance += self.getMonthBalance(i)
        return balance

    def getMonth(self, month) -> []:
        """
        Get the list of Accounts for the specified month.
        :param month:
        :return:
        """
        return [d for d in self.forecast_array if d.month == month]

    def setAmount(self, month, day, amount):
        """
        Updates the value of a transaction of an account on a specified month and day.
        :param month: month of the transaction.
        :param day: ordinal day of the transaction, not the actual day in the calendar
        :param amount: Account name
        :return: None
        """
        [c for c in [d for d in self.forecast_array if d.month == month] if c.day == day][0].amount = amount

    def correctTransaction(self, month, day, amount):
        """
        Updates the actual value of a transaction of an account on a specified month and day.
        Actual value vs. amount will show the actual budget vs real values.
        :param month: month of the transaction.
        :param day: ordinal day of the transaction, not the actual day in the calendar
        :param amount: Account name
        :return: None
        """
        txn = [c for c in [d for d in self.forecast_array if d.month == month] if c.day == day][0]
        txn.amount = amount
        txn.confirmed = True

    def confirmTransaction(self, month, day):
        """
        Updates the actual value of a transaction of an account on a specified month and day.
        Actual value vs. amount will show the actual budget vs real values.
        :param month: month of the transaction.
        :param day: ordinal day of the transaction, not the actual day in the calendar
        :param amount: Account name
        :return: None
        """
        txn = [c for c in [d for d in self.forecast_array if d.month == month] if c.day == day][0].confirmed = True

    def removeConfirmTransaction(self, month, day):
        """
        Removes the confirmation of the actual value of a transaction of an account on a specified month and day.
        Actual value vs. amount will show the actual budget vs real values.
        :param month: month of the transaction.
        :param day: ordinal day of the transaction, not the actual day in the calendar
        :param amount: Account name
        :return: None
        """
        txn = [c for c in [d for d in self.forecast_array if d.month == month] if c.day == day][0].confirmed = False

    def correctPreviousBalance(self, month, day, previous):
        """
        Updates the actual value of a transaction of an account on a specified month and day.
        Actual value vs. amount will show the actual budget vs real values.
        :param month: month of the transaction.
        :param day: ordinal day of the transaction, not the actual day in the calendar
        :param amount: Account name
        :return: None
        """
        [c for c in [d for d in self.forecast_array if d.month == month] if c.day == day][0].previous = previous

    def getFinalBalance(self) -> float:
        """
        Returns the final balance of the account
        :return:
        """
        balance = 0
        for month in range(1, 13):
            balance += self.getMonthBalance(month)
        return balance

    def getMonthBalance(self, month) -> float:
        """
        Returns the balance of an account for a specific month.
        :param month:
        :return:
        """
        balance = 0
        month_transactions = [d for d in self.forecast_array if d.month == month]
        for txn in month_transactions:
            balance += txn.amount
        return balance

    def getMonthDayBalance(self, month, day) -> float:
        """
        Returns the balance of an account for a specific month and day.
        :param month:
        :return:
        """
        balance = 0
        month_transactions = [d for d in self.forecast_array if d.month == month and d.day == day]
        for txn in month_transactions:
            balance += txn.amount
        return balance

    def getMonthBalance2(self, month) -> float:
        """
        Returns the balance of an account for a specific month.
        :param month:
        :return:
        """
        balance = 0
        month_transactions = [d for d in self.forecast_array if d.month == month]
        for txn in month_transactions:
            print(txn.account,",",txn.month,",",txn.day,",",txn.amount)
            balance += txn.amount
        return balance

    def getNegativeMonths(self) -> []:
        """
        Returns an array of the months where the final balance is less than zero.
        :return:
        """
        results = []
        for i in range(1, 13):
            balance = self.getMonthBalance(i)
            if (balance < 0):
                results.append({"month": i, "balance": balance})
        return results

    def getRunningBalance(self, month):
        """
        Returns the running (Accumulated) balance up to the specified month.
        :param month:
        :return:
        """
        balance = 0
        for days in range(1, month + 1):
            balance += self.getMonthBalance(days)
        return balance
