from tools.zoho_tools import (
    list_projects,
    list_tasks,
    get_task_details,
    list_project_members,
    get_task_utilisation,
)
from zoho_client import ZohoClient


async def run_query_agent(message: str, client: ZohoClient, memory: dict):
    msg = message.lower().strip()

    # General greeting / non-Zoho queries
    if any(k in msg for k in ["hello", "hi", "hey", "what is ai", "who are you", "what can you do"]):
        return (
            "I'm Skysecure's Zoho Projects AI Agent. I can help you:\n"
            "• List projects and tasks\n"
            "• Create, update, or delete tasks\n"
            "• Show project members and workloads\n"
            "What would you like to do?",
            memory,
        )

    # List projects
    if "project" in msg and any(k in msg for k in ["list", "what", "show", "have"]):
        projects = await list_projects(client)
        memory["projects"] = projects
        if projects:
            memory["active_project_id"] = projects[0].get("id_string")
        names = [p.get("name", "Unnamed") for p in projects]
        return f"Your projects: {', '.join(names) if names else 'No projects found.'}", memory

    # List tasks
    if "task" in msg and any(k in msg for k in ["list", "show"]):
        project_id = memory.get("active_project_id")
        if not project_id:
            return "Which project? Please mention the project name first.", memory
        tasks = await list_tasks(client, project_id)
        memory["tasks"] = tasks
        names = [f"{t.get('name', 'Unnamed')} (ID: {t.get('id_string', 'N/A')})" for t in tasks]
        return f"Tasks: {', '.join(names) if names else 'No tasks found.'}", memory

    # First project / first task
    if "first" in msg and any(k in msg for k in ["task", "project"]):
        projects = memory.get("projects", [])
        if not projects:
            return "Fetch your projects first.", memory
        project_id = projects[0].get("id_string")
        if not project_id:
            return "Invalid project data.", memory
        memory["active_project_id"] = project_id
        tasks = await list_tasks(client, project_id)
        memory["tasks"] = tasks
        names = [f"{t.get('name', 'Unnamed')} (ID: {t.get('id_string', 'N/A')})" for t in tasks]
        return f"Tasks in {projects[0].get('name', 'Unnamed')}: {', '.join(names) if names else 'No tasks.'}", memory

    # Members
    if "member" in msg or ("who" in msg and "project" in msg):
        project_id = memory.get("active_project_id")
        if not project_id:
            return "Which project?", memory
        members = await list_project_members(client, project_id)
        names = [f"{m.get('name', 'Unknown')} ({m.get('role', 'member')})" for m in members]
        return f"Members: {', '.join(names) if names else 'No members found.'}", memory

    # Utilisation / workload
    if any(k in msg for k in ["utilisation", "most tasks", "workload"]):
        project_id = memory.get("active_project_id")
        if not project_id:
            return "Which project?", memory
        util = await get_task_utilisation(client, project_id)
        if not util:
            return "No workload data available.", memory
        summary = ", ".join([f"{k}: {v} tasks" for k, v in util.items()])
        return f"Task load: {summary}", memory

    # Task details
    if "detail" in msg and "task" in msg:
        tasks = memory.get("tasks", [])
        if not tasks:
            return "Show tasks first.", memory
        task = tasks[0]
        project_id = memory.get("active_project_id")
        if not project_id:
            return "No active project.", memory
        details = await get_task_details(client, project_id, task.get("id_string"))
        return f"Task details: {details}", memory

    # Fallback
    return (
        "I can help with:\n"
        "• Listing projects and tasks\n"
        "• Creating, updating, or deleting tasks\n"
        "• Showing project members and workloads\n"
        "What would you like to do?",
        memory,
    )
