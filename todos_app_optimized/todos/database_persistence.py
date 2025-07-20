"""Custom DatabasePersistence class for the Todo App"""
import sys
from contextlib import contextmanager
from typing import Generator
from psycopg2 import connect, OperationalError
from psycopg2.extras import DictCursor
from psycopg2.extensions import connection as PGConnection


class DatabasePersistence:
    """Handles database persistence for todo app"""
    DBNAME = "todos"

    def __init__(self) -> None:
        """Initiates the DatabasePersistence class"""
        self.dbname = DatabasePersistence.DBNAME

    @contextmanager
    def _database_connect(self) -> Generator[PGConnection, None, None]:
        """Obtains a connection to the indicated PostgreSQL database"""
        connection = None
        try:
            connection = connection = connect(dbname=self.dbname)
            connection.autocommit = True
            with connection:
                yield connection
        except OperationalError:
            print(f"Unable to get a connection to: {self.dbname}. Exiting.")
            sys.exit(1)
        finally:
            if connection:
                connection.close()

    def all_lists(self) -> list:
        """Gets all lists iin the current session"""
        pass

    def create_list(self, title: str) -> None:
        """Creates a new todo list"""
        pass

    def update_list(self, list_id: int, title: str) -> None:
        """Updates the given todo list"""
        pass

    def delete_list(self, list_id: int) -> None:
        """Deletes the given todo list"""
        pass

    def find_list(self, todo_list_id: str) -> dict | None:
        """finds and returns the list associated with the given id or None"""
        pass

    def create_todo(self, todo_list: dict, todo_title: str) -> None:
        """Creates a todo in the given todo_list"""
        pass

    def delete_todo(self, todo_list: list, todo_id: int) -> None:
        """Deletes the todo with the given todo_id from the given todo_list"""
        pass

    def update_todo_status(self, todo: dict, is_completed: bool) -> None:
        """Sets the given todo's completed status to True"""
        pass

    def mark_all_todos_completed(self, todo_list: dict) -> None:
        """Sets all todos completed status to True"""
        pass
