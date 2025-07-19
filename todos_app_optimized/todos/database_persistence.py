"""Custom DatabasePersistence class for the Todo App"""


class DatabasePersistence:
    """Handles database persistence for todo app"""
    def __init__(self, session) -> None:
        pass

    def all_lists(self):
        """Gets all lists iin the current session"""
        pass

    def create_list(self, title):
        """Creates a new todo list"""
        pass

    def update_list(self, list_id, title):
        """Updates the given todo list"""
        pass

    def delete_list(self, list_id):
        """Deletes the given todo list"""
        pass

    def find_list(self, todo_lst_id: str) -> dict | None:
        """finds and returns the list associated with the given id or None"""
        pass

    def create_todo(self, todo_list, todo_title):
        """Creates a todo in the given todo_list"""
        pass

    def delete_todo(self, todo_list, todo_id):
        """Deletes the todo with the given todo_id from the given todo_list"""
        pass

    def update_todo_status(self, todo, is_completed):
        """Sets the given todo's completed status to True"""
        pass

    def mark_all_todos_completed(self, todo_list):
        """Sets all todos completed status to True"""
        pass
