import os
from typing import Dict, List, Tuple

import sqlite3

conn = sqlite3.connect(os.path.join('db', 'finance.db'))
cursor = conn.cursor()


# Inserting of the new expense into DB
def insert(table: str, column_values: Dict) -> object:
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f'INSERT INTO {table} '
        f'({columns}) '
        f'VALUES ({placeholders})',
        values)
    conn.commit()


# Inserting of the incomes to the database and summarize it with the previous incomes
def update(table: str, column_values: Dict) -> object:
    values = int(column_values['income'])
    print(type(values))
    income = cursor.execute(f'SELECT income from {table} WHERE codename = "base"').fetchone()[0]
    if income:
        values += int(income)
    cursor.execute(f'UPDATE {table} SET income = {values} WHERE codename = "base"')
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id = {row_id}")
    conn.commit()


def get_cursor():
    return cursor


# DB Initialization
def _init_db():
    with open("createdb.sql", "r", encoding='utf-8') as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


# Check if DB initialized, and initialize it if no
def check_db_exists():
    cursor.execute('SELECT name FROM main.sqlite_master '
                   'WHERE type=\'table\' AND name=\'expense\'')
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()