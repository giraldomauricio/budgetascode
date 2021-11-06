import xlsxwriter

from BudgetMe.Account import Account
from BudgetMe.Bank import Bank
from BudgetMe.Forecast import Forecast
from BudgetMe.BudgetException import *


class Budget:
    """
    Budget is the mayor object of the application.
    """

    def __init__(self, year, daysof=1, start=1, end=12):
        self.year = year
        self.transactions = []
        self.daysof = daysof
        self.days_labels = [""] * daysof
        self.banks = []
        self.template = {}
        self.start: int = start
        self.end: int = end

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
        return {"year": self.year, "daysof": self.daysof, "transactions": transactions, "banks": banks,
                "days_labels": self.days_labels, "template": self.template, "start": self.start, "end": self.end}

    def addAccount(self, name, days, category="", frequency=1, start=1, end=12, bank="", periodical=False,
                   txn_mode="Required", use_last=False, parent=None) -> Account:
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
            txn_mode = self.template['txn_mode']
        if (type(days) != list):
            days_array = []
            days_array.append(days)
            days = days_array
        if (len(days) != self.daysof):
            raise Exception("All accounts must have the number of days associated during creation.")
        bank_instance = self.getBank(name=bank)
        account = Account(account=name, year=self.year, category=category, frequency=frequency, start=start,
                          bank=bank_instance, periodical=periodical, txn_mode=txn_mode, budget_start=self.start,
                          budget_end=self.end, parent=parent)
        account.days = days
        account.init(range_start=start, range_end=end)
        self.transactions.append(account)
        self.template = account.asdict()  # Save the basic parameters to be reused and simplify the entries.
        self.template['end'] = end
        return account

    def addSingleAccount(self, name, month, days=[], category="", bank="", periodical=False, txn_mode="Required",
                         use_last=False, parent=None) -> Account:
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
            txn_mode = self.template['txn_mode']
        if (type(days) != list):
            days_array = []
            days_array.append(days)
            days = days_array
        if (len(days) != self.daysof):
            raise Exception("All accounts must have the number of days associated during creation.")
        bank_instance = self.getBank(name=bank)
        account = Account(account=name, year=self.year, category=category, frequency=1, start=month,
                          bank=bank_instance, periodical=periodical, txn_mode=txn_mode, parent=parent)
        account.days = days
        account.init_single_month(month)
        self.transactions.append(account)
        self.template = account.asdict()  # Save the basic parameters to be reused and simplify the entries.
        return account

    def getAccountBalance(self, account_name) -> float:
        """
        Gets the balance of an specified Account. If the account has child accounts, the balance is from the child accounts.
        :param account:
        :return: Float
        """
        balance = 0
        accounts = [d for d in self.transactions if d.parent == account_name]
        if (len(accounts) > 0):
            for account in accounts:
                balance += account.getFinalBalance()
            return balance
        else:
            account = self.getAccount(account_name)
            return account.getFinalBalance()

    def accountHasChildAccounts(self, account_name) -> bool:
        return len(self.getChildAccounts(parent_name=account_name)) > 0

    def getChildAccounts(self, parent_name) -> []:
        """
        Gets the child accounts of a parent Account
        :return:
        """
        return [d for d in self.transactions if d.parent == parent_name]

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

    def getMonthDayBalance(self, month, day) -> float:
        """
        Returns the balance of the specified month and day.
        :param month: Month to query.
        :return:
        """
        balance = 0
        for account in self.transactions:
            balance += account.getMonthDayBalance(month,day)
        return balance

    def getMonthBalance2(self, month) -> float:
        """
        Returns the balance of the specified month.
        :param month: Month to query.
        :return:
        """
        balance = 0
        for account in self.transactions:
            balance += account.getMonthBalance2(month)
        return balance

    def getVarianceForMonth(self, account: str, month: int) -> float:
        """
        Gets the deviation (Forecasted vs Actual) of the month.
        :param month: the month number (1-12)
        :return: The actual deviation
        """
        transactions = self.getAccount(account_name=account).getMonth(month=month)
        dev = 0
        for txn in transactions:
            dev += txn.amount - txn.planned
        return dev

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
        try:
            return [d for d in self.transactions if d.name == account_name][0]
        except:
            raise BudgetAccountNotFound("Account %s not found." % account_name)

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
        self.getAccount(account_name=account_name).correctTransaction(month, day, amount)

    def updatePreviousBalance(self, account_name, month, day, previous):
        """
        Updates a transaction in an account.
        :param account_name: Name of the account.
        :param month: Month to update.
        :param day: Day to update.
        :param amount: Amount to update.
        :return: None
        """
        self.getAccount(account_name=account_name).correctPreviousBalance(month, day, previous)

    def confirmTransaction(self, account_name, month, day):
        """
        Updates a transaction in an account.
        :param account_name: Name of the account.
        :param month: Month to update.
        :param day: Day to update.
        :param amount: Amount to update.
        :return: None
        """
        self.getAccount(account_name=account_name).confirmTransaction(month, day)

    def removeConfirmTransaction(self, account_name, month, day):
        """
        Removes confirmation of a transaction in an account.
        :param account_name: Name of the account.
        :param month: Month to update.
        :param day: Day to update.
        :param amount: Amount to update.
        :return: None
        """
        self.getAccount(account_name=account_name).removeConfirmTransaction(month, day)

    def formatCurrency(self, number) -> str:
        """
        Formats a number in the form of $0000.00
        :param number:
        :return: String
        """
        return "${:,.2f}".format(number)

    def setHtmlToConfirmed(self, txn):
        if(txn.confirmed):
            return " confirmed"
        else:
            return ""

    def generateHTMLTable(self) -> str:
        """
        Generates an HTML string with the entire budget
        :return: HTML in a String.
        """
        html = "<table border=\"1\" cellpadding=\"5\">\n"
        # Months Columns Headers
        html += "\t<tr style=\"background-color: cornflowerblue; color: aliceblue\">\n"
        html += "\t\t<td style=\"text-align: center; font-weight: bold\">" + str(self.year) + "</td>\n"
        for month in range(self.start, self.end + 1):
            html += "\t\t<td colspan=\"" + str(
                self.daysof) + "\" style=\"text-align: center; font-weight: bold\">" + str(
                self.getMonthName(month)) + "</td>\n"
        html += "\t\t<td style=\"background-color: #EEEEEE; color\">&nbsp;</td>\n"
        html += "\t</tr>\n"
        # Days labels columns headers
        html += "\t<tr style=\"background-color: cadetblue; color: aliceblue\">\n"
        html += "\t\t<td style=\"background-color: #EEEEEE; color\">&nbsp;</td>\n"
        for month in range(self.start, self.end + 1):
            for label in self.days_labels:
                html += "\t\t<td style=\"text-align: center; font-weight: bold; font-size: x-small;\">" + label + "</td>\n"
        html += "\t\t<td>Final&nbsp;balances</td>\n"
        html += "\t</tr>\n"
        # ------------
        for row in self.transactions:
            if (self.accountHasChildAccounts(row.name)):
                html += "\t<tr>\n"
                html += "\t\t<td><strong>" + row.name + "</strong></td>\n"
                for month in range(self.start, self.end + 1):
                    for day in row.getMonth(month):
                        html += "\t\t<td style=\"background-color: #EEEEEE;\">&nbsp;</td>\n"
                final_balance = self.getAccountBalance(row.name)
                if (final_balance < 0):
                    html += "\t\t<td  class=\"negative\">" + self.formatCurrency(final_balance) + "</td>\n"
                else:
                    html += "\t\t<td class=\"positive\">" + self.formatCurrency(final_balance) + "</td>\n"
                html += "\t</tr>\n"
                sub_row = self.getChildAccounts(row.name)
                for child in sub_row:
                    html += "\t<tr>\n"
                    html += "\t\t<td class=\"sub_account\">&nbsp;&nbsp;" + child.name + "</td>\n"
                    for month in range(self.start, self.end + 1):
                        for day in child.getMonth(month):
                            if (day.amount > 0):
                                html += "\t\t<td class=\"positive_italic " + self.setHtmlToConfirmed(day) + " \">&nbsp;&nbsp;" + self.formatCurrency(
                                    day.amount) + "</td>\n"
                            elif (day.amount == 0):
                                html += "\t\t<td style=\"background-color: #EEEEEE;\">&nbsp;</td>\n"
                            else:
                                html += "\t\t<td class=\"negative_italic " + self.setHtmlToConfirmed(day) + " \">&nbsp;&nbsp;" + self.formatCurrency(
                                    day.amount) + "</td>\n"
                    final_balance = self.getAccountBalance(child.name)
                    if (final_balance < 0):
                        html += "\t\t<td  class=\"negative_italic\">" + self.formatCurrency(final_balance) + "</td>\n"
                    else:
                        html += "\t\t<td class=\"positive_italic\">" + self.formatCurrency(final_balance) + "</td>\n"
                    html += "\t</tr>\n"
            else:
                html += "\t<tr>\n"
                html += "\t\t<td>" + row.name + "</td>\n"
                for month in range(self.start, self.end + 1):
                    for day in row.getMonth(month):
                        if (day.amount > 0):
                            html += "\t\t<td class=\"positive " + self.setHtmlToConfirmed(day) + " \">" + self.formatCurrency(day.amount) + "</td>\n"
                        elif (day.amount == 0):
                            html += "\t\t<td style=\"background-color: #EEEEEE;\">&nbsp;</td>\n"
                        else:
                            html += "\t\t<td class=\"negative " + self.setHtmlToConfirmed(day) + " \">" + self.formatCurrency(
                                day.amount) + "</td>\n"
                final_balance = row.getFinalBalance()
                if (final_balance < 0):
                    html += "\t\t<td  class=\"negative\">" + self.formatCurrency(
                        row.getFinalBalance()) + "</td>\n"
                else:
                    html += "\t\t<td class=\"positive\">" + self.formatCurrency(
                        row.getFinalBalance()) + "</td>\n"
                html += "\t</tr>\n"
        # ------------
        html += "\t<tr style=\"background-color: aliceblue\">\n"
        html += "\t\t<td>Balances</td>\n"
        for month in range(self.start, self.end + 1):
            for day in range(1, self.daysof + 1):
                monthly_balance = self.getMonthDayBalance(month, day)
                if (monthly_balance > 0):
                    html += "\t\t<td class=\"positive centered\">" + self.formatCurrency(
                        monthly_balance) + "</td>\n"
                else:
                    html += "\t\t<td class=\"negative centered\">" + self.formatCurrency(
                        monthly_balance) + "</td>\n"
        html += "\t\t<td>&nbsp;</td>\n"
        html += "\t</tr>\n"
        # ------------
        # Monthly Balance
        html += "\t<tr style=\"background-color: aliceblue\">\n"
        html += "\t\t<td>Monthly&nbsp;balance</td>\n"
        for month in range(self.start, self.end + 1):
            monthly_balance = self.getMonthBalance(month)
            if (monthly_balance > 0):
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\" class=\"positive centered\">" + self.formatCurrency(
                    monthly_balance) + "</td>\n"
            else:
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\"  class=\"negative centered\">" + self.formatCurrency(
                    monthly_balance) + "</td>\n"
        html += "\t\t<td>&nbsp;</td>\n"
        html += "\t</tr>\n"
        # Running Balances
        html += "\t<tr>\n"
        html += "\t\t<td>Running&nbsp;balance</td>\n"
        for month in range(self.start, self.end + 1):
            running_balance = self.getRunningBalance(month)
            if (running_balance > 0):
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\" class=\"positive, centered\">" + self.formatCurrency(
                    running_balance) + "</td>\n"
            else:
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\"  class=\"negative, centered\">" + self.formatCurrency(
                    running_balance) + "</td>\n"
        total_balance = self.getFinalBalance()
        if (total_balance < 0):
            html += "\t\t<td   class=\"negative, centered\">&nbsp;" + self.formatCurrency(
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
        html += "</tr>\n"
        html += "</table>"
        html += "</tr>\n"
        html += "</table>"
        css = """<style type="text/css">
		table {
			font-size: small;
			font-family: 'Helvetica';
			border-collapse: collapse;
		}
		.sub_account {
		    font-size: small;
			font-family: 'Helvetica';
			font-style: italic;
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
		.positive_italic {
			font-size: smaller;
			font-family: 'Helvetica';
			background-color: #bfffd5;
			font-style: italic;
		}
		.negative_italic {
			font-size: smaller;
			font-family: 'Helvetica';
			background-color: #fde1e5;
			font-style: italic;
		}
		.centered {
            text-align: center;
        }
        .confirmed {
            text-decoration: green underline overline wavy;
        }
	</style>"""
        body = "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\">\n<title>Report</title>\n" + css + "</head>\n<body>\n" + html + "\n</body>\n</html>"
        return body

    # TODO: Fix Excel generation. The columns are not considering Budgets of less than twelve months.
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
            if (self.accountHasChildAccounts(row.name)):
                child_accounts = self.getChildAccounts(row.name)
                row_counter += 1
                worksheet.write("A%s" % row_counter, row.name)
                for child in child_accounts:
                    row_counter += 1
                    worksheet.write("A%s" % row_counter, "- " + child.name)
                    days_counter = 0
                    for txn in child.forecast_array:
                        days_counter += 1
                        col = 65 + days_counter
                        worksheet.write("%s%s" % (chr(col), row_counter), txn.amount)
                    days_counter += 1
                    col = 65 + days_counter
                    worksheet.write("%s%s" % (chr(col), row_counter), child.getFinalBalance())
            else:
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
        txn = Forecast(1, 1, -1 * self.getAccount(from_account).getFinalBalance())
        self.getBank(to_bank).addTransaction(txn)

    def addBank(self, name):
        """
        Adds a bank
        :param name: Name of the bank
        :return:
        """
        self.banks.append(Bank(name=name))

    def getBank(self, name) -> Bank:
        """
        Retrieves a bank
        :param name: Bank name
        :return:
        """
        try:
            return [d for d in self.banks if d.name == name][0]
        except:
            return None

    @staticmethod
    def createForecastFromJson(forecast_json: dict) -> Forecast:
        """
        Creates a new Forecast object from a Forecast Dictionary.
        :param forecast_json: The json representation of the Forecast
        :return:
        """
        return Forecast(month=forecast_json['month'], day=forecast_json['day'], amount=forecast_json['amount'],
                        previous=forecast_json['previous'])

    @staticmethod
    def createBankFromJson(bank_json: dict) -> Bank:
        """
        Creates a new Bank object from a Bank Dictionary.
        :param bank_json: The json representation of the Bank
        :return:
        """
        bank = Bank(name=bank_json['name'], initial_balance=bank_json['balance'])
        for txn in bank_json['transactions']:
            bank.transactions.append(txn)
        return bank

    @staticmethod
    def createAccountFromJson(account_json: dict) -> Account:
        """
        Creates a new Account object from an Account Dictionary.
        :param account_json: The json representation of the Account
        :return:
        """
        bank = Budget.createBankFromJson(account_json['bank'])
        account = Account(account_json['account'], year=account_json['year'], category=account_json['category'],
                          frequency=account_json['frequency'], start=account_json['start'], bank=bank,
                          periodical=account_json['periodical'], txn_mode=account_json['txn_mode'],
                          budget_start=account_json['budget_start'], budget_end=account_json['budget_end'],
                          parent=account_json['parent'])
        for forecast in account_json['forecast_array']:
            account.forecast_array.append(Budget.createForecastFromJson(forecast))
        return account

    @staticmethod
    def createBudgetFromJson(budget_json):
        """
        Creates a new Budget object from an Budget Dictionary.
        :param account_json: The json representation of the Budget
        :return: Budget
        """
        budget = Budget(budget_json['year'], daysof=budget_json['daysof'])
        budget.days_labels = budget_json['days_labels']
        for account in budget_json['transactions']:
            budget.transactions.append(Budget.createAccountFromJson(account))
        return budget
