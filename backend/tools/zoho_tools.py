from fastapi import HTTPException

from zoho_client import ZohoClient

async def get_portal_id(client: ZohoClient):
    res = await client.get("/portals/")
    portals = res.get("login_info", {})
    portal_id = portals.get("portal_id")
    if portal_id:
        return portal_id

    portals_list = res.get("portals", [])
    if portals_list and portals_list[0].get("id_string"):
        return portals_list[0]["id_string"]

    raise HTTPException(status_code=502, detail="No Zoho portals found for this account.")

async def list_projects(client: ZohoClient):
    portal_id = await get_portal_id(client)
    res = await client.get(f"/portal/{portal_id}/projects/")
    return res.get("projects", [])

async def list_tasks(client: ZohoClient, project_id: str):
    portal_id = await get_portal_id(client)
    res = await client.get(f"/portal/{portal_id}/projects/{project_id}/tasks/")
    return res.get("tasks", [])

async def get_task_details(client: ZohoClient, project_id: str, task_id: str):
    portal_id = await get_portal_id(client)
    res = await client.get(f"/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/")
    return res.get("tasks", [])

async def create_task(client: ZohoClient, project_id: str, name: str):
    portal_id = await get_portal_id(client)
    res = await client.post(f"/portal/{portal_id}/projects/{project_id}/tasks/", {"name": name})
    return res.get("tasks", [])

async def update_task(client: ZohoClient, project_id: str, task_id: str, data: dict):
    portal_id = await get_portal_id(client)
    res = await client.patch(f"/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/", data)
    return res.get("tasks", [])

async def delete_task(client: ZohoClient, project_id: str, task_id: str):
    portal_id = await get_portal_id(client)
    res = await client.delete(f"/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/")
    return res

async def list_project_members(client: ZohoClient, project_id: str):
    portal_id = await get_portal_id(client)
    res = await client.get(f"/portal/{portal_id}/projects/{project_id}/users/")
    return res.get("users", [])

async def get_task_utilisation(client: ZohoClient, project_id: str):
    tasks = await list_tasks(client, project_id)
    members = await list_project_members(client, project_id)
    
    utilisation = {m["name"]: 0 for m in members}
    for task in tasks:
        assignee = task.get("details", {}).get("owners", [{}])[0].get("name")
        if assignee and assignee in utilisation:
            utilisation[assignee] += 1

    return utilisation