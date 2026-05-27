from agents.query_agent import run_query_agent
from agents.action_agent import run_action_agent, confirm_action
from zoho_client import ZohoClient

ACTION_KEYWORDS = ["create", "add", "delete", "update", "change", "assign"]
CONFIRM_KEYWORDS = ["yes", "confirm", "proceed", "go ahead", "yep", "yeah"]
CANCEL_KEYWORDS = ["no", "cancel", "stop", "abort"]

async def route(message: str, client: ZohoClient, memory: dict):
    msg = message.lower().strip()

    # Handle HIL confirmation
    if memory.get("pending_action"):
        if any(k in msg for k in CONFIRM_KEYWORDS):
            response, memory = await confirm_action(client, memory)
            return response, memory
        elif any(k in msg for k in CANCEL_KEYWORDS):
            memory.pop("pending_action")
            return "Action cancelled.", memory

    # Route to action agent
    if any(k in msg for k in ACTION_KEYWORDS):
        response, memory, _ = await run_action_agent(message, client, memory)
        return response, memory

    # Route to query agent
    response, memory = await run_query_agent(message, client, memory)
    return response, memory