"""Custom Classes for the Todo App"""
from uuid import uuid4


class SessionPersistence:
    """Handles the session persistence for todo app"""
    def __init__(self, session) -> None:
        self.session = session
        if 'lists' not in self.session:
            self.session['lists'] = []

    def all_lists(self) -> list:
        """Gets all lists in the current session"""
        return self.session['lists']

    def create_list(self, title: str) -> None:
        """Creates a new todo list"""
        self.all_lists().append({
            "id": str(uuid4()),
            "title": title,
            "todos": []
        })
        self.session.modified = True

    def update_list(self, list_id: int, title: str) -> None:
        """Updates the given todo list"""
        lst = self.find_list(list_id)
        if lst:
            lst["title"] = title
        self.session.modified = True

    def delete_list(self, list_id: int) -> None:
        """Deletes the given todo list"""
        self.session["lists"] = [
            lst for lst in self.session["lists"]
            if lst["id"] != list_id
        ]
        self.session.modified = True

    def find_list(self, todo_lst_id: str) -> dict | None:
        """finds and returns the list associated with the given id or None"""
        return next(
            (lst for lst in self.session['lists'] if lst['id'] == todo_lst_id),
            None
        )

    def create_todo(self, todo_list: list, todo_title: str) -> None:
        """Creates a todo in the given todo_list"""
        todo_list["todos"].append({
            "id": str(uuid4()),
            "title": todo_title,
            "completed": False
        })
        self.session.modified = True

    def delete_todo(self, todo_list: list, todo_id: int) -> None:
        """Deletes the todo with the given todo_id from the given todo_list"""
        todo_list["todos"] = [
            todo for todo in todo_list["todos"]
            if todo["id"] != todo_id
        ]
        self.session.modified = True

    def update_todo_status(self, todo: dict, is_completed: bool) -> None:
        """Sets the given todo's completed status to True"""
        todo["completed"] = is_completed
        self.session.modified = True

    def mark_all_todos_completed(self, todo_list: list) -> None:
        """Sets all todos completed status to True"""
        for todo in todo_list["todos"]:
            todo["completed"] = True
        self.session.modified = True
