from flask import Flask
from flask import render_template
from BudgetMe.B2022 import B2022

app = Flask(__name__)
budget = B2022.run()

@app.route('/')
@app.route('/budget/')
def budgetPage():
    months = []
    monthly_balance = []
    monthly_day_balance = []
    for month in range(budget.start, budget.end + 1):
        months.append(str(budget.getMonthName(month)))
        monthly_balance.append(round(budget.getMonthBalance(month), 2))
        for day in range(1, budget.daysof + 1):
            monthly_day_balance.append(round(budget.getMonthDayBalance(month, day), 2))
    return render_template('budget.html', budget=budget.asdict(), months=months, monthly_balance=monthly_balance,
                           monthly_day_balance=monthly_day_balance)

@app.route('/categories/')
def categoriesPage():
    categories = budget.getBalanceByCategories()
    cats = []
    for k, v in categories.items():
        cats.append({"name": k, "value": round(v,2)})
    return render_template('categories.html', categories=cats)

@app.route('/savings/')
def savingsPage():
    savings = budget.calcualtePotentialSavings()
    return render_template('savings.html', savings=savings)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
