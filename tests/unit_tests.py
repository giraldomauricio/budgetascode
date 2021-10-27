import unittest
from BudgetMe.Forecast import Forecast
from BudgetMe.Budget import Budget
from BudgetMe.Account import Account
from BudgetMe.Bank import Bank
from datetime import date


class BudgetMeTestCase(unittest.TestCase):

    def test_basic_instance(self):
        bm = Account()
        todays_date = date.today()
        year = todays_date.year
        self.assertEqual(year, bm.year)
        bm_2 = Account(year=2020)
        self.assertNotEqual(year, bm_2.year)
        self.assertEqual(2020, bm_2.year)
        bm_3 = Account(year="foo")
        self.assertNotEqual("foo", bm_3.year)
        self.assertEqual(year, bm_3.year)
        bm_4 = Account(year="Cat")
        self.assertEqual(year, bm_4.year)

    def test_init_budget(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10, 20]
        bm.init()
        self.assertEqual(24, len(bm.forecast_array))
        self.assertEqual(1, bm.forecast_array[0].day)
        self.assertEqual(2, bm.forecast_array[1].day)
        self.assertEqual(1, bm.forecast_array[0].month)
        self.assertEqual(1, bm.forecast_array[1].month)
        self.assertEqual(2, bm.forecast_array[2].month)
        self.assertEqual(2, bm.forecast_array[3].month)

    def test_init_budget_wrong(self):
        bm = Account(account="Foo", year=2020)
        bm.days = ["Foo", 20]
        try:
            bm.init()
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_init_budget_that_runs_for_specific_range(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [0, -10]
        bm.init(range_start=1, range_end=3)
        self.assertEqual(-30, bm.getFinalBalance())

    def test_init_budget_that_runs_for_specific_range_wrong(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [0, -10]
        try:
            bm.init(range_start=4, range_end=3)
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_init_budget_that_runs_for_single_day(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [0, -10]
        bm.init_single_month(month=3)
        self.assertEqual(-10, bm.getFinalBalance())

    def test_init_assignments(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10, 20]
        bm.init()
        x, y = bm.getMonth(1)
        self.assertEqual(10, x.amount)
        self.assertEqual(20, y.amount)

    def test_reassignments(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10, 20]
        bm.init()
        bm.setAmount(month=1, day=1, amount=-200)
        x, y = bm.getMonth(1)
        self.assertEqual(-200, x.amount)
        self.assertEqual(20, y.amount)

    def test_simplified_account_entry(self):
        bm = Budget(2021)
        bm.addAccount("Water", days=[-100], category="Utilities", frequency=3, start=2, bank="Checking",
                      txn_mode="Required")
        bm.addAccount("Pest Control", days=[-200], use_last=True)
        self.assertEqual(-1200, bm.getFinalBalance())

    def test_detect_negative_months(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10]
        bm.init()
        bm.setAmount(month=1, day=1, amount=-20)
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
        bm.setAmount(month=1, day=1, amount=-80)
        self.assertEqual(30.0, bm.getFinalBalance())

    def test_running_balances_transacions_modified(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10]
        bm.init()
        bm.setAmount(month=2, day=1, amount=-15)
        self.assertEqual(5, bm.getRunningBalance(month=3))

    def test_get_balance_previous_month(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10]
        bm.init()
        self.assertEqual(20, bm.getBalancePreviousMonth(month=3))
        self.assertEqual(0, bm.getBalancePreviousMonth(month=1))

    def test_transer_balance_previous_month(self):
        bm = Account(account="Foo", year=2020)
        bm.days = [10, -5]
        bm.init()
        self.assertEqual(60, bm.getFinalBalance())
        x, y = bm.getMonth(2)
        self.assertEqual(5, x.previous)

    def test_add_account_with_single_transaction(self):
        budget = Budget(2020, daysof=2)
        try:
            budget.addSingleAccount("Foo", month=3, days=[10, 20])
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_budget_of_less_than_twelve_months(self):
        budget = Budget(2020, daysof=2, start=10, end=12)
        budget.addAccount("Foo", days=[10, 0], start=10)
        self.assertEqual(6, len(budget.getAccount("Foo").forecast_array))

    def test_all_transactions_have_the_same_days(self):
        budget = Budget(2020, daysof=2)
        budget.addAccount("Foo", days=[10, 20])
        budget.addAccount("Bar", days=[5, 0])
        self.assertEqual(24, len(budget.transactions[0].forecast_array))
        self.assertEqual(24, len(budget.transactions[1].forecast_array))

    def test_all_transactions_have_the_same_days_error(self):
        budget = Budget(2020, daysof=2)
        try:
            budget.addAccount("Foo", days=[10])
            self.assertTrue(False)
        except:
            self.assertTrue(True)
        budget.addAccount("Bar", days=[5, 0])
        self.assertEqual(24, len(budget.transactions[0].forecast_array))

    def test_total_balance_two_accounts(self):
        budget = Budget(2020)
        budget.addAccount("Foo", days=[10])
        budget.addAccount("Bar", days=[5])
        self.assertEqual(180, budget.getFinalBalance())

    def test_running_balance_two_accounts(self):
        budget = Budget(2020)
        budget.addAccount("Foo", days=[10])
        budget.addAccount("Bar", days=[5])
        self.assertEqual(45, budget.getRunningBalance(3))

    def test_update_transaction(self):
        budget = Budget(2020)
        budget.addAccount("Foo", days=[10])
        budget.addAccount("Bar", days=[0])
        budget.updateTransaction("Bar", month=1, day=1, amount=100)
        self.assertEqual(220, budget.getFinalBalance())

    def test_calculate_variance(self):
        budget = Budget(2020)
        budget.addAccount("Foo", days=[10])
        budget.addAccount("Bar", days=[0])
        budget.updateTransaction("Bar", month=1, day=1, amount=100)
        self.assertEqual(0, budget.getVarianceForMonth("Foo", 1))
        self.assertEqual(100, budget.getVarianceForMonth("Bar", 1))
        budget.updateTransaction("Foo", month=1, day=1, amount=90)
        self.assertEqual(100, budget.getVarianceForMonth("Bar", 1))

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
        txn = Forecast(1, 1, 10)
        bank.addTransaction(txn)
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
        result = budget.detectNegativeBalance()
        self.assertEqual(6, result['month'])
        self.assertEqual(-20, result['balance'])

    def test_plan_payoff(self):
        budget = Budget(2020)
        budget.addBank("FooBank")
        budget.payOff("Bar", amount=100, time=3, start=2, bank="FooBank")
        payoff = budget.getAccount("Bar")
        payments_recorded = [d for d in payoff.forecast_array if d.amount > 0]
        self.assertEqual(3, len(payments_recorded))

    def test_negative_prevention(self):
        budget = Budget(2020)
        budget.addBank("FooBank")
        budget.addAccount("Starting Balance", days=[100], category="Credit Card", bank="FooBank", frequency=12, start=1)
        budget.addAccount("Foo", days=[-20], category="Credit Card", bank="FooBank")
        result = budget.detectNegativeBalance()
        self.assertEqual(6, result['month'])
        self.assertEqual(-20, result['balance'])
        budget.preventNegativeBalance()
        result2 = budget.detectNegativeBalance()
        self.assertEqual(0, result2['month'])
        self.assertEqual(0, result2['balance'])

    def test_transfer_from_account_to_bank(self):
        budget = Budget(2020)
        budget.addBank("FooBank")
        budget.addBank("Bar")
        budget.addAccount("FooAccount", days=[10], category="Credit Card", bank="FooBank")
        budget.transferFromAccountToBank(from_account="FooAccount", to_bank="Bar")
        self.assertEqual(-120, budget.getBank("Bar").balance)

    def test_parent_accounts(self):
        budget = Budget(2020)
        budget.addBank("FooBank")
        budget.addBank("Bar")
        budget.addAccount("Parent", days=[-10], category="Credit Card", bank="FooBank")
        budget.addAccount("Child 1", days=[-10], category="Credit Card", bank="FooBank", parent="Parent")
        budget.addAccount("Child 2", days=[-10], category="Credit Card", bank="FooBank", parent="Parent")
        self.assertEqual(2, len(budget.getChildAccounts(parent_name="Parent")))

    def test_get_balance_of_account(self):
        budget = Budget(2020)
        budget.addBank("FooBank")
        budget.addAccount("Parent", days=[-10], category="Credit Card", bank="FooBank")
        self.assertEqual(-120, budget.getAccountBalance("Parent"))

    def test_balances_of_parent_accounts(self):
        budget = Budget(2020)
        budget.addBank("FooBank")
        budget.addBank("Bar")
        budget.addAccount("Parent", days=[-10], category="Credit Card", bank="FooBank")
        budget.addAccount("Child 1", days=[-10], category="Credit Card", bank="FooBank", parent="Parent")
        budget.addAccount("Child 2", days=[-10], category="Credit Card", bank="FooBank", parent="Parent")
        budget.addAccount("No child", days=[-10], category="Credit Card", bank="FooBank")
        self.assertEqual(0, len(budget.getChildAccounts(parent_name="No child")))
        self.assertEqual(2, len(budget.getChildAccounts(parent_name="Parent")))
        self.assertEqual(-240, budget.getAccountBalance("Parent"))


    def test_calculate_savings(self):
        budget = Budget(2020)
        budget.addBank("FooBank")
        budget.addBank("Bar")
        budget.addAccount("Required 1", days=[-10], category="Credit Card", bank="FooBank", txn_mode="Required")
        budget.addAccount("Optional 1", days=[-10], category="Credit Card", bank="FooBank", txn_mode="Optional")
        budget.addAccount("Optional 2", days=[-10], category="Credit Card", bank="FooBank", txn_mode="Optional")
        savings = budget.calcualtePotentialSavings()
        self.assertEqual(-240, savings)

    def test_convert_from_json_forecast_to_forecast_object(self):
        json_forecast = {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 1, 'day': 2, 'amount': 3, 'planned': 3,
                         'previous': 0}
        forecast = Budget.createForecastFromJson(json_forecast)
        self.assertEqual("Forecast", str(type(forecast).__name__))

    def test_convert_from_json_bank_to_bank_object(self):
        json_forecast = {'name': 'Foo', 'balance': 100, 'transactions': []}
        bank = Budget.createBankFromJson(json_forecast)
        self.assertEqual("Bank", str(type(bank).__name__))

    def test_convert_from_json_account_to_account_object(self):
        account_json = {'name': 'Foo', 'year': 2022, 'forecast_array': [], 'account': 'Foo', 'days': [],
                        'category': 'Bar', 'frequency': 1, 'start': 2,
                        'bank': {'name': 'FooBank', 'balance': 0, 'transactions': []}, 'periodical': True,
                        'txn_mode': 'Optional', 'budget_start': 1, 'budget_end': 2, 'parent': 'None',
                        'transfer_balance': "False"}
        account = Budget.createAccountFromJson(account_json)
        self.assertEqual("Account", str(type(account).__name__))
        self.assertEqual("Bank", str(type(account.bank).__name__))

    def test_convert_from_json_budget_to_budget_object(self):
        budget_json = {'year': 2021, 'daysof': 1, 'transactions': [{'name': 'Optional 1', 'year': 2021,
                                                                    'forecast_array': [
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 1, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': 0},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 2, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -10},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 3, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -20},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 4, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -30},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 5, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -40},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 6, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -50},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 7, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -60},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 8, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -70},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 9, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -80},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 10, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -90},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 11, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -100},
                                                                        {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                         'month': 12, 'day': 1, 'amount': -10,
                                                                         'planned': -10, 'previous': -110}],
                                                                    'account': 'Optional 1', 'days': [-10],
                                                                    'category': 'Credit Card', 'frequency': 1,
                                                                    'start': 1,
                                                                    'bank': {'name': 'FooBank', 'balance': -120,
                                                                             'transactions': [{
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}, {
                                                                                 'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                 'amount': -10}]},
                                                                    'periodical': False, 'txn_mode': 'Optional',
                                                                    'budget_start': 2, 'budget_end': 2,
                                                                    'parent': 'None', 'transfer_balance': 'False'}],
                       'banks': [{'name': 'FooBank', 'balance': -120,
                                  'transactions': [{'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10},
                                                   {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'amount': -10}]}],
                       'days_labels': [''], 'template': {'name': 'Optional 1', 'year': 2021, 'forecast_array': [
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 1, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': 0},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 2, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -10},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 3, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -20},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 4, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -30},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 5, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -40},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 6, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -50},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 7, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -60},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 8, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -70},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 9, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -80},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 10, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -90},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 11, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -100},
                {'id': '535bf824-99f1-329c-a4d9-68e0887ca66f', 'month': 12, 'day': 1, 'amount': -10, 'planned': -10,
                 'previous': -110}], 'account': 'Optional 1', 'days': [-10], 'category': 'Credit Card', 'frequency': 1,
                                                         'start': 1, 'bank': {'name': 'FooBank', 'balance': -120,
                                                                              'transactions': [{
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}, {
                                                                                  'id': '535bf824-99f1-329c-a4d9-68e0887ca66f',
                                                                                  'amount': -10}]},
                                                         'periodical': False, 'txn_mode': 'Optional', 'budget_start': 2,
                                                         'budget_end': 2, 'parent': 'None',
                                                         'transfer_balance': 'False'}}
        budget = Budget.createBudgetFromJson(budget_json)
        self.assertEqual("Budget", str(type(budget).__name__))


if __name__ == '__main__':
    unittest.main()
