from tools.zoho_tools import create_task, update_task, delete_task
from zoho_client import ZohoClient

async def run_action_agent(message: str, client: ZohoClient, memory: dict):
    msg = message.lower()

    # CREATE
    if "create" in msg or "add" in msg:
        task_name = message.split("called")[-1].strip() if "called" in message else message.split("create task")[-1].strip()
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
        task_id = ''.join(filter(str.isdigit, message))
        project_id = memory.get("active_project_id")
        if not project_id or not task_id:
            return "Please specify the task number and make sure a project is selected.", memory, None

        pending = {
            "action": "delete",
            "project_id": project_id,
            "task_id": task_id
        }
        memory["pending_action"] = pending
        return f"Delete task #{task_id}? Reply 'yes' to confirm.", memory, pending

    # UPDATE
    if "update" in msg or "change" in msg:
        task_id = ''.join(filter(str.isdigit, message))
        project_id = memory.get("active_project_id")
        if not project_id or not task_id:
            return "Please specify the task and project.", memory, None

        pending = {
            "action": "update",
            "project_id": project_id,
            "task_id": task_id,
            "data": {"status": "closed"}
        }
        memory["pending_action"] = pending
        return f"Update task #{task_id} status to closed? Reply 'yes' to confirm.", memory, pending

    return "I can create, update, or delete tasks.", memory, None


async def confirm_action(client: ZohoClient, memory: dict):
    pending = memory.get("pending_action")
    if not pending:
        return "No pending action.", memory

    action = pending["action"]
    project_id = pending["project_id"]

    if action == "create":
        result = await create_task(client, project_id, pending["task_name"])
        memory.pop("pending_action", None)
        return f"Task '{pending['task_name']}' created!", memory

    if action == "delete":
        await delete_task(client, project_id, pending["task_id"])
        memory.pop("pending_action", None)
        return f"Task #{pending['task_id']} deleted.", memory

    if action == "update":
        await update_task(client, project_id, pending["task_id"], pending["data"])
        memory.pop("pending_action", None)
        return f"Task #{pending['task_id']} updated.", memory

    return "Unknown action.", memory