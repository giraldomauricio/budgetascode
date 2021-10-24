from datetime import date

import xlsxwriter

"""
BudgetMe is an approach to BaC (Budget as Code).
Author: Mauricio Giraldo <mgiraldo@gmail.com> 
"""


# TODO: mark periodicals. Mark required and optionals. Calculate potential savings. Add graphs. Classify expenses from credits.
# TODO: web migration.
# TODO: iOS migration.

class Account:
    """
    Account is the base of any money movement in a year.
    """

    def __init__(self, account="", year=None, category="", frequency=1, start=1, bank=None, periodical=False,
                 txn_type="Debit", tnx_mode="Required"):
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
        self.txn_type = txn_type
        self.txn_mode = tnx_mode

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
                "bank": self.bank.asdict(), "periodical": self.periodical, "txn_type": self.txn_type, "txn_mode": self.txn_mode}

    def init_single_month(self, month):
        self.init(range_start=month, range_end=month)

    def init(self, range_start=1, range_end=12):
        """
        Initializes an account, filling the year with transactions based on the start, end and frequency.
        :param range_start: Month where the transactions start.
        :param range_end: Month where the transactions end.
        :return: None
        """
        frequency_counter = 0
        for i in range(1, 13):
            if (i >= range_start and i <= range_end):
                if (frequency_counter == self.frequency):
                    frequency_counter = 0
                if (i >= self.start):
                    frequency_counter += 1
                if (frequency_counter == 1):
                    for j in range(1, len(self.days) + 1):
                        self.forecast_array.append(
                            Forecast(month=i, day=j, amount=self.days[j - 1], previous=self.getBalancePreviousMont(i)))
                        if (self.bank):
                            self.bank.addTransaction(self.days[j - 1])
                    # frequency_counter = 0
                else:
                    for j in range(1, len(self.days) + 1):
                        self.forecast_array.append(
                            Forecast(month=i, day=j, amount=0, previous=self.getBalancePreviousMont(i)))
            else:
                for j in range(1, len(self.days) + 1):
                    self.forecast_array.append(
                        Forecast(month=i, day=j, amount=0, previous=self.getBalancePreviousMont(i)))

    def getBalancePreviousMont(self, month) -> float:
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

    def setActual(self, month, day, amount):
        """
        Updates the value of a transaction of an account on a specified month nad day.
        :param month: month of the transaction.
        :param day: ordinal day of the transaction, not the actual day in the calendar
        :param amount: Account name
        :return: None
        """
        [c for c in [d for d in self.forecast_array if d.month == month] if c.day == day][0].amount = amount

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


class Forecast:
    """
    Forecast is a transaction for an account.
    """

    def __init__(self, month, day, amount, previous=0):
        self.month = month
        self.day = day
        self.amount = amount
        self.previous = previous  # Balance transfer from previous month

    def asdict(self):
        return {"month": self.month, "day": self.day, "amount": self.amount, "previous": self.previous}


