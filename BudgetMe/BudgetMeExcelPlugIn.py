from BudgetMe.Budget import Budget


class BudgetMeHtml(Budget):

    def __init__(self, year, daysof=1, start=1, end=12):
        super(BudgetMeHtml, self).__init__(year, daysof, start, end)

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