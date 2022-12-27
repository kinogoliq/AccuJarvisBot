# Main Server loading file of the AccuJarvis Bot

import logging

from aiogram import Bot, Dispatcher, executor, types

import config
import exceptions
import expenses
from categories import Categories
from middlewares import AccessMiddleware

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp: Dispatcher = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(config.ACCESS_ID))


# Welcome message and bot help
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(
        "Я семейный помощник учёта финансов\n\n"
        "<b>Для добавления дохода добавь 'зп' после цифр</b>\n\n"
        "Добавить расход в виде: <b>100 кофе</b>\n"
        "Статистика сегодня: /today\n"
        "Статистика за месяц: /month\n"
        "Доходы: /incomes\n"
        "Последние расходы: /expenses\n"
        "Категории расходов: /categories", parse_mode='html')


# Deleting income record per record identifier
@dp.message_handler(lambda message: message.text.startswith('/deli'))
async def del_income(message: types.Message):
    row_id = int((message.text[-1]))
    expenses.delete_income(row_id)
    answer_message = 'Доход удалён!'
    await message.answer(answer_message)


# Deleting record per record identifier
@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    row_id = int(message.text[-1])
    expenses.delete_expense(row_id)
    answer_message = "Расход удалён!"
    await message.answer(answer_message)


# Sending the list of the categories of the expenses
@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    categories = Categories().get_all_categories()
    answer_message = "Категории расходов:\n\n* " + \
                     ("\n* ".join([c.name + ' (' + ", ".join(c.aliases) + ')' for c in categories]))
    await message.answer(answer_message)


# Sending of today's expenses statistics
@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)


# Sending of monthly expenses statistics
@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)


# Sending list of last expenses records
@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    last_expenses = expenses.last()
    print(last_expenses)
    if not last_expenses:
        await message.answer("Пока расходов нет")
        return

    last_expenses_rows = [
        f'{expense.amount} грн на {expense.category_name} — нажми '
        f'/del{expense.id} для удаления'
        for expense in last_expenses]
    answer_message = 'Последние сохраненные расходы:\n\n* ' + '\n\n* ' \
        .join(last_expenses_rows)
    await message.answer(answer_message)


# Sending list of last incomes records
@dp.message_handler(commands=['incomes'])
async def list_incomes(message: types.Message):
    last_income = expenses.last_incomes()
    print(last_income)
    if not last_income:
        await message.answer("Пока доходы не вносили")
        return

    last_incomes_rows = [
        f'{last_income.amount} грн — нажми '
        f'/deli{last_income.id} для удаления'
        for last_income in last_income]
    answer_message = 'Последние сохраненные доходы:\n\n* ' + '\n\n* ' \
        .join(last_incomes_rows)
    await message.answer(answer_message)


#Adding new income or expense to the database
@dp.message_handler()
async def new(message: types.Message):
    try:
        result = expenses._parse_message(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    if isinstance(result, expenses.Income):
        income = expenses.add_income(message.text)
        answer_message = (
            f"Добавлен доход {income.amount} грн \n\n"
            f"{expenses.get_today_incomes()}")
        await message.answer(answer_message)
    elif isinstance(result, expenses.Message):
        expense = expenses.add_expense(message.text)
        answer_message = (
            f"Добавлен расход {expense.amount} грн на {expense.category_name}.\n\n"
            f"{expenses.get_today_statistics()}")
        await message.answer(answer_message)
    else:
        return


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