class Budget:
    """
    Budget is the mayor object of the application.
    """

    def __init__(self, year, daysof=1):
        self.year = year
        self.transactions = []
        self.daysof = daysof
        self.days_labels = [""] * daysof
        self.banks = []
        self.template = {}

    def asdict(self) -> dict:
        """
        Converts the class structure into a dictionary.
        :return: dict
        """
        transactions = []
        banks = []
        for txn in self.transactions:
            transactions.append(txn.asdict())
        for bank in self.banks:
            banks.append(bank.asdict())
        return {"year": self.year, "daysof": self.daysof, "transactions": transactions, "banks": banks, "days_labels": self.days_labels, "template": self.template}

    def addAccount(self, name, days=0, category="", frequency=1, start=1, end=12, bank="", periodical=False, txn_type="Debit", txn_mode="Required", use_last=False) -> Account:
        """
        Adds an account to the Budget
        :param name: Name of the account.
        :param days: Days of transactions in the form of an array. The array size has to be the same size of the parameter 'daysof' of the Account.
        :param category: The category where to put the Account.
        :param frequency: How frequent in months the transaction happens. Default is 1.
        :param start: Month where the transactions start.
        :param end: Month where the transactions end.
        :param bank: Name of the bank where the money comes or goes.
        :param periodical: Boolean to identify if the transactions happens periodically.
        :param txn_type: String with the name of the transaction type: Debit or Credit.
        :param txn_mode: String with the mode of the transaction: Required or Optional.
        :param use_last: Boolean to identify to use the same parameters as the last creation of an account.
        :return: Account
        """
        if use_last:
            category = self.template['category']
            frequency = self.template['frequency']
            start = self.template['start']
            end = self.template['end']
            bank = self.template['bank']
            periodical = self.template['periodical']
            txn_type = self.template['txn_type']
            txn_mode = self.template['txn_mode']
        if (type(days) != list):
            days_array = []
            days_array.append(days)
            days = days_array
        if (len(days) != self.daysof):
            raise Exception("All accounts must have the number of days associated during creation.")
        bank_instance = self.getBank(name=bank)
        account = Account(account=name, year=self.year, category=category, frequency=frequency, start=start,
                          bank=bank_instance, periodical=periodical, txn_type=txn_type, tnx_mode=txn_mode)
        account.days = days
        account.init(range_start=start, range_end=end)
        self.transactions.append(account)
        self.template = account.asdict() # Save the basic parameters to be reused and simplify the entries.
        self.template['end'] = end
        return account

    def addSingleAccount(self, name, month, days=[], category="", bank="", periodical=False, txn_type="Debit", txn_mode="Required", use_last=False) -> Account:
        """
        Creates an account that only has one single transaction in the entire year.
        :param name: Name of the account.
        :param month: Number of the month where the transaction happens.
        :param days: Ordinal of the day where the transaction happens.
        :param category: Category of the transaction.
        :param bank: Name of the bank where the money comes or goes.
        :param periodical: Boolean to identify if the transactions happens periodically.
        :param txn_type: String with the name of the transaction type: Debit or Credit.
        :param txn_mode: String with the mode of the transaction: Required or Optional.
        :param use_last: Boolean to identify to use the same parameters as the last creation of an account. 
        :return: Account
        """
        if use_last:
            category = self.template['category']
            bank = self.template['bank']
            periodical = self.template['periodical']
            txn_type = self.template['txn_type']
            txn_mode = self.template['txn_mode']
        if (type(days) != list):
            days_array = []
            days_array.append(days)
            days = days_array
        if (len(days) != self.daysof):
            raise Exception("All accounts must have the number of days associated during creation.")
        bank_instance = self.getBank(name=bank)
        account = Account(account=name, year=self.year, category=category, frequency=1, start=month,
                          bank=bank_instance, periodical=periodical, txn_type=txn_type, tnx_mode=txn_mode)
        account.days = days
        account.init_single_month(month)
        self.transactions.append(account)
        self.template = account.asdict()  # Save the basic parameters to be reused and simplify the entries.
        return account

    def getCategories(self) -> list:
        """
        Get the categories from all accounts added.
        :return: list
        """
        result = []
        for account in self.transactions:
            if (account.category not in result):
                result.append(account.category)
        return result

    def payOff(self, account, amount, time, start=1, category="", bank=""):
        """
        Create a sequence of transactions to pay of an specified ammount.
        :param account: Name of the account.
        :param amount: The amount to pay off.
        :param time: The time to pay off the amount.
        :param start: When to start the payments.
        :param category: Category of the account.
        :param bank: Name of the bank where the money comes.
        :return: None
        """
        monthly_payment = round(amount / time, 2)
        days = []
        days.append(monthly_payment)
        for i in range(1, self.daysof):
            days.append(0)
        self.addAccount(name=account, days=days, category=category, frequency=1, start=start, end=start + time - 1,
                        bank=bank)

    def getBalanceByCategories(self) -> dict:
        """
        Gets the balance by categories
        :return: Dictionary with the categories and its balances.
        """
        result = {}
        categories = self.getCategories()
        for category in categories:
            result[category] = self.getTotalBalanceByCategory(category)
        return result

    def getFinalBalance(self) -> float:
        """
        Returns the final balance from all the accounts.
        :return:
        """
        balance = 0.0
        for txn in self.transactions:
            balance += txn.getFinalBalance()
        return balance

    def detectNegativeBalance(self) -> dict:
        """
        Detects and returns if the first month that will end up with negative balance.
        :return:
        """
        result = {"month": 0, "balance": 0}
        for month in range(1, 13):
            balance = self.getRunningBalance(month)
            if (balance < 0):
                result = {"month": month, "balance": balance}
                break
        return result

    def preventNegativeBalance(self, account_name="Negative protection"):
        """
        Creates transactions to avoid ending in negative balances,
        :param account_name: Name of the account.
        :return:
        """
        analysis = self.detectNegativeBalance()
        self.addAccount(account_name, days=0)
        month_start = analysis['month']
        for month in range(month_start, 13):
            negative_analysis = self.detectNegativeBalance()
            if (negative_analysis['balance'] < 0):
                self.updateTransaction("Negative protection", month, 1, negative_analysis['balance'] * -1)

    def calcualtePotentialSavings(self) -> float:
        """
        Returns how much money is being spent in accounts classified as optional.
        :return: How much money you spend in optionals.
        """
        optional_accounts = [d for d in self.transactions if d.txn_mode == "Optional"]
        savings = 0
        for optional in optional_accounts:
            for txn in optional.forecast_array:
                savings += txn.amount
        return savings

    def getRunningBalance(self, month) -> float:
        """
        Running balance is the balance accumulated until the month specified
        :param month:
        :return:
        """
        balance = 0.0
        for txn in self.transactions:
            balance += txn.getRunningBalance(month)
        return balance

    def getMonthBalance(self, month) -> float:
        """
        Returns the balance of the specified month.
        :param month: Month to query.
        :return:
        """
        balance = 0
        for account in self.transactions:
            balance += account.getMonthBalance(month)
        return balance

    def getTotalBalanceByCategory(self, category) -> float:
        """
        Returns the total balance for a Category by the end of the year.
        :param category: Name of the category.
        :return: Balance of the category at the end of the year.
        """
        transactions = [d for d in self.transactions if d.category == category]
        balance = 0
        for transaction in transactions:
            balance += transaction.getFinalBalance()
        return balance

    def getAccount(self, account_name) -> Account:
        """
        Returns an account
        :param account_name: Name of the Account
        :return: Account
        """
        return [d for d in self.transactions if d.name == account_name][0]

    def getMonthName(self, month_number):
        """
        Transaltes ordinals in names of months in english.
        :param month_number: Number of the month.
        :return: Name of the month in a 3 letter abbreviation.
        """
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        if (month_number < 1 or month_number > 12):
            raise Exception("Month must be between 1 and 12.")
        return months[month_number - 1]

    def updateTransaction(self, account_name, month, day, amount):
        """
        Updates a transaction in an account.
        :param account_name: Name of the account.
        :param month: Month to update.
        :param day: Day to update.
        :param amount: Amount to update.
        :return: None
        """
        self.getAccount(account_name=account_name).setActual(month, day, amount)

    def formatCurrency(self, number) -> str:
        """
        Formats a number in the form of $0000.00
        :param number:
        :return: String
        """
        return "${:,.2f}".format(number)

    def generateHTMLTable(self) -> str:
        """
        Generates an HTML string with the entire budget
        :return: HTML in a String.
        """
        html = "<table border=\"1\" cellpadding=\"5\">\n"
        # Months Columns Headers
        html += "\t<tr style=\"background-color: cornflowerblue; color: aliceblue\">\n"
        html += "\t\t<td style=\"text-align: center; font-weight: bold\">" + str(self.year) + "</td>\n"
        for month in range(1, 13):
            html += "\t\t<td colspan=\"" + str(
                self.daysof) + "\" style=\"text-align: center; font-weight: bold\">" + str(
                self.getMonthName(month)) + "</td>\n"
        html += "\t\t<td style=\"background-color: #EEEEEE; color\">&nbsp;</td>\n"
        html += "\t</tr>\n"
        # Days labels columns headers
        html += "\t<tr style=\"background-color: cadetblue; color: aliceblue\">\n"
        html += "\t\t<td style=\"background-color: #EEEEEE; color\">&nbsp;</td>\n"
        for month in range(1, 13):
            for label in self.days_labels:
                html += "\t\t<td style=\"text-align: center; font-weight: bold; font-size: x-small;\">" + label + "</td>\n"
        html += "\t\t<td>Final&nbsp;balances</td>\n"
        html += "\t</tr>\n"
        for row in self.transactions:
            html += "\t<tr>\n"
            html += "\t\t<td>" + row.name + "</td>\n"
            for month in range(1, 13):
                for day in row.getMonth(month):
                    if (day.amount > 0):
                        html += "\t\t<td class=\"positive\">" + self.formatCurrency(day.amount) + "</td>\n"
                    elif (day.amount == 0):
                        html += "\t\t<td style=\"background-color: #EEEEEE;\">&nbsp;</td>\n"
                    else:
                        html += "\t\t<td class=\"negative\">" + self.formatCurrency(
                            day.amount) + "</td>\n"
            final_balance = row.getFinalBalance()
            if (final_balance < 0):
                html += "\t\t<td  class=\"negative\">" + self.formatCurrency(
                    row.getFinalBalance()) + "</td>\n"
            else:
                html += "\t\t<td class=\"positive\">" + self.formatCurrency(
                    row.getFinalBalance()) + "</td>\n"
            html += "\t</tr>\n"
        # Monthly Balance
        html += "\t<tr style=\"background-color: aliceblue\">\n"
        html += "\t\t<td>Monthly&nbsp;balance</td>\n"
        for month in range(1, 13):
            monthly_balance = self.getMonthBalance(month)
            if (monthly_balance > 0):
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\" class=\"positive\">" + self.formatCurrency(
                    monthly_balance) + "</td>\n"
            else:
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\"  class=\"negative\">" + self.formatCurrency(
                    monthly_balance) + "</td>\n"
        html += "\t\t<td>&nbsp;</td>\n"
        html += "\t</tr>\n"
        # Running Balances
        html += "\t<tr>\n"
        html += "\t\t<td>Running&nbsp;balance</td>\n"
        for month in range(1, 13):
            running_balance = self.getRunningBalance(month)
            if (running_balance > 0):
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\" class=\"positive\">" + self.formatCurrency(
                    running_balance) + "</td>\n"
            else:
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\"  class=\"negative\">" + self.formatCurrency(
                    running_balance) + "</td>\n"
        total_balance = self.getFinalBalance()
        if (total_balance < 0):
            html += "\t\t<td   class=\"negative\">&nbsp;" + self.formatCurrency(
                total_balance) + "</td>\n"
        else:
            html += "\t\t<td  style=\"text-align: right; font-weight: bold\">&nbsp;" + self.formatCurrency(
                total_balance) + "</td>\n"
        html += "\t</tr>\n"
        html += "<table border=\"1\" cellpadding=\"5\">\n<br>"
        html += "<td colspan=\"3\" style=\"text-align: center; font-weight: bold \">Categories</td>\n"
        categories = self.getBalanceByCategories()
        for k, v in categories.items():
            html += "<tr>\n"
            html += "\t<td>" + k + "</td><td style=\"text-align: right\">" + self.formatCurrency(
                v) + "</td><td style=\"text-align: right\">" + self.formatCurrency(v / 12) + "/mo</td>\n"
            html += "<tr>\n"
        html += "</table>"
        html += "\t</tr>\n"
        html += "<table style=\"font-size: small; font-family: 'Helvetica'; border-collapse: collapse\" border=\"1\" cellpadding=\"5\">\n<br>"
        html += "<td colspan=\"2\" style=\"text-align: center; font-weight: bold \">Banks</td>\n"
        for bank in self.banks:
            html += "<tr>\n"
            html += "\t<td>" + bank.name + "</td><td style=\"text-align: right\">" + self.formatCurrency(
                bank.balance) + "</td>\n"
            html += "<tr>\n"
        html += "</table>"
        html += "<tr>\n"
        html += "<table border=\"1\" cellpadding=\"5\">\n<br>"
        html += "<td style=\"text-align: center; font-weight: bold \">Potential savings</td>\n"
        html += "<tr>\n"
        html += "\t<td style=\"text-align: right\">" + self.formatCurrency(self.calcualtePotentialSavings()) + "</td>\n"
        html += "<tr>\n"
        html += "</table>"
        css = """<style type="text/css">
		table {
			font-size: small;
			font-family: 'Helvetica';
			border-collapse: collapse;
		}
		.negative {
			font-size: small;
			font-family: 'Helvetica';
			background-color: #fde1e5
		}
		.positive {
			font-size: small;
			font-family: 'Helvetica';
			background-color: #bfffd5;
		}
	</style>"""
        body = "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\">\n<title>Report</title>\n" + css + "</head>\n<body>\n" + html + "\n</body>\n</html>"
        return body

    def generateExcelFile(self, filename="budget.xlsx"):
        """
        Generates a file with representation of the Budget HTML in Excel format.
        :param filename: Name of the file to save the data.
        :return: None
        """
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)
        worksheet.write('A1', self.year)
        month = 0
        for column in range(1, 25, 2):
            month += 1
            col = 65 + column
            cell = '%s1' % chr(col)
            merge = '%s1' % chr(col + 1)
            worksheet.merge_range("%s:%s" % (cell, merge), str(self.getMonthName(month)))
        for month in range(1, 25):
            for label in self.days_labels:
                col = 65 + month
                worksheet.write("%s2" % chr(col), label)
        worksheet.write("Z2", "Final balances")
        row_counter = 2
        for row in self.transactions:
            row_counter += 1
            worksheet.write("A%s" % row_counter, row.name)
            days_counter = 0
            for txn in row.forecast_array:
                days_counter += 1
                col = 65 + days_counter
                worksheet.write("%s%s" % (chr(col), row_counter), txn.amount)
            days_counter += 1
            col = 65 + days_counter
            worksheet.write("%s%s" % (chr(col), row_counter), row.getFinalBalance())
        # # Monthly Balance
        row_counter += 1
        worksheet.write("A%s" % row_counter, "Monthly balance")
        month = 0
        for column in range(1, 25, 2):
            month += 1
            col = 65 + column
            cell = '%s%s' % (chr(col), row_counter)
            merge = '%s%s' % (chr(col + 1), row_counter)
            worksheet.merge_range("%s:%s" % (cell, merge), str(self.getMonthBalance(month)))
        row_counter += 1
        worksheet.write("A%s" % row_counter, "Running balance")
        month = 0
        for column in range(1, 25, 2):
            month += 1
            col = 65 + column
            cell = '%s%s' % (chr(col), row_counter)
            merge = '%s%s' % (chr(col + 1), row_counter)
            worksheet.merge_range("%s:%s" % (cell, merge), str(self.getRunningBalance(month)))
        month += 1
        worksheet.write("Z%s" % row_counter, self.getFinalBalance())

        row_counter += 2
        cell = 'A%s' % (row_counter)
        merge = 'C%s' % (row_counter)
        worksheet.merge_range("%s:%s" % (cell, merge), "Categories")
        row_counter += 1
        categories = self.getBalanceByCategories()
        for k, v in categories.items():
            worksheet.write("A%s" % row_counter, k)
            worksheet.write("B%s" % row_counter, v)
            worksheet.write("C%s" % row_counter, v / 12)
            row_counter += 1

        row_counter += 2
        cell = 'A%s' % (row_counter)
        merge = 'B%s' % (row_counter)
        worksheet.merge_range("%s:%s" % (cell, merge), "Banks")
        row_counter += 1
        for bank in self.banks:
            worksheet.write("A%s" % row_counter, bank.name)
            worksheet.write("B%s" % row_counter, bank.balance)
            row_counter += 1

        row_counter += 2
        worksheet.write("A%s" % row_counter, "Potential savings")
        row_counter += 1
        worksheet.write("A%s" % row_counter, self.calcualtePotentialSavings())
        row_counter += 1
        workbook.close()

    def generateHtmlFile(self, file_name="report.html"):
        """
        Generates the file of the HTML Budget.
        :param file_name: Name of the file.
        :return: None
        """
        with open(file_name, "w") as text_file:
            text_file.write(self.generateHTMLTable())

    def transferFromAccountToBank(self, from_account, to_bank):
        """
        Transfers money from one account to a bank
        :param from_account: Name of the account.
        :param to_bank: Name of the bank.
        :return: None
        """
        self.getBank(to_bank).addTransaction(-1 * self.getAccount(from_account).getFinalBalance())

    def addBank(self, name):
        """
        Adds a bank
        :param name: Name of the bank
        :return:
        """
        self.banks.append(Bank(name=name))

    def getBank(self, name):
        """
        Retrieves a bank
        :param name: Bank name
        :return:
        """
        try:
            return [d for d in self.banks if d.name == name][0]
        except:
            return None


class Bank:
    """
    Basic bank object.
    """
    def __init__(self, name, initial_balance=0):
        self.name = name
        self.balance = initial_balance

    def addTransaction(self, amount):
        self.balance += amount

    def asdict(self):
        return {"name": self.name, "balance": self.balance}


class EmptyObject:
    def asdict(self):
        return {}

class Txntypes:

    @staticmethod
    def debit() -> str:
        return "Debit"

    @staticmethod
    def credit() -> str:
        return "Credit"

    @staticmethod
    def required() -> str:
        return "Required"

    @staticmethod
    def optional() -> str:
        return "Optional"
