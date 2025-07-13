"""
Custom classes for expense program
"""
import sys
from datetime import date
from textwrap import dedent
from contextlib import contextmanager
from psycopg2 import (
    connect, DataError, IntegrityError,
    InterfaceError, OperationalError,
    ProgrammingError
)
from psycopg2.extras import DictCursor


class DbConnection:
    """
    A connection object to the given database
    """
    def __init__(self, dbname):
        self.dbname = dbname

    @contextmanager
    def _database_connect(self):
        """
        Creates a connection context manager for the given database
        """
        connection = None
        try:
            connection = connect(dbname=self.dbname)
            connection.autocommit = True
            with connection:
                yield connection
        except OperationalError:
            print(f"Unable to get a connection to: {self.dbname}. Exiting.")
            sys.exit(1)
        finally:
            if connection:
                connection.close()

    @contextmanager
    def _database_cursor(self):
        """
        Creates a cursor context manager for the given database
        """
        try:
            with self._database_connect() as connection:
                with connection.cursor(cursor_factory=DictCursor) as cursor:
                    yield cursor
        except InterfaceError as e:
            print(e)
            sys.exit(1)

    def execute_query(self, query, *query_args):
        """
        Attempts to execute the given SQL query using the given cursor and
        returns rows if applicable
        """
        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, query_args)
                return cursor.fetchall() if cursor.description else None
        except (
            DataError, IntegrityError, OperationalError, ProgrammingError
        ) as e:
            print(e)
            sys.exit(1)


class ExpenseData:
    """
    Enables CRUD on the given DbConnection
    """
    def __init__(self, dbname):
        self.db_connection = DbConnection(dbname)

    @staticmethod
    def display_expenses(expenses):
        """
        Prints all returned rows with columns delimited by '|'
        """
        for expense in expenses:
            print(
                f"{expense['id']} | {expense['created_on']} | "
                f"{expense['amount']:>12} | {expense['memo']}"
            )

    def add_expense(self, args: list):
        """
        Inserts a new expense to the connected database
        :param args (list): cmdline args
        """
        if len(args) < 2:
            print("You must provide an amount and memo")
            sys.exit(1)

        try:
            amount = round(float(args[0]), 2)
        except ValueError:
            print("The amount must be a number")
            sys.exit(1)

        memo = args[1]
        created_on = date.today()

        query = dedent("""
            INSERT INTO expenses (amount, memo, created_on)
            VALUES (%s, %s, %s)
        """)

        self.db_connection.execute_query(query, amount, memo, created_on)

    def list_expenses(self):
        """
        Prints all expenses in a '|' delimited table
        """
        query = dedent("""
            SELECT * FROM expenses
        """)

        expenses = self.db_connection.execute_query(query)
        if expenses:
            ExpenseData.display_expenses(expenses)

    def search_expenses(self, search_term: str):
        """
        Prints all expenses with memos that contain the given search_term
        :param search_term (str): the term to filter for in the db query
        """
        query = dedent("""
            SELECT * FROM expenses WHERE memo ILIKE (%s)
        """)
        print(search_term)
        if not search_term:
            print("You must provide a search term. Exiting.")
            sys.exit(1)

        expenses = self.db_connection.execute_query(query, f"%{search_term}%")
        if expenses:
            ExpenseData.display_expenses(expenses)


class CLI:
    """
    Driver class for the expense program
    """
    def __init__(self, dbname: str):
        self.expense_data = ExpenseData(dbname)

    @classmethod
    def display_help(cls):
        """
        Prints a help menu for the expense program
        """
        print(dedent("""
            An expense recording system

            Commands:

            add AMOUNT MEMO - record a new expense
            clear - delete all expenses
            list - list all expenses
            delete NUMBER - remove expense with id NUMBER
            search QUERY - list expenses with a matching memo field
        """))

    def run(self, args: list):
        """
        Retrieves and Processes cmdline arguments for the expense program
        :param args (list): cmdline args
        """
        cmd, args = (args[0], args[1:]) if args else (None, None)

        if cmd:
            match cmd.lower():
                case "add":
                    self.expense_data.add_expense(args)
                case "list":
                    self.expense_data.list_expenses()
                case "search":
                    self.expense_data.search_expenses(' '.join(args))
        else:
            self.display_help()
