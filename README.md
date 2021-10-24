# BaC 
## Budget As Code
Easy personal budget management in Python.

Author: Mauricio Giraldo <mgiraldo@gmail.com>

### Installations

First, run the dependencies installation:

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

If your accounts gets billed in a frequency different that monthly, and starts in a month different that 1 (January), you can specify the frequency:

```python
budget.addAccount("Water bill", days=[-200, 0], category="Utilities", frequency=3, start=2, bank="Checking")
```

This means that you pay the water bill each 3 months, the first half of the month, starting in the month 2 (February).

If you have a transaction that only happens once a year, you can use:

```python
budget.addSingleAccount("Tax", month=3, days=[1000, 0], category="Taxes", bank="Checking")
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
budget = Budget(2020)
budget.addBank("FooBank")
budget.addAccount("Starting Balance", days=[100], category="Credit Card", bank="FooBank", frequency=12, start=1)
budget.addAccount("Foo", days=[-20], category="Credit Card", bank="FooBank")
budget.updateTransaction("Foo",month=3,day=1,amount=-15) # day is the ordinal of the day (1,2...)
```


### Unit Testing

To run the tests and check the stability of the code, just run:

```shell script
python -m unittest tests/unit_tests.py
```