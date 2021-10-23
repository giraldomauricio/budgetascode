from datetime import date

import xlsxwriter

"""
BudgetMe is an approach to BaaC (Budget as a Code).
Author: Mauricio Giraldo <mgiraldo@gmail.com> 
"""

class Account:
    """
    Account is the base of any money movement in a year.
    """
    def __init__(self, account="", year=None, category="", frequency=1, start=1, bank=None):
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

    def asdict(self):
        """
        Converts the object variables into a dictionary
        :return:
        dict
        """
        forecast_array = []
        for forecast in self.forecast_array:
            forecast_array.append(forecast.asdict())
        return {"name": self.name, "year": self.year, "forecast_array": forecast_array, "account": self.account, "days": self.days, "category": self.category, "frequency": self.frequency, "start": self.start, "bank": self.bank.asdict()}

    def init_single_month(self, month):
        self.init(range_start=month, range_end=month)

    def init(self, range_start=1, range_end=12):
        frequency_counter = 0
        for i in range(1,13):
            if(i>= range_start and i<= range_end):
                if (frequency_counter == self.frequency):
                    frequency_counter = 0
                if(i>=self.start):
                    frequency_counter += 1
                if(frequency_counter == 1):
                    for j in range(1,len(self.days)+1):
                        self.forecast_array.append(Forecast(month=i, day=j, amount=self.days[j-1], previous=self.getBalancePreviousMont(i)))
                        if(self.bank):
                            self.bank.addTransaction(self.days[j-1])
                    # frequency_counter = 0
                else:
                    for j in range(1,len(self.days)+1):
                        self.forecast_array.append(Forecast(month=i, day=j, amount=0, previous=self.getBalancePreviousMont(i)))
            else:
                for j in range(1, len(self.days) + 1):
                    self.forecast_array.append(Forecast(month=i, day=j, amount=0, previous=self.getBalancePreviousMont(i)))

    def getBalancePreviousMont(self, month):
        balance = 0
        if (month > 1):
            for i in range(1, month):
                balance += self.getMonthBalance(i)
        return balance

    def getMonth(self, month):
        return [d for d in self.forecast_array if d.month == month]

    def setActual(self, month, day, amount):
        array_start = (month - 1) * 2
        if (day == 2):
            array_start += 1
        [c for c in [d for d in self.forecast_array if d.month == month] if c.day == day][0].amount = amount

    def getFinalBalance(self):
        balance = 0
        for month in range(1,13):
            balance += self.getMonthBalance(month)
        return balance

    def getMonthBalance(self, month):
        balance = 0
        month_transactions = [d for d in self.forecast_array if d.month == month]
        for txn in month_transactions:
            balance += txn.amount
        return balance

    def getNegativeMonths(self) -> []:
        results = []
        for i in range(1,13):
            balance = self.getMonthBalance(i)
            if(balance < 0):
                results.append({"month": i, "balance": balance})
        return results

    def getRunningBalance(self, month):
        balance = 0
        for days in range(1,month+1):
            balance += self.getMonthBalance(days)
        return balance


class Forecast:

    def __init__(self, month, day, amount, previous=0):
        self.month = month
        self.day = day
        self.amount = amount
        self.previous = previous  # Balance transfer from previous month

    def asdict(self):
        return {"month": self.month, "day": self.day, "amount": self.amount, "previous": self.previous}


