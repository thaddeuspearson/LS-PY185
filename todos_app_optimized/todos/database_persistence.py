"""Custom DatabasePersistence class for the Todo App"""


class DatabasePersistence:
    """Handles database persistence for todo app"""
    def __init__(self) -> None:
        pass

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
