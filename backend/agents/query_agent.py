from tools.zoho_tools import (list_projects, list_tasks,
                               get_task_details, list_project_members,
                               get_task_utilisation)
from zoho_client import ZohoClient

async def run_query_agent(message: str, client: ZohoClient, memory: dict):
    msg = message.lower()

    if "project" in msg and ("list" in msg or "what" in msg or "show" in msg or "have" in msg):
        projects = await list_projects(client)
        memory["projects"] = projects
        if projects:
            memory["active_project_id"] = projects[0]["id_string"]
        names = [p["name"] for p in projects]
        return f"Your projects: {', '.join(names)}", memory

    if "task" in msg and ("list" in msg or "show" in msg):
        project_id = memory.get("active_project_id")
        if not project_id:
            return "Which project? Please mention the project name first.", memory
        tasks = await list_tasks(client, project_id)
        memory["tasks"] = tasks
        names = [f"{t['name']} (ID: {t['id_string']})" for t in tasks]
        return f"Tasks: {', '.join(names)}", memory

    if "first" in msg and ("task" in msg or "project" in msg):
        projects = memory.get("projects", [])
        if not projects:
            return "Fetch your projects first.", memory
        project_id = projects[0]["id_string"]
        memory["active_project_id"] = project_id
        tasks = await list_tasks(client, project_id)
        memory["tasks"] = tasks
        names = [f"{t['name']} (ID: {t['id_string']})" for t in tasks]
        return f"Tasks in {projects[0]['name']}: {', '.join(names)}", memory

    if "member" in msg or ("who" in msg and "project" in msg):
        project_id = memory.get("active_project_id")
        if not project_id:
            return "Which project?", memory
        members = await list_project_members(client, project_id)
        names = [f"{m['name']} ({m.get('role', 'member')})" for m in members]
        return f"Members: {', '.join(names)}", memory

    if "utilisation" in msg or "most tasks" in msg or "workload" in msg:
        project_id = memory.get("active_project_id")
        if not project_id:
            return "Which project?", memory
        util = await get_task_utilisation(client, project_id)
        summary = ", ".join([f"{k}: {v} tasks" for k, v in util.items()])
        return f"Task load: {summary}", memory

    if "detail" in msg and "task" in msg:
        tasks = memory.get("tasks", [])
        if not tasks:
            return "Show tasks first.", memory
        task = tasks[0]
        project_id = memory.get("active_project_id")
        details = await get_task_details(client, project_id, task["id_string"])
        return f"Task details: {details}", memory

    return "I can help with listing projects, tasks, members, and workload.", memory