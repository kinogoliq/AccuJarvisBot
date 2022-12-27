# Work with the expenses, adding, deleting, etc
import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
import exceptions
from categories import Categories


# New expense parsing structure
class Message(NamedTuple):
    amount: int
    category_text: str


# New income parsing structure
class Income(NamedTuple):
    id: Optional[int]
    amount: int


# New expenses DB insertion structure
class Expense(NamedTuple):
    id: Optional[int]
    amount: int
    category_name: str


# Adding a new msg. Taking entry of new text msg, coming to Bot
def add_expense(raw_message: str) -> Expense:
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(parsed_message.category_text)
    db.insert("expense", {
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Expense(id=None,
                   amount=parsed_message.amount,
                   category_name=category.name)


# Adding a new Income. Taking entry of new text msg, coming to Bot
def add_income(raw_message: str) -> Income:
    parsed_message = _parse_message(raw_message)
    db.insert("budget", {"income": parsed_message.amount,
                         "created": _get_now_formatted()})
    return Income(id=None, amount=parsed_message.amount)


# Return the stat of today's expenses
def get_today_statistics() -> str:
    cursor = db.get_cursor()
    cursor.execute("select sum(amount) from expense where date(created)=date('now', 'localtime')")
    result = cursor.fetchone()
    if not result[0]:
        return "Пока расходов нет"
    all_today_expenses = result[0]
    cursor.execute("select sum(amount) "
                   "from expense where date(created)=date('now', 'localtime') "
                   "and category_codename in (select codename "
                   "from category where is_base_expense=true)")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0
    return (f"Расходов за сегодня:\n"
            f"Всего: {all_today_expenses} грн\n"
            f"Из них базовых: {base_today_expenses} грн \n\n"
            f"Текущий месяц: /month")


# Return the stat of today's incomes
def get_today_incomes() -> str:
    cursor = db.get_cursor()
    cursor.execute("select income from budget where date(created)=date('now', 'localtime')")
    result = cursor.fetchone()
    if not result[0]:
        return "Сегодня доходов нет"
    cursor.execute("select sum(income) from budget")
    result = cursor.fetchone()
    all_today_incomes = result[0] if result[0] else 0
    return (f"Сегодня доходов: \n"
            f"Всего — {all_today_incomes} грн\n")


# Return the stat of monthly expenses
def get_month_statistics() -> str:
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}'")
    result = cursor.fetchone()
    if not result[0]:
        return "В этом месяце пока расходов нет"
    all_today_expenses = result[0]
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}' "
                   f"and category_codename in (select codename "
                   f"from category where is_base_expense=true)")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0

    cursor.execute(f"select sum(income) from budget")
    result = cursor.fetchone()
    remain_funds = int(result[0] - all_today_expenses)
    print(remain_funds)

    return (f"Расходы в текущем месяце:\n"
            f"всего: {all_today_expenses} грн.\n"
            f"из них базовых: {base_today_expenses} грн.\n"
            f"остаток средств: {remain_funds} грн.")


# Return the stat of last couple expenses
def last() -> List[Expense]:
    cursor = db.get_cursor()
    cursor.execute(
        "select e.id, e.amount, c.name "
        "from expense e left join category c "
        "on c.codename=e.category_codename "
        "order by created desc limit 10")
    rows = cursor.fetchall()
    last_expenses = [Expense(id=row[0], amount=row[1], category_name=row[2]) for row in rows]
    return last_expenses


# Return the stat of last couple incomes
def last_incomes() -> List[Income]:
    cursor = db.get_cursor()
    cursor.execute("select budget.id, income from budget order by created desc limit 20")
    rows = cursor.fetchall()
    last_income = [Income(id=row[0], amount=row[1]) for row in rows]
    print(last_income)
    return last_income


# Delete the expense by its identifier
def delete_expense(row_id: int) -> None:
    db.delete("expense", row_id)


# Delete the income by its identifier
def delete_income(row_idi: int) -> None:
    db.delete("budget", row_idi)


# Parsing of incoming message abt the new expense OR INCOME
def _parse_message(raw_message: str, amount=int, category_name=None, row=None) -> Message:
    if row is None:
        row = [0]
    regexp_result = re.match(r'([\d ]+) (.*)', raw_message)
    print(regexp_result)

    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Напиши сообщение в формате, "
            "например:\n100 еда")
    elif regexp_result.group(2) == 'зп':
        amount = regexp_result.group(1).replace(" ", "")
        income = Income(id=row[0], amount=amount)
        print(income.amount)
        return income
    else:
        amount = regexp_result.group(1).replace(" ", "")
        category_text = regexp_result.group(2).strip().lower()
        return Message(amount=amount, category_text=category_text)


# Return today's date as a string
def _get_now_formatted() -> str:
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


# Return today's date bss timezone (Kyiv)
def _get_now_datetime() -> datetime.datetime:
    tz = pytz.timezone("Europe/Kiev")
    now = datetime.datetime.now(tz)
    return now


# Return daily limit for the base expenses
# def _get_budget_limit() -> int:
#     return db.fetchall("budget", ["daily_limit"])[0]["daily_limit"]
