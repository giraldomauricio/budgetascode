import unittest
from BudgetMe.Account import *
from datetime import date

class BudgetMeTestCase(unittest.TestCase):

    def test_basic_instance(self):
        bm = Account()
        todays_date = date.today()
        year = todays_date.year
        self.assertEqual(year,bm.year)
        bm_2 = Account(year=2020)
        self.assertNotEqual(year, bm_2.year)
        self.assertEqual(2020, bm_2.year)
        bm_3 = Account(year="foo")
        self.assertNotEqual("foo", bm_3.year)
        self.assertEqual(year, bm_3.year)

    def test_init_budget(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10, 20]
        bm.init()
        self.assertEqual(24, len(bm.forecast_array))
        self.assertEqual(1,bm.forecast_array[0].day)
        self.assertEqual(2, bm.forecast_array[1].day)
        self.assertEqual(1,bm.forecast_array[0].month)
        self.assertEqual(1, bm.forecast_array[1].month)
        self.assertEqual(2, bm.forecast_array[2].month)
        self.assertEqual(2, bm.forecast_array[3].month)

    def test_init_budget_that_runs_for_specific_range(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [0, -10]
        bm.init(range_start=1, range_end=3)
        self.assertEqual(-30, bm.getFinalBalance())

    def test_init_budget_that_runs_for_single_day(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [0, -10]
        bm.init_single_month(month=3)
        self.assertEqual(-10, bm.getFinalBalance())

    def test_init_assignments(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10, 20]
        bm.init()
        x,y = bm.getMonth(1)
        self.assertEqual(10, x.amount)
        self.assertEqual(20, y.amount)

    def test_reassignments(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10,20]
        bm.init()
        bm.setActual(month=1,day=1,amount=-200)
        x,y = bm.getMonth(1)
        self.assertEqual(-200, x.amount)
        self.assertEqual(20, y.amount)

    def test_detect_negative_months(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10]
        bm.init()
        bm.setActual(month=1,day=1,amount=-20)
        self.assertEqual(1, len(bm.getNegativeMonths()))

    def test_balances(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10]
        bm.init()
        self.assertEqual(120, bm.getFinalBalance())

    def test_transactions_not_monthly(self):
        bm = Account(account="Foo", year=2020, frequency=3, start=2)
        bm.days = [10]
        bm.init()
        self.assertEqual(40, bm.getFinalBalance())

    def test_running_balances(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10]
        bm.init()
        self.assertEqual(30, bm.getRunningBalance(month=3))

    def test_balances_transactions_modified(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10]
        bm.init()
        bm.setActual(month=1, day=1, amount=-80)
        self.assertEqual(30.0, bm.getFinalBalance())

    def test_running_balances_transacions_modified(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10]
        bm.init()
        bm.setActual(month=2, day=1, amount=-15)
        self.assertEqual(5, bm.getRunningBalance(month=3))

    def test_get_balance_previous_month(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10]
        bm.init()
        self.assertEqual(20, bm.getBalancePreviousMont(month=3))
        self.assertEqual(0, bm.getBalancePreviousMont(month=1))

    def test_transer_balance_previous_month(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10,-5]
        bm.init()
        self.assertEqual(60, bm.getFinalBalance())
        x,y = bm.getMonth(2)
        self.assertEqual(5, x.previous)

    def test_add_account_with_single_transaction(self):
        budget = Budget(2020, daysof=2)
        budget.addSingleAccount("Foo", month=3, days=[10,20])
        self.assertEqual(30, budget.getFinalBalance())

    def test_all_transactions_have_the_same_days(self):
        budget = Budget(2020, daysof=2)
        budget.addAccount("Foo", days=[10,20])
        budget.addAccount("Bar", days=[5,0])
        self.assertEqual(24, len(budget.transactions[0].forecast_array))
        self.assertEqual(24, len(budget.transactions[1].forecast_array))

    def test_all_transactions_have_the_same_days_error(self):
        budget = Budget(2020, daysof=2)
        try:
            budget.addAccount("Foo", days=[10])
            self.assertTrue(False)
        except:
            self.assertTrue(True)
        budget.addAccount("Bar", days=[5,0])
        self.assertEqual(24, len(budget.transactions[0].forecast_array))

    def test_total_balance_two_accounts(self):
        budget = Budget(2020)
        budget.addAccount("Foo",days=[10])
        budget.addAccount("Bar", days=[5])
        self.assertEqual(180,budget.getFinalBalance())

    def test_running_balance_two_accounts(self):
        budget = Budget(2020)
        budget.addAccount("Foo",days = [10])
        budget.addAccount("Bar", days = [5])
        self.assertEqual(45,budget.getRunningBalance(3))

    def test_update_transaction(self):
        budget = Budget(2020)
        budget.addAccount("Foo",days = [10])
        budget.addAccount("Bar", days = [0])
        budget.updateTransaction("Bar", month=1, day=1, amount=100)
        self.assertEqual(220,budget.getFinalBalance())

    def test_get_monthly_balance(self):
        budget = Budget(2020)
        budget.addAccount("Foo", days=[10])
        budget.addAccount("Bar", days=[20])
        self.assertEqual(30, budget.getMonthBalance(3))

    def test_frequency_in_budget(self):
        budget = Budget(2020)
        budget.addAccount("Foo", days=[10], category="Credit Card")
        budget.addAccount("Bar", days=[10], category="Utilities", frequency=3, start=2)
        self.assertEqual(40, budget.getTotalBalanceByCategory("Utilities"))

    def test_get_categorization(self):
        budget = Budget(2020)
        budget.addAccount("Foo", days=[10], category="Credit Card")
        budget.addAccount("Bar", days=[20], category="Utilities")
        budget.addAccount("FooBar", days=[20], category="Credit Card")
        self.assertEqual(360, budget.getTotalBalanceByCategory("Credit Card"))
        self.assertEqual(240, budget.getTotalBalanceByCategory("Utilities"))
        self.assertEqual(0, budget.getTotalBalanceByCategory("Foo"))

    def test_extract_categories(self):
        budget = Budget(2020)
        budget.addAccount("Foo", days=[10], category="Credit Card")
        budget.addAccount("Bar", days=[20], category="Utilities")
        budget.addAccount("FooBar", days=[20], category="Credit Card")
        self.assertEqual(2, len(budget.getCategories()))
        self.assertTrue("Credit Card" in budget.getCategories())
        self.assertTrue("Utilities" in budget.getCategories())
        self.assertTrue("House" not in budget.getCategories())

    def test_get_expense_by_category(self):
        budget = Budget(2020)
        budget.addAccount("Foo", days=[10], category="Credit Card")
        budget.addAccount("Bar", days=[20], category="Utilities")
        budget.addAccount("FooBar", days=[20], category="Credit Card")
        categories = budget.getBalanceByCategories()
        self.assertEqual(2, len(categories))
        self.assertEqual(360, categories['Credit Card'])
        self.assertEqual(240, categories['Utilities'])

    def test_formatting(self):
        budget = Budget(2020)
        self.assertEqual("$12.00", budget.formatCurrency(12))
        self.assertEqual("$12.13", budget.formatCurrency(12.13))

    def test_bank(self):
        bank = Bank(name="Foo")
        bank.addTransaction(10)
        self.assertEqual(10, bank.balance)

    def test_banks(self):
        budget = Budget(2020)
        budget.addBank("Foo")
        budget.addAccount("Foo", days=[10], category="Credit Card", bank="Foo")
        self.assertEqual(120, budget.getBank("Foo").balance)

    def test_negative_balance(self):
        budget = Budget(2020)
        budget.addBank("FooBank")
        budget.addAccount("Starting Balance", days=[100], category="Credit Card", bank="FooBank", frequency=12, start=1)
        budget.addAccount("Foo", days=[-20], category="Credit Card", bank="FooBank")
        result= budget.detectNegativeBalance()
        print(result)
        budget.generateHtmlFile("test.html")
        self.assertEqual(6, result['month'])
        self.assertEqual(-20, result['balance'])

    def test_transfer_from_account_to_bank(self):
        budget = Budget(2020)
        budget.addBank("FooBank")
        budget.addBank("Bar")
        budget.addAccount("FooAccount", days=[10], category="Credit Card", bank="FooBank")
        budget.transferFromAccountToBank(from_account="FooAccount", to_bank="Bar")
        self.assertEqual(-120, budget.getBank("Bar").balance)

if __name__ == '__main__':
    unittest.main()