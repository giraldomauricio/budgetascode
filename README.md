# BaC 
## Budget As Code
Advanced personal budget management in Python.

* Author: Mauricio Giraldo
* Version: 1.16.87429b8
* Compatibility: Python 3 (Win/Linux/Mac)

BudgetAsCode (BaC) is a programmatic approach to personal finance. These days, managing is as important as planning for your future. Many budget applications look and feel like an Excel spreadsheet or are designed with a marketing background as a leading strategy. Budget as code lets you see your finances as code in Python, not as a database somewhere. You can create your objects and modify them to see how your finance looks. Check savings, monthly balances to understand where the money is going. Then adjust your entries until you get to the point that you can feel you are not living paycheck to paycheck. The final objective is to end with some savings each month to move to an account to get a healthier personal finance.
BaC includes basic objects to manipulate the data and even a Flask application to see everything from a broad perspective.
BaC is constantly changing and evolving to provide tools that you can use to get better, like potential savings or alerts when a month goes negative.

### Installations

First, run the dependencies' installation:

```shell script
pip install -r requirements.txt
```

Then open any of the two examples:

* demo.py: Basic budget using single transactions per month.
* demo_basic.py: Demo using months with two transaction per month (Like when you get paid twice a month and yoo pay bills either in the first or second half of each month).

Run the example you want:

```shell script
python demo.py
python demo_basic.py
```

Each file will generate an HTML and an Excel file with the budget results.

### Usage

BaC i basically let you add income and expenses into Python as objects. Then you can generate am HTML and/or Excel file of the actual budget. You can manage banks and categories so you can see where the money is going and how much you will have at the end of each month in a 12 month period.

This is how the concept looks in a year:

| 2021|  1 | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | 10  | 11  | 12  |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|Payroll| 1000  | 1000  | 1000  | 1000  | 1000  | 1000  | 1000  | 1000  | 1000  |  1000 |  1000 |  1000 |
|Mortgage| -500  | -500  | -500  | -500  |  -500 | -500  | -500  |  -500 |  -500 |  -500 |  -500 |  -500 |
|Water utility|   |   | -50  |   |   |  50 |   |   |  50 |   |   | 50  |
|Bonus|   | 1000  |   |   |   |   |   |   |   |   |   |  |

#### Example

You start creating an instance of the Budget class with the year you are making the budget:
```python
from BudgetMe.Account import *

budget = Budget(2022)
```

