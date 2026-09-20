from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("todo.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        task = request.form["task"]

        conn = get_db()

        conn.execute(
            "INSERT INTO tasks (name) VALUES (?)",
            (task,)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    conn = get_db()

    tasks = conn.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    conn.close()

    incomplete_count = sum(
        1 for task in tasks
        if task["completed"] == 0
    )

    complete_count = sum(
        1 for task in tasks
        if task["completed"] == 1
    )

    return render_template(
        "index.html",
        tasks=tasks,
        incomplete_count=incomplete_count,
        complete_count=complete_count
    )


@app.route("/complete/<int:id>")
def complete(id):

    conn = get_db()

    task = conn.execute(
        "SELECT completed FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    new_status = 0 if task["completed"] else 1

    conn.execute(
        "UPDATE tasks SET completed = ? WHERE id = ?",
        (new_status, id)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = get_db()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        new_name = request.form["task"]

        conn.execute(
            "UPDATE tasks SET name = ? WHERE id = ?",
            (new_name, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()

    return render_template(
        "edit.html",
        task=task
    )

@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")

init_db()


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)