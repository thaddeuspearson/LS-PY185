import os
from functools import wraps
from secrets import token_hex
from uuid import uuid4
from flask import (
    flash,
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.exceptions import NotFound
from todos.utils import (
    delete_todo_by_id,
    error_for_list_title,
    error_for_todo,
    find_todo_by_id,
    is_list_completed,
    is_todo_completed,
    mark_all_todos_completed,
    sort_items,
    todos_remaining,
)
from todos.session_persistence import SessionPersistence

app = Flask(__name__)
app.secret_key = token_hex(32)


def require_list(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        list_id = kwargs.get("list_id")
        lst = g.storage.find_list(list_id)

        if not lst:
            raise NotFound(description="List not Found")
        return f(lst=lst, *args, **kwargs)
    return decorated_function


def require_todo(f):
    @wraps(f)
    @require_list
    def decorated_function(lst, *args, **kwargs):
        todo_id = kwargs.get("todo_id")
        todo = find_todo_by_id(todo_id, lst)

        if not todo:
            raise NotFound(description="Todo not found")
        return f(lst=lst, todo=todo, *args, **kwargs)
    return decorated_function


@app.context_processor
def list_utilities_processor():
    return {
        "is_list_completed": is_list_completed,
    }


@app.before_request
def load_storage():
    g.storage = SessionPersistence(session)


@app.route("/")
def index():
    return redirect(url_for("get_lists"))


@app.route("/lists/new")
def add_todo_list():
    return render_template('new_list.html')


@app.route("/lists", methods=["GET"])
def get_lists():
    lists = sort_items(g.storage.all_lists(), is_list_completed)
    return render_template('lists.html', lists=lists,
                           todos_remaining=todos_remaining)


@app.route("/lists", methods=["POST"])
def create_list():
    title = request.form["list_title"].strip()
    error = error_for_list_title(title, g.storage.all_lists())
    if error:
        flash(error, "error")
        return render_template("/new_list.html", title=title)

    g.storage.create_list(title)
    flash("The list has been created.", "success")
    return redirect(url_for("get_lists"))


@app.route("/lists/<list_id>", methods=["POST"])
@require_list
def update_list(lst, list_id):
    title = request.form["list_title"].strip()
    error = error_for_list_title(title, g.storage.all_lists())
    if error:
        flash(error, "error")
        return render_template("/edit_list.html", lst=lst, title=title)
    g.storage.update_list(list_id, title)
    flash('The list title has been updated', "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<list_id>/delete", methods=["POST"])
@require_list
def delete_list(lst, list_id):
    title = lst["title"]
    g.storage.delete_list(list_id)
    flash(f"The list: '{title}' has been deleted", "success")
    return redirect(url_for("get_lists"))


@app.route("/lists/<list_id>/todos", methods=["POST"])
@require_list
def create_todo(lst, list_id):
    todo_title = request.form["todo"].strip()
    error = error_for_todo(todo_title)

    if error:
        flash(error, "error")
        return render_template("/list.html", lst=lst)

    lst["todos"].append({
        "id": str(uuid4()),
        "title": todo_title,
        "completed": False
    })

    session.modified = True
    flash("The todo has been created.", "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<list_id>", methods=["GET"])
@require_list
def display_list(lst, list_id):
    lst["todos"] = sort_items(lst["todos"], is_todo_completed)
    return render_template("list.html", lst=lst)


@app.route("/lists/<list_id>/edit", methods=["GET"])
@require_list
def edit_list(lst, list_id):
    return render_template("edit_list.html", lst=lst)


@app.route("/lists/<list_id>/todos/<todo_id>/toggle", methods=["POST"])
@require_todo
def toggle_todo_complete(lst, todo, list_id, todo_id):
    todo["completed"] = request.form["completed"] == "True"

    session.modified = True
    flash("The todo has been updated.", "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<list_id>/todos/<todo_id>/delete", methods=["POST"])
@require_todo
def delete_todo(lst, todo, list_id, todo_id):
    delete_todo_by_id(todo_id, lst)

    session.modified = True
    flash("The todo has been deleted.", "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<list_id>/complete_all", methods=["POST"])
@require_list
def complete_all_todos(lst, list_id):
    mark_all_todos_completed(lst)

    session.modified = True
    flash("The todos have been updated.", "success")
    return redirect(url_for("display_list", list_id=list_id))


if __name__ == "__main__":
    if os.environ.get("FLASK_ENV") == "production":
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)
