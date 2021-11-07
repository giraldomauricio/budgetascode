from BudgetMe.Budget import Budget

class B2022():

    @staticmethod
    def run() -> Budget:
        budget = Budget(2022, daysof=2, start=10, end=12)
        budget.addBank("BoA Checking")
        budget.addBank("BoA Savings")
        budget.addBank("PayPal")
        budget.addBank("Apple")
        budget.addBank("AMEX")
        budget.addBank("Visa")
        budget.days_labels = ["H1 (1)", "H2 (15)"]
        budget.addAccount("Adjustments", days=[0, 0], category="Banking", bank="BoA Checking", start=10)
        budget.addAccount("Checking", days=[2000.96, 2000.96], category="Job", bank="BoA Checking", start=10)
        budget.addAccount("Mortgage", days=[-1500, 0], category="Mortgage", bank="BoA Checking", start=10)
        budget.updateAccountsBalances()
        return budget
