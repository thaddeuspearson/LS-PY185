import os
from functools import wraps
from secrets import token_hex
from flask import (
    flash,
    Flask,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.exceptions import NotFound
from todos.utils import (
    error_for_list_title,
    error_for_todo,
    is_list_completed,
    is_todo_completed,
    sort_items,
)
from todos.database_persistence import DatabasePersistence

app = Flask(__name__)
app.secret_key = token_hex(32)

storage = DatabasePersistence()


def require_list(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        list_id = kwargs.get("list_id")
        lst = g.storage.find_list(list_id)

        if not lst:
            raise NotFound(description="List not Found")
        return f(lst=lst, *args, **kwargs)
    return decorated_function


@app.context_processor
def list_utilities_processor():
    return {
        "is_list_completed": is_list_completed,
    }


@app.before_request
def load_data():
    g.storage = storage


@app.route("/")
def index():
    return redirect(url_for("get_lists"))


@app.route("/lists/new")
def add_todo_list():
    return render_template('new_list.html')


@app.route("/lists", methods=["GET"])
def get_lists():
    lists = sort_items(g.storage.all_lists(), is_list_completed)
    return render_template('lists.html', lists=lists)


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


@app.route("/lists/<int:list_id>", methods=["POST"])
@require_list
def update_list(lst, list_id):
    new_title = request.form["list_title"].strip()
    error = error_for_list_title(new_title, g.storage.all_lists())
    if error:
        flash(error, "error")
        return render_template("/edit_list.html", lst=lst,
                               list_id=list_id, title=new_title)
    g.storage.update_list(list_id, new_title)
    flash('The list title has been updated', "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<int:list_id>/delete", methods=["POST"])
@require_list
def delete_list(lst, list_id):
    title = lst["title"]
    g.storage.delete_list(list_id)
    flash(f"The list: '{title}' has been deleted", "success")
    return redirect(url_for("get_lists"))


@app.route("/lists/<int:list_id>", methods=["GET"])
@require_list
def display_list(lst, list_id):
    todos = g.storage.find_todos_for_list(lst['id'])
    lst["todos"] = sort_items(todos, is_todo_completed)
    return render_template("list.html", lst=lst, list_id=list_id)


@app.route("/lists/<int:list_id>/edit", methods=["GET"])
@require_list
def edit_list(lst, list_id):
    return render_template("edit_list.html", lst=lst, list_id=list_id)


@app.route("/lists/<int:list_id>/todos", methods=["POST"])
@require_list
def create_todo(lst, list_id):
    todo_title = request.form["todo"].strip()
    error = error_for_todo(todo_title)
    if error:
        flash(error, "error")
        return render_template("/list.html", lst=lst, list_id=list_id)
    g.storage.create_todo(todo_title, list_id)
    flash("The todo has been created.", "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<int:list_id>/todos/<int:todo_id>/toggle", methods=["POST"])
def update_todo_status(list_id, todo_id):
    is_completed = request.form["completed"] == "True"
    g.storage.update_todo_status(todo_id, list_id, is_completed)
    flash("The todo has been updated.", "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<int:list_id>/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(list_id, todo_id):
    g.storage.delete_todo(todo_id, list_id)
    flash("The todo has been deleted.", "success")
    return redirect(url_for("display_list", list_id=list_id))


@app.route("/lists/<int:list_id>/complete_all", methods=["POST"])
@require_list
def complete_all_todos(lst, list_id):
    g.storage.mark_all_todos_completed(list_id)
    flash("The todos have been updated.", "success")
    return redirect(url_for("display_list", list_id=list_id))


if __name__ == "__main__":
    if os.environ.get("FLASK_ENV") == "production":
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)