If you plan to record two transactions per account per month (I'll explain this), you start like this:

```python
from BudgetMe.Account import *

budget = Budget(2022,daysof=2)
```
This is how the concept looks in a month:
| |   |   | 
|---|---|---|
|Account| H1  | H2  |
|Payroll| 1000  |   |
|Credit card|   | -200  |

The `daysof` means how often one 'Accounts' gets affected each month. For exampe if you get paid twice a month, you need a value of 2. If you get paid 4 times (Weekly), you use 4.

You can label each transaction per month for easy reading:

```python
from BudgetMe.Account import *

budget = Budget(2022,daysof=2)
budget.days_labels = ["Half 1","Half 2"]
```

Now you can add a Bank (Optional). This will thells the app, where the money is going, or where the money is leaving.

```python
from BudgetMe.Account import *

budget = Budget(2022,daysof=2)
budget.days_labels = ["Half 1","Half 2"]
budget.addBank("Checking")
```

##### Accounts

This is the most basic object. It represents an Account (Like Payroll, Utility bill or Credit Card) that puts or removes money from your budget.

To tell the Budget how an account behaves, you create an account and tell for each of the `daysof` how much money enter or leaves. You can also set a category of the transaction and the bank:

```python
from BudgetMe.Account import *

budget = Budget(2022,daysof=2)
budget.days_labels = ["Half 1","Half 2"]
budget.addBank("Checking")
budget.addAccount("Payroll", days=[1000, 1000], category="Job", bank="Checking")
```

This tells the application that each month, you get $1,000 in the first half of the month and $1,000 the seconf half of the month.

For expenses, you put negative values:

```python
budget.addAccount("Mortgage", days=[-2000,0], category="House", bank="Checking")
```

The last transaction tells that you pay the mortgage ($2,000) only in the first half of the month.

The `days` parameter receives an arry with the same number of items you put in `daysof`. If you don't, you will get an error.

A complete details of an account, includes the type (Debit or Credit), the mode (Required, Optional) and if its Periodical (True or False):

```python
budget.addAccount(account="Netflix", year=2022, category="TV", frequency=1, start=1, bank="Chase", periodical=True, txn_type="Debit", tnx_mode="Optional")
```

If your accounts gets billed in a frequency different that monthly, and starts in a month different that 1 (January), you can specify the frequency:

```python
budget.addAccount("Water bill", days=[-200, 0], category="Utilities", frequency=3, start=2, bank="Checking")
```

This means that you pay the water bill each 3 months, the first half of the month, starting in the month 2 (February).

If you have a transaction that only happens once a year, you can use:

```python
budget.addSingleAccount("Tax", month=3, days=[1000, 0], category="Taxes", bank="Checking")
```
                 
If the accounts only runs for a specific period of time, you can specify between what months it create transacions:

```python
budget.addSingleAccount("Tax", month=3, days=[1000, 0], category="Taxes", bank="Checking", budget_start=6, budget_end=10)
```

Finally, to see your budget, you can generate an HTML and/or an Excel file (The Excel is the representation of the HTML file):

```python
budget.generateHtmlFile(file_name="budget.html")
budget.generateExcelFile(filename="budget.xlsx")
```

You full budget will end up looking like this:

```python
from BudgetMe.Account import *

budget = Budget(2022,daysof=2)
budget.days_labels = ["Half 1","Half 2"]
budget.addBank("Checking")
budget.addAccount("Payroll", days=[1000, 1000], category="Job", bank="Checking")
budget.addAccount("Mortgage", days=[-2000,0], category="House", bank="Checking")
budget.addAccount("Water bill", days=[-200, 0], category="Utilities", frequency=3, start=2, bank="Checking")
budget.addSingleAccount("Tax break", month=3, days=[1000, 0], category="Taxes", bank="Checking")
budget.generateHtmlFile(file_name="budget.html")
budget.generateExcelFile(filename="budget.xlsx")
```

There is no limit on the number of accounts and Banks.

### Parent Accounts

BaC supports parent and child accounts. For example, some of your transactions are registered under one accounts.
Lets say you have a Bank Account called "Chase" and you pay your phone and your rent with it. Also you get your paycheck in that account. You can create this as follows:

```python
from BudgetMe.Account import *

budget = Budget(2022,daysof=2)
budget.days_labels = ["Half 1","Half 2"]
budget.addBank("Checking")
budget.addAccount("Chase", days=[1000, 1000], category="Credit Card", bank="Checking")
budget.addAccount("Paycheck", days=[2000,2000], category="Job", bank="Checking", parent="Chase")
budget.addAccount("Phone", days=[0,-100], category="Phone", bank="Checking", parent="Chase")
budget.addAccount("Rent", days=[-1000,0], category="Phone", bank="Checking", parent="Chase")
budget.getAccountBalance("Chase")
34800
```
34,800 = ((2000 + 2000) x 12) + ((0-100) x 12) + ((-1000 + 0) x 12)

And not 24,000 becase Chase has child accounts.

When you have parent accounts, the balance is calculated from the child accounts. BaC will ignore any input in the parent account.

### Utilities

#### Detecting negative balance

You can tell the application to detect when you will have negative balance. This means you end a month with more expensed that income:

```python
budget.detectNegativeBalance()
```

The application will return the month you will be negative and for how much in a json format:

```json
{'month': 6, 'balance': -20.0}
```

If you don't go negative, the response will be:

```json
{'month': 0, 'balance': 0}
```

#### Payoff

Payoff helps to set the payoff of any amount in a period of time starting on a specific month. Basically creates an account that is divided by the amount of the payment in the range specified.

```python
from BudgetMe.Account import *

budget = Budget(2020)
budget.addBank("FooBank")
budget.payOff("Bar", amount=100, time=3, start=2, bank="FooBank")
```

#### Negative balance protection

You can ask the application to determine what transactions to add in order to prevent landing in a balance of zero in the entire budget:

```python
from BudgetMe.Account import *

budget = Budget(2020)
budget.addBank("FooBank")
budget.addAccount("Starting Balance", days=[100], category="Credit Card", bank="FooBank", frequency=12, start=1)
budget.addAccount("Foo", days=[-20], category="Credit Card", bank="FooBank")
budget.detectNegativeBalance()
{'month': 6, 'balance': -20.0}
budget.preventNegativeBalance()
budget.detectNegativeBalance()
{'month': 0, 'balance': 0}
```

#### Account conciliation

If you need to adjust the amount of a transaction, lets say you ballpark the value in the budget and the actual value is different for a specific month or months:

```python
from BudgetMe.Account import *

budget = Budget(2020)
budget.addBank("FooBank")
budget.addAccount("Starting Balance", days=[100], category="Credit Card", bank="FooBank", frequency=12, start=1)
budget.addAccount("Foo", days=[-20], category="Credit Card", bank="FooBank")
budget.updateTransaction("Foo",month=3,day=1,amount=-15) # day is the ordinal of the day (1,2...)
```

#### Potential savings

BaC can tell you how much potentially you can save, checkig the "Optional" mode in the Accounts transactions:

```python
from BudgetMe.Account import *

budget = Budget(2020)
budget.addBank("FooBank")
budget.addBank("Bar")
budget.addAccount("Required 1", days=[-10], category="Credit Card", bank="FooBank", txn_mode="Required")
budget.addAccount("Optional 1", days=[-10], category="Credit Card", bank="FooBank", txn_mode="Optional")
budget.addAccount("Optional 2", days=[-10], category="Credit Card", bank="FooBank", txn_mode="Optional")
budget.calcualtePotentialSavings()
240
```

### Serialization

BaC allows serialization and deserialization. This means that the objects can become JSON and JSON can be converted back to objects:

```python
from BudgetMe.Account import *
# Convert a json into an Object
budget_json = {'year': 2021, 'daysof':'dayso ... '}
budget = Budget.createBudgetFromJson(budget_json)
```

```python
from BudgetMe.Account import *
# Create a JSON representation of an object
budget = Budget(2021)
budget.asdict()
{'year': 2021, 'daysof':'dayso ... '}
```

### Plug-Ins

Writing plug-ins is pretty simple. Just inherit the Budget class and create the needed methods to extend the main class:

```python
from BudgetMe.Budget import Budget

class BudgetExtendedSample(Budget):

    def __init__(self, year, daysof=1, start=1, end=12):
        super(BudgetExtendedSample, self).__init__(year, daysof, start, end)

    def calculateMonthsOfBudget(self) -> int:
        return self.end - self.start
```

### Flask Implementation

You can create your budget as a class with a static method to use it in your Flask implementation:

Your budget class:

```python
from BudgetMe.Budget import Budget

class B2022():

    @staticmethod
    def run() -> Budget:
        budget = Budget(2022, daysof=2, start=10, end=12)
        budget.addBank("Checking")
        budget.days_labels = ["H1 (1)", "H2 (15)"]
        budget.addAccount("Adjustments", days=[100, 0], category="Banking", bank="Checking", start=10)
        budget.updateAccountsBalances()
        return budget
```

The implementation in Flask:

```python
from flask import Flask
from flask import render_template
from BudgetMe.B2022 import B2022

app = Flask(__name__)
budget = B2022.run()

@app.route('/balance')
def balance_page():
    return render_template('budget.html', balance=budget.getFinalBalance())
```

### Unit Testing

To run the tests and check the stability of the code, just run:

```shell script
python -m unittest tests/unit_tests.py
```