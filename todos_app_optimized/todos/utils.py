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


def find_todo_by_id(todo_id: str, todo_list: list) -> dict | None:
    return next(
        (todo for todo in todo_list["todos"] if todo["id"] == todo_id), None
    )


def todos_remaining(todo_lst: dict) -> int:
    return sum(1 for todo in todo_lst["todos"] if not todo["completed"])


def is_list_completed(todo_lst: list) -> bool:
    return len(todo_lst["todos"]) > 0 and todos_remaining(todo_lst) == 0


def is_todo_completed(todo: dict) -> bool:
    return todo["completed"]


def sort_items(items: list, select_completed: Callable) -> list:
    incompleted = []
    completed = []

    for lst in sorted(items, key=lambda item: item["title"].lower()):
        if select_completed(lst):
            completed.append(lst)
        else:
            incompleted.append(lst)

    return incompleted + completed
