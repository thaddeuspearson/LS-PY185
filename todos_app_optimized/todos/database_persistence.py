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
        self._setup_schema()

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

    def _execute_query(self, query: str, params: tuple = (),
                       **kwargs) -> list[dict] | dict | None:
        """Executes the given query with given params on the connected DB."""

        logger.info("Executing query %s with params %s", query, params)

        fetchall = kwargs.get("fetchall", False)
        fetchone = kwargs.get("fetchone", False)

        if fetchall and fetchone:
            raise ValueError(
                "Cannot use both 'fetchall' and 'fetchone' in the same call."
            )

        try:
            with self._database_cursor() as cursor:
                cursor.execute(query, params)

                if fetchall:
                    return cursor.fetchall()
                if fetchone:
                    return cursor.fetchone()

        except DatabaseError as e:
            logger.exception(e)

        if fetchall or fetchone:
            return []
        return None

    def _setup_schema(self):
        """Creates the database schema if the tables do not exist"""

        query = dedent("""
            CREATE TABLE IF NOT EXISTS lists (
                id serial PRIMARY KEY,
                title text NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS todos (
                id serial PRIMARY KEY,
                title text NOT NULL,
                completed boolean NOT NULL DEFAULT false,
                list_id integer NOT NULL
                    REFERENCES lists (id)
                    ON DELETE CASCADE
            );
        """)
        self._execute_query(query, params=())

    def all_lists(self) -> list[dict]:
        """Gets all lists in the current session."""

        query = dedent("""
            SELECT * FROM lists
        """)

        results = self._execute_query(query, fetchall=True)
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
        self._execute_query(query, (title,))

    def update_list(self, list_id: int, new_title: str) -> None:
        """Updates the given todo list."""

        query = dedent("""
            UPDATE lists SET title = %s WHERE id = %s
        """)
        self._execute_query(query, (new_title, list_id))

    def delete_list(self, list_id: int) -> None:
        """Deletes the given todo list."""

        query = dedent("""
            DELETE from lists WHERE id = %s
        """)
        self._execute_query(query, (list_id,))

    def _find_todos_for_list(self, todo_list_id: int) -> list[dict]:
        """Finds all todos associated with the given todo_list_id."""

        query = dedent("""
            SELECT * FROM todos WHERE list_id = %s
        """)
        todos = self._execute_query(query, (todo_list_id,), fetchall=True)
        return [dict(todo) for todo in todos]

    def find_list(self, todo_list_id: int) -> dict | None:
        """Finds and returns the list associated with the given id or None."""

        query = dedent("""
            SELECT * FROM lists WHERE id = %s
        """)
        result = self._execute_query(query, (todo_list_id,), fetchone=True)
        if result is None:
            return None
        lst = dict(result)
        lst["todos"] = self._find_todos_for_list(todo_list_id)
        return lst

    def create_todo(self, todo_title: str, todo_list_id: int) -> None:
        """Creates a todo in the given todo_list."""

        query = dedent("""
            INSERT INTO todos (title, list_id) VALUES (%s, %s)
        """)
        self._execute_query(query, (todo_title, todo_list_id))

    def delete_todo(self, todo_id: int, todo_list_id: int) -> None:
        """Deletes the todo with the given todo_id from the given todo_list."""

        query = dedent("""
            DELETE FROM todos WHERE id = %s and list_id = %s
        """)
        self._execute_query(query, (todo_id, todo_list_id))

    def update_todo_status(self, todo_id: int, todo_list_id: int,
                           is_completed: bool) -> None:
        """Sets the given todo's completed status to True."""

        query = dedent("""
            UPDATE todos SET completed = %s
            WHERE id = %s AND list_id = %s
        """)
        self._execute_query(query, (is_completed, todo_id, todo_list_id))

    def mark_all_todos_completed(self, todo_list_id: int) -> None:
        """Sets all todos completed status to True."""

        query = dedent("""
            UPDATE todos SET completed = True WHERE list_id = %s
        """)
        self._execute_query(query, (todo_list_id,))
