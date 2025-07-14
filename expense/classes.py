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
        self._setup_schema()

    def _setup_schema(self):
        """Checks if the expenses table exists and creates it if not"""
        query = dedent("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'expenses';
        """)
        table_exists = self.db_connection.execute_query(query)[0][0]

        if not table_exists:
            query = dedent("""
                CREATE TABLE expenses (
                    id serial PRIMARY KEY,
                    amount numeric(6, 2) NOT NULL CHECK (amount > 0),
                    memo text NOT NULL,
                    created_on date NOT NULL
                )
            """)
            self.db_connection.execute_query(query)
            print("Expenses table created.")

    def _display_count(self, count):
        """
        Prints the count of rows returned from the associated db query
        :param count int: number of returned rows from the associated db query
        """
        print(f"There {'is' if count == 1 else 'are'} {count if count else 'no'} "
              f"expense{'' if count == 1 else 's'}.")

    def _display_total(self, expenses):
        """
        Displays the total price of all expenses returned
        :param count int: number of returned rows from the associated db query
        """
        total = round(sum(expense['amount'] for expense in expenses), 2)
        if len(expenses) > 1:
            print("-" * 50)
            print(f"Total {total:>25}")

    def display_expenses(self, expenses):
        """
        Prints all returned rows with columns delimited by '|'
        :param expenses list<str>: returned rows from the assoiciated db query
        """
        self._display_count(len(expenses))

        if expenses:
            for expense in expenses:
                print(
                    f"  {expense['id']} | {expense['created_on']} | "
                    f"{expense['amount']:>12} | {expense['memo']}"
                )
            self._display_total(expenses)

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

    def delete_expenses(self, expense_ids: list):
        """
        Deletes the expenses associated with the given expense ids
        :param expense_ids (list<str>): the ids of the expense to delete
        """
        if not expense_ids or not expense_ids[0].isnumeric():
            print("You must provide at least 1 expense id. Exiting.")
            sys.exit(1)

        deleted_expenses = []
        invalid_ids = []

        for expense_id in expense_ids:
            query = dedent("""
                SELECT * FROM expenses WHERE id = (%s)
            """)
            expense = self.db_connection.execute_query(query, expense_id)
            if expense:
                query = dedent("""
                    DELETE FROM expenses WHERE id = (%s)
                """)
                self.db_connection.execute_query(query, expense_id)
                deleted_expenses.append(expense)
            else:
                invalid_ids.append(expense_id)

        if deleted_expenses:
            print("The following expense(s) have been deleted:")
            for expense in deleted_expenses:
                self.display_expenses(expense)
            print()
        if invalid_ids:
            print(f"No expense(s) found with id(s): {', '.join(invalid_ids)}.")
            print()

    def delete_all_expenses(self):
        """
        Clears the expenses table after confirmation from the user
        """
        if (input(
            "This will remove all expenses. Are you sure? (enter y to confirm)"
        ).strip()).lower() == "y":
            query = dedent("""
                DELETE FROM expenses
            """)
            self.db_connection.execute_query(query)
            print("All expenses have been deleted.")

    def list_expenses(self):
        """
        Prints all expenses in a '|' delimited table
        """
        query = dedent("""
            SELECT * FROM expenses
        """)

        expenses = self.db_connection.execute_query(query)
        self.display_expenses(expenses)

    def search_expenses(self, search_term: str):
        """
        Prints all expenses with memos that contain the given search_term
        :param search_term (str): the term to filter for in the db query
        """
        if not search_term:
            print("You must provide a search term. Exiting.")
            sys.exit(1)

        query = dedent("""
            SELECT * FROM expenses WHERE memo ILIKE (%s)
        """)

        expenses = self.db_connection.execute_query(query, f"%{search_term}%")
        self.display_expenses(expenses)


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
                case "clear":
                    self.expense_data.delete_all_expenses()
                case "delete":
                    self.expense_data.delete_expenses(args)
                case "list":
                    self.expense_data.list_expenses()
                case "search":
                    self.expense_data.search_expenses(' '.join(args))

        else:
            self.display_help()
