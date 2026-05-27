from tools.zoho_tools import create_task, update_task, delete_task
from zoho_client import ZohoClient

def find_task_id(message: str, memory: dict):
    tasks = memory.get("tasks", [])
    # match by name
    for task in tasks:
        if task["name"].lower() in message.lower():
            return task["id_string"]
    # match by number in message
    digits = ''.join(filter(str.isdigit, message))
    if digits:
        for task in tasks:
            if task["id_string"] == digits:
                return digits
    return None

async def run_action_agent(message: str, client: ZohoClient, memory: dict):
    msg = message.lower()

    # CREATE
    if "create" in msg or "add" in msg:
        if "called" in message:
            task_name = message.split("called")[-1].strip()
        elif "create task" in msg:
            task_name = message.lower().split("create task")[-1].strip()
        elif "add task" in msg:
            task_name = message.lower().split("add task")[-1].strip()
        else:
            task_name = message.strip()

        project_id = memory.get("active_project_id")
        if not project_id:
            return "Which project should I create the task in?", memory, None

        pending = {
            "action": "create",
            "project_id": project_id,
            "task_name": task_name
        }
        memory["pending_action"] = pending
        return f"Create task '{task_name}' in this project? Reply 'yes' to confirm.", memory, pending

    # DELETE
    if "delete" in msg:
        task_id = find_task_id(message, memory)
        project_id = memory.get("active_project_id")

        if not project_id:
            return "No active project. List projects first.", memory, None
        if not task_id:
            return "Couldn't find that task. Show tasks first so I can find the ID.", memory, None

        pending = {
            "action": "delete",
            "project_id": project_id,
            "task_id": task_id
        }
        memory["pending_action"] = pending
        return f"Delete task '{task_id}'? Reply 'yes' to confirm.", memory, pending

    # UPDATE
    if "update" in msg or "change" in msg or "mark" in msg:
        task_id = find_task_id(message, memory)
        project_id = memory.get("active_project_id")

        if not project_id or not task_id:
            return "Specify the task and make sure a project is selected.", memory, None

        status = "closed" if "done" in msg or "complete" in msg or "close" in msg else "open"

        pending = {
            "action": "update",
            "project_id": project_id,
            "task_id": task_id,
            "data": {"status": status}
        }
        memory["pending_action"] = pending
        return f"Update task '{task_id}' status to '{status}'? Reply 'yes' to confirm.", memory, pending

    return "I can create, update, or delete tasks.", memory, None


async def confirm_action(client: ZohoClient, memory: dict):
    pending = memory.get("pending_action")
    if not pending:
        return "No pending action.", memory

    action = pending["action"]
    project_id = pending["project_id"]

    if action == "create":
        await create_task(client, project_id, pending["task_name"])
        memory.pop("pending_action")
        return f"Task '{pending['task_name']}' created!", memory

    if action == "delete":
        await delete_task(client, project_id, pending["task_id"])
        memory.pop("pending_action")
        return f"Task '{pending['task_id']}' deleted.", memory

    if action == "update":
        await update_task(client, project_id, pending["task_id"], pending["data"])
        memory.pop("pending_action")
        return f"Task '{pending['task_id']}' updated.", memory

    return "Unknown action.", memory