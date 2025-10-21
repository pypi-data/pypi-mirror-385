# todoist-to-todotxt

![PyPI - Version](https://img.shields.io/pypi/v/todoist-to-todotxt)

Script to save tasks from Todoist to todo.txt format.

It provides support for export of limited set of Todoist's task fields, particularly:

- Priority
- Creation date
- Task name and description (merged together into one line)
- Project and section (merged together)
- Labels
- Due date
- Recurrence date
- Deadline date

Definitely NOT supported:

- Sub-tasks (all tasks exported in flat list, so there will be no tree-like structure)
- Completed tasks (it is possible to load only active tasks via API)
- Due time (only due date part saved)
- Comments
- Task order number
- Creator and assignee (assuming that it is used for personal todo-list)
- Reminders
- Location

Above list may be not complete, as there could be features in Todoist I'm not aware of.

## Install

Use `pipx` or `pip` to install:

    $ pipx install todoist-to-todotxt

    $ pip install todoist-to-todotxt

## Usage

Generate API token in your Todoist account [Integrations settings](https://todoist.com/app/settings/integrations/developer).

Launch script with your API token (it will print tasks in todo.txt format to stdout):

    $ todoist-to-todotxt <TODOIST-TOKEN>

## Contributing

Feel free to open bug reports and send pull requests.

