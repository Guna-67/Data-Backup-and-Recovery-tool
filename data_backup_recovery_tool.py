from flask import Flask, render_template_string
import os
import shutil
from datetime import datetime

app = Flask(__name__)

DATA_FOLDER = "data"
BACKUP_FOLDER = "backups"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Data Backup & Recovery Tool</title>
    <style>
        body { font-family: Arial; background: #f4f6f8; margin: 0; }
        .container { width: 90%; max-width: 900px; margin: 40px auto; }
        h1 { text-align: center; }
        .card { background: white; padding: 25px; margin: 20px 0;
                border-radius: 12px; box-shadow: 0 3px 10px #ccc; }
        button { padding: 10px 16px; border: none; border-radius: 6px;
                 color: white; cursor: pointer; }
        .backup { background: #28a745; }
        .restore { background: #007bff; }
        .delete { background: #dc3545; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }
        .status { background: #e8f5e9; padding: 12px; margin-bottom: 15px; border-radius: 6px; }
        form { display: inline; }
    </style>
</head>
<body>
<div class="container">
    <h1>📦 Data Backup & Recovery Tool</h1>

    {% if message %}
        <div class="status">{{ message }}</div>
    {% endif %}

    <div class="card">
        <h2>Create Backup</h2>
        <p>Backup all files from the <b>data</b> folder.</p>
        <form action="/backup" method="POST">
            <button class="backup">Create Backup</button>
        </form>
    </div>

    <div class="card">
        <h2>Available Backups</h2>
        {% if backups %}
        <table>
            <tr><th>Backup</th><th>Created</th><th>Actions</th></tr>
            {% for backup in backups %}
            <tr>
                <td>{{ backup.name }}</td>
                <td>{{ backup.date }}</td>
                <td>
                    <form action="/restore/{{ backup.name }}" method="POST">
                        <button class="restore">Restore</button>
                    </form>
                    <form action="/delete/{{ backup.name }}" method="POST">
                        <button class="delete">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
            <p>No backups available.</p>
        {% endif %}
    </div>
</div>
</body>
</html>
"""

def get_backups():
    backups = []
    for name in os.listdir(BACKUP_FOLDER):
        path = os.path.join(BACKUP_FOLDER, name)
        if os.path.isdir(path):
            date = datetime.fromtimestamp(
                os.path.getctime(path)
            ).strftime("%d-%m-%Y %H:%M:%S")
            backups.append({"name": name, "date": date})
    backups.sort(key=lambda x: x["name"], reverse=True)
    return backups

def page(message=None):
    return render_template_string(
        HTML,
        backups=get_backups(),
        message=message
    )

@app.route("/")
def home():
    return page()

@app.route("/backup", methods=["POST"])
def create_backup():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_name = "backup_" + timestamp
        destination = os.path.join(BACKUP_FOLDER, backup_name)
        shutil.copytree(DATA_FOLDER, destination)
        return page("Backup created successfully!")
    except Exception as e:
        return page("Backup failed: " + str(e))

@app.route("/restore/<backup_name>", methods=["POST"])
def restore_backup(backup_name):
    backup_path = os.path.join(BACKUP_FOLDER, backup_name)
    try:
        if not os.path.exists(backup_path):
            return page("Backup not found.")
        if os.path.exists(DATA_FOLDER):
            shutil.rmtree(DATA_FOLDER)
        shutil.copytree(backup_path, DATA_FOLDER)
        return page("Backup restored successfully!")
    except Exception as e:
        return page("Restore failed: " + str(e))

@app.route("/delete/<backup_name>", methods=["POST"])
def delete_backup(backup_name):
    backup_path = os.path.join(BACKUP_FOLDER, backup_name)
    try:
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
            return page("Backup deleted successfully.")
        return page("Backup not found.")
    except Exception as e:
        return page("Delete failed: " + str(e))

if __name__ == "__main__":
    print("=" * 50)
    print("DATA BACKUP & RECOVERY TOOL")
    print("=" * 50)
    print("Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)
