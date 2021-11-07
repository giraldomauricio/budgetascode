from BudgetMe.Account import *

if __name__ == '__main__':
    budget = Budget(2022)
    budget.addBank("Checkings")
    budget.addBank("Savings")
    budget.days_labels = ["H1","H2"]
    budget.addAccount("Starting balance", days=[300, 0], category="Savings", frequency=12, start=1, bank="Checking")
    budget.addAccount("Payroll", days=[1500, 1500], category="Job", bank="Work")
    budget.addAccount("Rent", days=[-1200,0], category="House", bank="Home")
    budget.addAccount("Groceries", days=[0,-350], category="Expenses", bank="Checkings")
    budget.addAccount("Water", days=[-200, 0], category="Utilities", frequency=3, start=1, bank="Checking")
    budget.addAccount("Light", days=[-150, 0], category="Utilities", bank="Checkings")
    budget.addAccount("Gas", days=[-60, -60], category="Car", bank="Checkings")
    budget.addAccount("Car loan", days=[-300, 0], category="Car", bank="Checkings")
    budget.addAccount("College loan", days=[0, -500], category="Car", bank="Checkings")
    budget.addAccount("Credit card", days=[-150, 0], category="Car", bank="Checkings")
    budget.addAccount("Savings", days=[-200, -200], category="Savings", frequency=1, start=3, bank="Checking")
    budget.addSingleAccount("Tax", month=3, days=[2000, 0], category="Taxes", bank="Checkings")
    budget.transferFromAccountToBank(from_account="Savings", to_bank="Savings")
    budget.generateHtmlFile(file_name="demo_basic.html")
    budget.generateExcelFile(filename="demo_basic.xlsx")