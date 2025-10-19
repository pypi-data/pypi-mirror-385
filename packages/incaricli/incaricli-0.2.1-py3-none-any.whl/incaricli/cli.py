import argparse
import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

VALID_STATUSES = ["todo", "in-progress", "done"]
DB_FILE = "tasks_db.json"

console = Console()

task_struct = {
    "id": 0,
    "description": "",
    "status": "",
    "createdAt": "",
    "updatedAt": "",
}


def make_table(title, data):
    if not data:
        console.print(f"[yellow]No tasks found.[/yellow]")
        return

    table = Table(title=title)
    columns = list(data[0].keys())

    for column in columns:
        table.add_column(column, style="cyan")

    for row in data:
        status_color = {"todo": "yellow", "in-progress": "blue", "done": "green"}.get(
            row.get("status", ""), "white"
        )

        table.add_row(*[str(row[column]) for column in columns], style=status_color)

    console.print(table)


def handle_json():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)
    with open(DB_FILE, "r") as f:
        return json.load(f)


def update_db(task_list):
    with open(DB_FILE, "w") as f:
        json.dump(task_list, f, indent=4)


def get_next_id(task_list):
    if not task_list:
        return 1
    return max(task["id"] for task in task_list) + 1


def find_task_by_id(task_list, task_id):
    for index, task in enumerate(task_list):
        if task["id"] == task_id:
            return task, index
    return None, None


def add_task(description):
    if not description or not description.strip():
        console.print("[red]Error: Task description cannot be empty.[/red]")
        return

    task_list = handle_json()
    new_task = task_struct.copy()
    new_task["id"] = get_next_id(task_list)
    new_task["description"] = description.strip()
    new_task["status"] = "todo"
    new_task["createdAt"] = new_task["updatedAt"] = datetime.now().isoformat()

    task_list.append(new_task)
    update_db(task_list)
    console.print(
        f'[green]Task "{description}" added successfully, id: {new_task["id"]}[/green]'
    )


def delete_task(task_id):
    task_list = handle_json()
    task, index = find_task_by_id(task_list, task_id)

    if task is None:
        console.print(f"[red]Error: Task with ID {task_id} not found.[/red]")
        return

    task_list.pop(index)
    update_db(task_list)
    console.print(f"[green]Task with ID {task_id} removed successfully.[/green]")


def update_task(task_id, description):
    if not description or not description.strip():
        console.print("[red]Error: Task description cannot be empty.[/red]")
        return

    task_list = handle_json()
    task, index = find_task_by_id(task_list, task_id)

    if task is None:
        console.print(f"[red]Error: Task with ID {task_id} not found.[/red]")
        return

    task_list[index]["description"] = description.strip()
    task_list[index]["updatedAt"] = datetime.now().isoformat()
    update_db(task_list)
    console.print(
        f"[green]Task with ID {task_id} updated successfully to '{description}'.[/green]"
    )


def list_tasks(status=None):
    task_list = handle_json()

    if status:
        filtered_tasks = [task for task in task_list if task["status"] == status]
    else:
        filtered_tasks = task_list

    # Sort tasks by ID
    filtered_tasks.sort(key=lambda x: x["id"])
    make_table("Tasks", filtered_tasks)


def update_status(task_id, status):
    task_list = handle_json()
    valid_choices = ["in-progress", "done"]

    if status not in valid_choices:
        console.print(
            f"[red]Error: Status '{status}' is not valid. Valid options: {', '.join(valid_choices)}[/red]"
        )
        return

    task, index = find_task_by_id(task_list, task_id)

    if task is None:
        console.print(f"[red]Error: Task with ID {task_id} not found.[/red]")
        return

    task_list[index]["status"] = status
    task_list[index]["updatedAt"] = datetime.now().isoformat()
    update_db(task_list)
    console.print(
        f"[green]Task with ID {task_id} status updated to '{status}'.[/green]"
    )


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        "IncariCLI",
        "%(prog)s <command> <subcommand> [flags]\n",
        "A simple task manager for your CLI",
        "https://github.com/paolobtl",
    )

    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a new task: DESCRIPTION")
    add_parser.add_argument(
        "description", help="Description of the task to add", metavar="DESCRIPTION"
    )

    update_parser = subparsers.add_parser(
        "update", help="Update an existing task: ID DESCRIPTION"
    )
    update_parser.add_argument(
        "id", type=int, help="The ID of the task to update", metavar="ID"
    )
    update_parser.add_argument(
        "description", help="New description for the task", metavar="DESCRIPTION"
    )

    delete_parser = subparsers.add_parser("delete", help="Delete a task: ID")
    delete_parser.add_argument(
        "id", type=int, help="The ID of the task to remove", metavar="ID"
    )

    list_parser = subparsers.add_parser("list", help="List tasks: STATUS")
    list_parser.add_argument(
        "status",
        nargs="?",
        choices=VALID_STATUSES,
        help="(Optional) Filter tasks by status: todo, in-progress, or done. If omitted, shows all tasks",
        metavar="STATUS",
    )

    status_parser = subparsers.add_parser("status", help="Update task status: ID STATUS")
    status_parser.add_argument(
        "id", type=int, help="The ID of the task to update", metavar="ID"
    )
    status_parser.add_argument(
        "new_status",
        choices=["in-progress", "done"],
        help="New status for the task: in-progress or done",
        metavar="STATUS",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
    else:
        match args.command:
            case "add":
                add_task(args.description)
            case "update":
                update_task(args.id, args.description)
            case "delete":
                delete_task(args.id)
            case "list":
                list_tasks(args.status)
            case "status":
                update_status(args.id, args.new_status)


if __name__ == "__main__":
    main()
