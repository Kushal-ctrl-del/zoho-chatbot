import httpx
from fastapi import HTTPException

from config import ZOHO_API_BASE

class ZohoClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {"Authorization": f"Zoho-oauthtoken {self.access_token}"}

    async def _request_json(self, method: str, endpoint: str, **kwargs):
        async with httpx.AsyncClient() as client:
            try:
                res = await client.request(method, f"{ZOHO_API_BASE}{endpoint}", headers=self.headers, **kwargs)
                res.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text.strip() or f"Zoho request failed with status {exc.response.status_code}"
                raise HTTPException(status_code=exc.response.status_code, detail=detail)

            if not res.content:
                return {}
            try:
                payload = res.json()
            except ValueError:
                return {}

            if isinstance(payload, dict):
                error = payload.get("error")
                if isinstance(error, dict):
                    error_code = error.get("code")
                    error_message = str(error.get("message", "")).lower()
                    if error_code == 6401 or "invalid oauth access token" in error_message:
                        raise HTTPException(
                            status_code=401,
                            detail="Zoho access token expired or invalid. Please login again."
                        )

            return payload

    async def get(self, endpoint: str):
        return await self._request_json("GET", endpoint)

    async def post(self, endpoint: str, data: dict):
        return await self._request_json("POST", endpoint, data=data)

    async def patch(self, endpoint: str, data: dict):
        return await self._request_json("PATCH", endpoint, data=data)

    async def delete(self, endpoint: str):
        return await self._request_json("DELETE", endpoint)