from dotenv import load_dotenv
import os

load_dotenv()

ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")
ZOHO_SCOPE = "ZohoProjects.portals.READ,ZohoProjects.projects.READ,ZohoProjects.tasks.READ,ZohoProjects.tasks.WRITE"
ZOHO_AUTH_URL = "https://accounts.zoho.in/oauth/v2/auth"
ZOHO_TOKEN_URL = "https://accounts.zoho.in/oauth/v2/token"
ZOHO_API_BASE = "https://projectsapi.zoho.in/restapi"

GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL = "grok-3-mini"

SECRET_KEY = os.getenv("SECRET_KEY")