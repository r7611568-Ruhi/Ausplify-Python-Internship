
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path
from datetime import date, datetime

app = Flask(__name__)
DATABASE = Path(__file__).resolve().parent / "tasks.db"


def now():
    return datetime.now().isoformat(timespec="seconds")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT DEFAULT 'Pending',
                priority TEXT DEFAULT 'Medium',
                due_date TEXT DEFAULT '',
                created_at TEXT DEFAULT '',
                started_at TEXT DEFAULT '',
                completed_at TEXT DEFAULT ''
            )
        """)

        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(tasks)")
        }

        for column, definition in {
            "created_at": "TEXT DEFAULT ''",
            "started_at": "TEXT DEFAULT ''",
            "completed_at": "TEXT DEFAULT ''"
        }.items():
            if column not in columns:
                conn.execute(
                    f"ALTER TABLE tasks ADD COLUMN {column} {definition}"
                )


def prepare_task(task):
    item = dict(task)
    today = date.today()
    item["overdue"] = False
    item["deadline_message"] = ""
    item["days_left"] = None
    item["duration"] = ""

    if item["due_date"] and item["status"] != "Completed":
        try:
            due = date.fromisoformat(item["due_date"])
            difference = (due - today).days
            item["days_left"] = difference

            if difference < 0:
                item["overdue"] = True
                item["deadline_message"] = (
                    f"Task is {abs(difference)} day(s) overdue!"
                )
            elif difference == 0:
                item["deadline_message"] = "Task is due today!"
            elif difference == 1:
                item["deadline_message"] = "Only 1 day left!"
            elif difference == 2:
                item["deadline_message"] = "Only 2 days left!"
            elif difference <= 7:
                item["deadline_message"] = f"{difference} days left."
        except ValueError:
            pass

    if item["started_at"]:
        try:
            start = datetime.fromisoformat(item["started_at"])
            end = (
                datetime.fromisoformat(item["completed_at"])
                if item["completed_at"]
                else datetime.now()
            )
            seconds = max(0, int((end - start).total_seconds()))
            hours, remainder = divmod(seconds, 3600)
            minutes = remainder // 60
            item["duration"] = f"{hours}h {minutes}m"
        except ValueError:
            pass

    return item


@app.route("/")
def home():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "All")

    with get_db() as conn:
        query = "SELECT * FROM tasks WHERE title LIKE ?"
        params = [f"%{search}%"]

        if status_filter in ["Pending", "Ongoing", "Completed"]:
            query += " AND status = ?"
            params.append(status_filter)

        query += """
            ORDER BY
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                ELSE 3
            END,
            CASE WHEN due_date = '' THEN 1 ELSE 0 END,
            due_date ASC,
            id DESC
        """

        tasks = [
            prepare_task(row)
            for row in conn.execute(query, params).fetchall()
        ]

        statistics = conn.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN status = 'Ongoing' THEN 1 ELSE 0 END) AS ongoing,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed
            FROM tasks
        """).fetchone()

    reminders = [
        task for task in tasks
        if task["deadline_message"] and not task["overdue"]
    ]
    overdue_tasks = [task for task in tasks if task["overdue"]]

    reminder_items = [
        {
            "title": task["title"],
            "deadline_message": task["deadline_message"],
            "overdue": task["overdue"]
        }
        for task in overdue_tasks + reminders
    ]

    return render_template(
        "index.html",
        tasks=tasks,
        statistics=statistics,
        search=search,
        status_filter=status_filter,
        reminders=reminders,
        overdue_tasks=overdue_tasks,
        reminder_items=reminder_items,
        overdue_count=len(overdue_tasks)
    )


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")

    if not title or len(title) > 200:
        return redirect(url_for("home"))

    if priority not in ["High", "Medium", "Low"]:
        priority = "Medium"

    try:
        if due_date:
            date.fromisoformat(due_date)
    except ValueError:
        due_date = ""

    with get_db() as conn:
        conn.execute("""
            INSERT INTO tasks
            (title, description, priority, due_date, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, priority, due_date, now()))

    return redirect(url_for("home"))


@app.route("/status/<int:task_id>", methods=["POST"])
def update_status(task_id):
    status = request.form.get("status")

    if status not in ["Pending", "Ongoing", "Completed"]:
        return redirect(url_for("home"))

    with get_db() as conn:
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if task:
            started_at = task["started_at"] or ""
            completed_at = ""

            if status == "Ongoing" and not started_at:
                started_at = now()

            if status == "Completed":
                if not started_at:
                    started_at = now()
                completed_at = now()

            conn.execute("""
                UPDATE tasks
                SET status = ?, started_at = ?, completed_at = ?
                WHERE id = ?
            """, (status, started_at, completed_at, task_id))

    return redirect(url_for("home"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    with get_db() as conn:
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if task is None:
            return redirect(url_for("home"))

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            priority = request.form.get("priority", "Medium")
            due_date = request.form.get("due_date", "")

            try:
                if due_date:
                    date.fromisoformat(due_date)
            except ValueError:
                due_date = ""

            if title and len(title) <= 200 and priority in [
                "High", "Medium", "Low"
            ]:
                conn.execute("""
                    UPDATE tasks
                    SET title = ?, description = ?,
                        priority = ?, due_date = ?
                    WHERE id = ?
                """, (title, description, priority, due_date, task_id))

            return redirect(url_for("home"))

    return render_template("edit.html", task=task)


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    with get_db() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return redirect(url_for("home"))


initialize_database()

if __name__ == "__main__":
    app.run(debug=True)
