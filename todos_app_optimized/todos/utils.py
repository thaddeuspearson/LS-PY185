from typing import Callable


def error_for_list_title(title: str, lists: list) -> str | None:
    error = None

    if any(lst["title"] == title for lst in lists):
        error = "Title must be unique."
    elif not 1 <= len(title) <= 100:
        error = "Title must be between 1 and 100 characters."

    return error


def error_for_todo(title: str) -> str | None:
    error = None

    if not 1 <= len(title) <= 100:
        error = "Title must be between 1 and 100 characters."

    return error


def find_todo_by_id(todo_id: int, todo_list: list) -> dict | None:
    return next(
        (todo for todo in todo_list if todo["id"] == todo_id), None
    )


def is_list_completed(todo_lst: list) -> bool:
    return todo_lst["todo_count"] > 0 and todo_lst["todos_remaining"] == 0


def is_todo_completed(todo: dict) -> bool:
    return todo["completed"]


def sort_items(todo_lists: list[dict], select_completed: Callable) -> list:
    incompleted = []
    completed = []

    for lst in sorted(todo_lists, key=lambda lst: lst["title"].lower()):
        if select_completed(lst):
            completed.append(lst)
        else:
            incompleted.append(lst)

    return incompleted + completed
