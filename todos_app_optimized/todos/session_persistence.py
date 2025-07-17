"""Custom Classes for the Todo App"""


class SessionPersistence:
    """Handles the session persistence for todo app"""
    def __init__(self, session) -> None:
        self.session = session
        if 'lists' not in self.session:
            self.session['lists'] = []

    def all_lists(self):
        """Gets all lists iin the ciurrent session"""
        return self.session['lists']

    def find_list(self, todo_lst_id: str) -> dict | None:
        """finds and returns the list associated with the given id or None"""
        return next(
            (lst for lst in self.session['lists'] if lst['id'] == todo_lst_id),
            None
        )
