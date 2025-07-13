"""
Custom classes for expense program
"""
import sys
from datetime import date
from textwrap import dedent
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
        self.connection = self.get_connection()

    def __del__(self):
        self.close()

    def close(self):
        self.connection.close()

    def get_connection(self):
        """
        Gets a connection to the given database
        """
        try:
            connection = connect(dbname=self.dbname)
            connection.autocommit = True
            return connection
        except OperationalError:
            print(f"Unable to get a connection to: {self.dbname}. Exiting.")
            sys.exit(1)

    def execute_query(self, query, *query_args):
        """
        Attempts to execute the given SQL query using the given cursor and
        returns rows if applicable
        """
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, query_args)
                return cursor.fetchall() if cursor.description else None
        except (
            DataError, IntegrityError, InterfaceError,
            OperationalError, ProgrammingError
        ) as e:
            print(e)
            sys.exit(1)


class ExpenseData:
    """
    Enables CRUD on the given DbConnection
    """
    def __init__(self, dbname):
        self.db_connection = DbConnection(dbname)

    def add_expenses(self, args):
        """
        Inserts a new expense to the connected database
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
        query = "SELECT * FROM expenses"
        expenses = self.db_connection.execute_query(query)
        if expenses:
            for expense in expenses:
                print(
                    f"{expense['id']} | {expense['created_on']} | "
                    f"{expense['amount']:>12} | {expense['memo']}"
                )


class CLI:
    """
    Driver class for the expense program
    """
    def __init__(self, dbname):
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

    def run(self):
        """
        Retrieves and Processes cmdline arguments for the expense program
        """
        try:
            cmd = sys.argv[1] if len(sys.argv) > 1 else None
            args = sys.argv[2:]

            if cmd:
                match cmd.lower():
                    case "add":
                        self.expense_data.add_expenses(args)
                    case "list":
                        self.expense_data.list_expenses()
            else:
                self.display_help()
        finally:
            self.expense_data.db_connection.close()
