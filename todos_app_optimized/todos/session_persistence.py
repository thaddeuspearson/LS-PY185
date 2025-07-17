"""Custom Classes for the Todo App"""
from uuid import uuid4


class SessionPersistence:
    """Handles the session persistence for todo app"""
    def __init__(self, session) -> None:
        self.session = session
        if 'lists' not in self.session:
            self.session['lists'] = []

    def all_lists(self):
        """Gets all lists iin the ciurrent session"""
        return self.session['lists']

    def create_list(self, title):
        self.all_lists().append({
            "id": str(uuid4()),
            "title": title,
            "todos": []
        })
        self.session.modified = True

    def update_list(self, list_id, title):
        lst = self.find_list(list_id)
        if lst:
            lst["title"] = title
        self.session.modified = True

    def delete_list(self, list_id):
        self.session["lists"] = [
            lst for lst in self.session["lists"]
            if lst.id != list_id
        ]
        self.session.modified = True

    def find_list(self, todo_lst_id: str) -> dict | None:
        """finds and returns the list associated with the given id or None"""
        return next(
            (lst for lst in self.session['lists'] if lst['id'] == todo_lst_id),
            None
        )
