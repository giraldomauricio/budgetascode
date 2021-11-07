from BudgetMe.Budget import Budget


class BudgetMeHtml(Budget):

    def __init__(self, year, daysof=1, start=1, end=12):
        super(BudgetMeHtml, self).__init__(year, daysof, start, end)

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
                                html += "\t\t<td class=\"positive_italic " + self.setHtmlToConfirmed(
                                    day) + " \">&nbsp;&nbsp;" + self.formatCurrency(
                                    day.amount) + "</td>\n"
                            elif (day.amount == 0):
                                html += "\t\t<td style=\"background-color: #EEEEEE;\">&nbsp;</td>\n"
                            else:
                                html += "\t\t<td class=\"negative_italic " + self.setHtmlToConfirmed(
                                    day) + " \">&nbsp;&nbsp;" + self.formatCurrency(
                                    day.amount) + "</td>\n"
                    final_balance = self.getAccountBalance(child.name)
                    if (final_balance < 0):
                        html += "\t\t<td  class=\"negative_italic\">" + self.formatCurrency(
                            final_balance) + "</td>\n"
                    else:
                        html += "\t\t<td class=\"positive_italic\">" + self.formatCurrency(
                            final_balance) + "</td>\n"
                    html += "\t</tr>\n"
            else:
                html += "\t<tr>\n"
                html += "\t\t<td>" + row.name + "</td>\n"
                for month in range(self.start, self.end + 1):
                    for day in row.getMonth(month):
                        if (day.amount > 0):
                            html += "\t\t<td class=\"positive " + self.setHtmlToConfirmed(
                                day) + " \">" + self.formatCurrency(day.amount) + "</td>\n"
                        elif (day.amount == 0):
                            html += "\t\t<td style=\"background-color: #EEEEEE;\">&nbsp;</td>\n"
                        else:
                            html += "\t\t<td class=\"negative " + self.setHtmlToConfirmed(
                                day) + " \">" + self.formatCurrency(
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
        html += "\t<td style=\"text-align: right\">" + self.formatCurrency(
            self.calcualtePotentialSavings()) + "</td>\n"
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

    def generateHtmlFile(self, file_name="report.html"):
        """
        Generates the file of the HTML Budget.
        :param file_name: Name of the file.
        :return: None
        """
        with open(file_name, "w") as text_file:
            text_file.write(self.generateHTMLTable())