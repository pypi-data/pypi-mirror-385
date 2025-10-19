"""Tests for CLI functionality."""
import json
import os
import tempfile
from pathlib import Path

import pytest

from incaricli.cli import (
    add_task,
    delete_task,
    find_task_by_id,
    get_next_id,
    handle_json,
    list_tasks,
    update_status,
    update_task,
)


@pytest.fixture
def temp_db_file(monkeypatch):
    """Create a temporary database file for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "tasks_db.json"
        monkeypatch.setattr("incaricli.cli.DB_FILE", str(db_file))
        yield str(db_file)


def test_handle_json_creates_file(temp_db_file):
    """Test that handle_json creates a new file if it doesn't exist."""
    assert not os.path.exists(temp_db_file)
    result = handle_json()
    assert result == []
    assert os.path.exists(temp_db_file)


def test_get_next_id_empty_list():
    """Test get_next_id with empty list."""
    assert get_next_id([]) == 1


def test_get_next_id_with_tasks():
    """Test get_next_id with existing tasks."""
    tasks = [{"id": 1}, {"id": 2}, {"id": 5}]
    assert get_next_id(tasks) == 6


def test_find_task_by_id_found():
    """Test finding a task by ID."""
    tasks = [{"id": 1, "description": "Task 1"}, {"id": 2, "description": "Task 2"}]
    task, index = find_task_by_id(tasks, 2)
    assert task == {"id": 2, "description": "Task 2"}
    assert index == 1


def test_find_task_by_id_not_found():
    """Test finding a non-existent task."""
    tasks = [{"id": 1, "description": "Task 1"}]
    task, index = find_task_by_id(tasks, 99)
    assert task is None
    assert index is None


def test_add_task(temp_db_file, capsys):
    """Test adding a task."""
    add_task("Test task")

    with open(temp_db_file, "r") as f:
        tasks = json.load(f)

    assert len(tasks) == 1
    assert tasks[0]["description"] == "Test task"
    assert tasks[0]["status"] == "todo"
    assert tasks[0]["id"] == 1

    captured = capsys.readouterr()
    assert "added successfully" in captured.out


def test_add_task_empty_description(temp_db_file, capsys):
    """Test adding a task with empty description."""
    add_task("")

    with open(temp_db_file, "r") as f:
        tasks = json.load(f)

    assert len(tasks) == 0
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_delete_task(temp_db_file, capsys):
    """Test deleting a task."""
    add_task("Test task")
    capsys.readouterr()  # Clear output

    delete_task(1)

    with open(temp_db_file, "r") as f:
        tasks = json.load(f)

    assert len(tasks) == 0
    captured = capsys.readouterr()
    assert "removed successfully" in captured.out


def test_delete_task_not_found(temp_db_file, capsys):
    """Test deleting a non-existent task."""
    delete_task(99)

    captured = capsys.readouterr()
    assert "Error" in captured.out
    assert "not found" in captured.out


def test_update_task(temp_db_file, capsys):
    """Test updating a task."""
    add_task("Original task")
    capsys.readouterr()  # Clear output

    update_task(1, "Updated task")

    with open(temp_db_file, "r") as f:
        tasks = json.load(f)

    assert tasks[0]["description"] == "Updated task"
    captured = capsys.readouterr()
    assert "updated successfully" in captured.out


def test_update_status(temp_db_file, capsys):
    """Test updating task status."""
    add_task("Test task")
    capsys.readouterr()  # Clear output

    update_status(1, "in-progress")

    with open(temp_db_file, "r") as f:
        tasks = json.load(f)

    assert tasks[0]["status"] == "in-progress"
    captured = capsys.readouterr()
    assert "status updated" in captured.out


def test_update_status_invalid(temp_db_file, capsys):
    """Test updating task with invalid status."""
    add_task("Test task")
    capsys.readouterr()  # Clear output

    update_status(1, "invalid-status")

    captured = capsys.readouterr()
    assert "Error" in captured.out
    assert "not valid" in captured.out