class Budget:

    def __init__(self, year, daysof=1):
        self.year = year
        self.transactions = []
        self.daysof = daysof
        self.days_labels = [""] * daysof
        self.banks = []

    def asdict(self) -> dict:
        """
        Converts the class structure into a dictionary.
        :return: dict
        """
        transactions = []
        for txn in self.transactions:
            transactions.append(txn.asdict())
        return {"year": self.year, "daysof": self.daysof, "transactions": transactions}

    def addAccount(self, name, days=0, category="", frequency=1, start=1, bank=""):
        if(type(days) != list):
            days_array = []
            days_array.append(days)
            days = days_array
        if(len(days) != self.daysof):
            raise Exception("All accounts must have the number of days associated during creation.")
        bank_instance = self.getBank(name=bank)
        account = Account(account=name, year=self.year, category=category, frequency=frequency, start=start, bank=bank_instance)
        account.days = days
        account.init()
        self.transactions.append(account)

    def addSingleAccount(self, name, month, days=[], category="", bank=""):
        if (type(days) != list):
            days_array = []
            days_array.append(days)
            days = days_array
        if (len(days) != self.daysof):
            raise Exception("All accounts must have the number of days associated during creation.")
        bank_instance = self.getBank(name=bank)
        account = Account(account=name, year=self.year, category=category, frequency=1, start=month,
                          bank=bank_instance)
        account.days = days
        account.init_single_month(month)
        self.transactions.append(account)

    def getCategories(self) -> list:
        """
        Get the categories from all accounts added.
        :return: list
        """
        result = []
        for account in self.transactions:
            if(account.category not in result):
                result.append(account.category)
        return result

    def getBalanceByCategories(self) -> dict:
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

    def getMonthBalance(self, month):
        balance = 0
        for account in self.transactions:
            balance += account.getMonthBalance(month)
        return balance

    def getTotalBalanceByCategory(self, category):
        transactions = [d for d in self.transactions if d.category == category]
        balance = 0
        for transaction in transactions:
            balance += transaction.getFinalBalance()
        return balance

    def getAccount(self, account_name)->Account:
        return [d for d in self.transactions if d.name == account_name][0]

    def getMonthName(self, month_number):
        months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
        if(month_number < 1 or month_number > 12):
            raise Exception("Month must be between 1 and 12.")
        return months[month_number-1]

    def updateTransaction(self, account_name, month, day, amount):
        self.getAccount(account_name=account_name).setActual(month, day, amount)

    def formatCurrency(self, number):
        return "${:,.2f}".format(number)

    def generateHTMLTable(self):
        html = "<table style=\"font-size: small; font-family: 'Helvetica'; border-collapse: collapse\" border=\"1\" cellpadding=\"5\">\n"
        # Months Columns Headers
        html += "\t<tr style=\"background-color: cornflowerblue; color: aliceblue\">\n"
        html += "\t\t<td style=\"text-align: center; font-weight: bold\">" + str(self.year) + "</td>\n"
        for month in range(1,13):
            html += "\t\t<td colspan=\"" + str(self.daysof) + "\" style=\"text-align: center; font-weight: bold\">" + str(self.getMonthName(month)) + "</td>\n"
        html += "\t\t<td>&nbsp;</td>\n"
        html += "\t</tr>\n"
        # Days labels columns headers
        html += "\t<tr style=\"background-color: cadetblue; color: aliceblue\">\n"
        html += "\t\t<td>&nbsp;</td>\n"
        for month in range(1, 13):
            for label in self.days_labels:
                html += "\t\t<td style=\"text-align: center; font-weight: bold; font-size: x-small;\">" + label + "</td>\n"
        html += "\t\t<td>Final&nbsp;balances</td>\n"
        html += "\t</tr>\n"
        for row in self.transactions:
            html += "\t<tr>\n"
            html += "\t\t<td>" + row.name + "</td>\n"
            for month in range(1,13):
                for day in row.getMonth(month):
                    if(day.amount > 0):
                        html += "\t\t<td style=\"text-align: right\">" + self.formatCurrency(day.amount) + "</td>\n"
                    elif(day.amount == 0):
                        html += "\t\t<td style=\"text-align: right; color: red\">&nbsp;</td>\n"
                    else:
                        html += "\t\t<td style=\"text-align: right; color: red\">" + self.formatCurrency(day.amount) + "</td>\n"
            final_balance = row.getFinalBalance()
            if(final_balance < 0):
                html += "\t\t<td style=\"text-align: right; color: red; font-weight: bold\">" + self.formatCurrency(row.getFinalBalance()) + "</td>\n"
            else:
                html += "\t\t<td style=\"text-align: right; font-weight: bold\">" + self.formatCurrency(row.getFinalBalance()) + "</td>\n"
            html += "\t</tr>\n"
        # Monthly Balance
        html += "\t<tr style=\"background-color: aliceblue\">\n"
        html += "\t\t<td>Monthly&nbsp;balance</td>\n"
        for month in range(1, 13):
            monthly_balance = self.getMonthBalance(month)
            if (monthly_balance > 0):
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\" style=\"text-align: center; font-weight: bold\">" + self.formatCurrency(
                    monthly_balance) + "</td>\n"
            else:
                html += "\t\t<td colspan=\"" + str(
                    self.daysof) + "\" style=\"text-align: center; font-weight: bold; color: red\">" + self.formatCurrency(
                    monthly_balance) + "</td>\n"
        html += "\t\t<td>&nbsp;</td>\n"
        html += "\t</tr>\n"
        # Running Balances
        html += "\t<tr>\n"
        html += "\t\t<td>Running&nbsp;balance</td>\n"
        for month in range(1, 13):
            running_balance = self.getRunningBalance(month)
            if (running_balance > 0):
                html += "\t\t<td colspan=\"" + str(self.daysof) + "\" style=\"text-align: center; weight: bold\">" +  self.formatCurrency(running_balance) + "</td>\n"
            else:
                html += "\t\t<td colspan=\"" + str(self.daysof) + "\" style=\"text-align: center; weight: bold; color: red\">" +  self.formatCurrency(running_balance) + "</td>\n"
        total_balance = self.getFinalBalance()
        if(total_balance < 0):
            html += "\t\t<td  style=\"text-align: right; font-weight: bold; color: red\">&nbsp;" + self.formatCurrency(total_balance) + "</td>\n"
        else:
            html += "\t\t<td  style=\"text-align: right; font-weight: bold\">&nbsp;" + self.formatCurrency(total_balance) + "</td>\n"
        html += "\t</tr>\n"
        html += "<table style=\"font-size: small; font-family: 'Helvetica'; border-collapse: collapse\" border=\"1\" cellpadding=\"5\">\n<br>"
        html += "<td colspan=\"2\" style=\"text-align: center; font-weight: bold \">Categories</td>\n"
        categories = self.getBalanceByCategories()
        for k,v in categories.items():
            html += "<tr>\n"
            html += "\t<td>" + k + "</td><td style=\"text-align: right\">" + self.formatCurrency(v) + "</td>\n"
            html += "<tr>\n"
        html += "</table>"
        html += "\t</tr>\n"
        html += "<table style=\"font-size: small; font-family: 'Helvetica'; border-collapse: collapse\" border=\"1\" cellpadding=\"5\">\n<br>"
        html += "<td colspan=\"2\" style=\"text-align: center; font-weight: bold \">Banks</td>\n"
        for bank in self.banks:
            html += "<tr>\n"
            html += "\t<td>" + bank.name + "</td><td style=\"text-align: right\">" + self.formatCurrency(bank.balance) + "</td>\n"
            html += "<tr>\n"
        html += "</table>"
        body = "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\">\n<title>Report</title>\n</head>\n<body>\n" + html + "\n</body>\n</html>"
        return body

    def generateExcelFile(self, filename="budget.xlsx"):
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)
        worksheet.write('A1', self.year)
        month = 0
        for column in range(1,25,2):
            month += 1
            col = 65 + column
            cell = '%s1' % chr(col)
            merge = '%s1' % chr(col+1)
            worksheet.merge_range("%s:%s" % (cell,merge), str(self.getMonthName(month)))
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
        for column in range(1,25,2):
            month += 1
            col = 65 + column
            cell = '%s%s' % (chr(col),row_counter)
            merge = '%s%s' % (chr(col+1),row_counter)
            worksheet.merge_range("%s:%s" % (cell,merge), str(self.getMonthBalance(month)))
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
        merge = 'B%s' % (row_counter)
        worksheet.merge_range("%s:%s" % (cell, merge), "Categories")
        row_counter += 1
        categories = self.getBalanceByCategories()
        for k,v in categories.items():
            worksheet.write("A%s" % row_counter, k)
            worksheet.write("B%s" % row_counter, v)
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
        workbook.close()

    def generateHtmlFile(self, file_name="report.html"):
        with open(file_name, "w") as text_file:
            text_file.write(self.generateHTMLTable())

    def transferFromAccountToBank(self, from_account, to_bank):
        self.getBank(to_bank).addTransaction(-1 * self.getAccount(from_account).getFinalBalance())

    def addBank(self, name):
        self.banks.append(Bank(name=name))

    def getBank(self, name):
        try:
            return  [d for d in self.banks if d.name == name][0]
        except:
            return None

class Bank:

    def __init__(self, name, initial_balance=0):
        self.name = name
        self.balance = initial_balance

    def addTransaction(self, amount):
        self.balance += amount

    def asdict(self):
        return {"name": self.name, "balance": self.balance}