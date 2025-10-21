#!/usr/bin/env python3

import sys
import requests

from requests.adapters import HTTPAdapter, Retry

def cli():
    if len(sys.argv) == 1:
        print("Please, provide Todoist API token to proceed. Abort.")
        sys.exit()

    execute(sys.argv[1])

def clean(line):
    return line.replace(" ", "_")

def get_project(project_id, projects):
    line = ''
    for project in projects:
        if project["id"] == project_id:
            line = project["name"]

            if project['parent_id']:
                line = line + ':' + get_project(project['parent_id'], projects)

            break

    return line

def get_project_section(project_id, section_id, projects, sections):
    line = get_project(project_id, projects)

    for section in sections:
        if section["id"] == section_id:
            line += ":" + section["name"]
            break

    return clean(line)

def load_items(code, http, token, next_cursor):
    if next_cursor:
        link = f'https://api.todoist.com/api/v1/{code}?cursor={next_cursor}'
    else:
        link = f'https://api.todoist.com/api/v1/{code}'

    items_r = http.get(link,
                       headers={"Authorization": f"Bearer {token}"})
    items_r.raise_for_status()

    items = items_r.json()['results']
    cursor = items_r.json()['next_cursor']

    if cursor:
        items = items + load_items(code, http, token, cursor)

    return items

def execute(token):
    retry_strategy = Retry(
            total=5,
            backoff_factor=5,
            status_forcelist=[429, 500, 502, 503, 504]
            )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)

    tasks = load_items('tasks', http, token, None)
    projects = load_items('projects', http, token, None)
    sections = load_items('sections', http, token, None)

    for task in tasks:
        line = ""

        # priority
        if task["priority"] > 1:
            line += "(" + {4: "A", 3: "B", 2: "C"}.get(task["priority"]) + ") "

        # creation date
        line += task["added_at"][:10] + " "

        # content
        line += task["content"]

        if task["description"]:
            # merge description into single line (ignore empty lines)
            desc = task["description"]
            line += " (" + " ".join(l.strip() for l in desc.splitlines() if l) + ")"

        # project
        line += " +" + get_project_section(task["project_id"], task["section_id"],
                                           projects, sections)

        # context
        if task["labels"]:
            for label in task["labels"]:
                line += " @" + clean(label)

        # additional metadata: due and rec
        if task["due"]:
            line += " due:" + task["due"]["date"].partition("T")[0]

            if task["due"]["is_recurring"]:
                line += " rec:" + clean(task["due"]["string"])

        # additional metadata: deadline
        if task["deadline"]:
            line += " deadline:" + task["deadline"]["date"]

        # result
        print(line)

if __name__ == "__main__":
    cli()

