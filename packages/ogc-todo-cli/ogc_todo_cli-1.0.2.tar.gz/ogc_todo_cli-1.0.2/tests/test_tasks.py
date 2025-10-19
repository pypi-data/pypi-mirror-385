import json
from pathlib import Path
import pytest

from todo_cli.models import Task, TaskManager

def test_task_creation():
    """Check that a Task object initializes correctly"""
    task = Task("Study Python", "Education")
    assert task.text == "Study Python"
    assert task.category == "Education"
    assert task.status == "Pending"

def test_add_task_creates_entry(tmp_path, monkeypatch):
    """Ensure TaskManager.add_task() adds a task to the JSON file"""

    test_file = tmp_path / "test_tasks.json"

    from todo_cli import storage
    monkeypatch.setattr(storage, "FILE_NAME", str(test_file))

    # Make sure the temp file does not exist yet (our code should handle that)
    if test_file.exists():
        test_file.unlink()

    manager = TaskManager()
    manager.add_task("Read Book", "Personal")

    # Reload data to verify that one task was written
    data = storage.load()
    assert len(data) == 1
    assert data[0]["Task"] == "Read Book"
    assert data[0]["Category"] == "Personal"
    assert data[0]["Status"] == "Pending"






