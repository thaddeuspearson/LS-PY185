"""Custom DatabasePersistence class for the Todo App"""
import sys
from contextlib import contextmanager
from textwrap import dedent
from typing import Generator
import logging
from psycopg2 import connect, DatabaseError, InterfaceError, OperationalError
from psycopg2.extras import DictCursor
from psycopg2.extensions import connection as PGConnection


LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class DatabasePersistence:
    """Handles database persistence for todo app."""
    DBNAME = "todos"

    def __init__(self) -> None:
        """Initiates the DatabasePersistence class."""
        self.dbname = DatabasePersistence.DBNAME

    @contextmanager
    def _database_connect(self) -> Generator[PGConnection, None, None]:
        """Obtains a connection to the indicated PostgreSQL database."""
        connection = None
        try:
            connection = connect(dbname=self.dbname)
            connection.autocommit = True
            with connection:
                yield connection
        except OperationalError:
            logger.exception("Unable to get a connection to: %s. Exiting.",
                             self.dbname)
            sys.exit(1)
        finally:
            if connection:
                connection.close()

    @contextmanager
    def _database_cursor(self) -> Generator[DictCursor, None, None]:
        """Creates a cursor context manager for the given database."""
        try:
            with self._database_connect() as connection:
                with connection.cursor(cursor_factory=DictCursor) as cursor:
                    yield cursor
        except InterfaceError as e:
            logger.exception(e)
            sys.exit(1)

    def all_lists(self) -> list[dict]:
        """Gets all lists in the current session."""

        query = dedent("""
            SELECT * FROM lists
        """)

        logger.info("Executing query: %s", query)

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        except DatabaseError as e:
            logger.exception(e)
            return []

        lists = [dict(row) for row in results]

        for lst in lists:
            todos = self._find_todos_for_list(lst['id'])
            lst.setdefault('todos', todos)

        return lists

    def create_list(self, title: str) -> None:
        """Creates a new todo list."""

        query = dedent("""
            INSERT INTO lists (title) VALUES (%s)
        """)

        logger.info("Executing query: %s with title: %s", query, title)

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, (title,))
        except DatabaseError as e:
            logger.exception(e)

    def update_list(self, list_id: int, new_title: str) -> None:
        """Updates the given todo list."""

        query = dedent("""
            UPDATE lists SET title = %s WHERE id = %s
        """)

        logger.info("Executing query: %s with new title: %s and id: %s",
                    query, new_title, list_id)

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, (new_title, list_id))
        except DatabaseError as e:
            logger.exception(e)

    def delete_list(self, list_id: int) -> None:
        """Deletes the given todo list."""

        query = dedent("""
            DELETE from lists WHERE id = %s
        """)

        logger.info("Executing query: %s with id: %s", query, list_id)

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, (list_id,))
        except DatabaseError as e:
            logger.exception(e)

    def _find_todos_for_list(self, todo_list_id: int) -> list[dict]:
        """Finds all todos associated with the given todo_list_id."""

        query = dedent("""
            SELECT * FROM todos WHERE list_id = %s
        """)

        logger.info("Executing query: %s with list_id %s", query, todo_list_id)

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, (todo_list_id,))
                todos = cursor.fetchall()
        except DatabaseError as e:
            logger.exception(e)
            return []

        todos = [dict(todo) for todo in todos]
        return todos

    def find_list(self, todo_list_id: str) -> dict | None:
        """Finds and returns the list associated with the given id or None."""

        query = dedent("""
            SELECT * FROM lists WHERE id = %s
        """)

        logger.info("Executing query: %s with todo_list_id: %s",
                    query, todo_list_id)

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, (todo_list_id,))
                result = cursor.fetchone()
                if result is None:
                    return None
                lst = dict(result)
        except DatabaseError as e:
            logger.exception(e)
            return None

        todos = self._find_todos_for_list(todo_list_id)
        lst.setdefault('todos', todos)
        return lst

    def create_todo(self, todo_title: str, todo_list_id: int) -> None:
        """Creates a todo in the given todo_list."""

        query = dedent("""
            INSERT INTO todos (title, list_id) VALUES (%s, %s)
        """)

        logger.info(
            "Executing query: %s with todo_title: %s and todo_list_id: %s",
            query, todo_title, todo_list_id
        )

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, (todo_title, todo_list_id))
        except DatabaseError as e:
            logger.exception(e)

    def delete_todo(self, todo_id: int, todo_list_id: list) -> None:
        """Deletes the todo with the given todo_id from the given todo_list."""

        query = dedent("""
                DELETE FROM todos WHERE id = %s and list_id = %s
        """)

        logger.info(
            "Executing query: %s with todo_id: %s and todo_list_id: %s",
            query, todo_id, todo_list_id
        )

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, (todo_id, todo_list_id))
        except DatabaseError as e:
            logger.exception(e)

    def update_todo_status(self, todo_id: int, todo_list_id: int,
                           is_completed: bool) -> None:
        """Sets the given todo's completed status to True."""

        query = dedent("""
                UPDATE todos SET completed = %s
                WHERE id = %s AND list_id = %s
        """)

        logger.info(
            "Executing query: %s with todo_id: %s "
            "and todo_list_id: %s and is_completed = %s",
            query, is_completed, todo_id, todo_list_id
        )

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, (is_completed, todo_id, todo_list_id))
        except DatabaseError as e:
            logger.exception(e)

    def mark_all_todos_completed(self, todo_list: dict) -> None:
        """Sets all todos completed status to True."""
        pass
