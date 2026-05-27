import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from config import (ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, 
                    ZOHO_REDIRECT_URI, ZOHO_AUTH_URL, 
                    ZOHO_TOKEN_URL, ZOHO_SCOPE)
from memory.store import save_tokens, get_tokens

router = APIRouter()

@router.get("/auth/login")
async def login():
    url = (
        f"{ZOHO_AUTH_URL}?response_type=code"
        f"&client_id={ZOHO_CLIENT_ID}"
        f"&scope={ZOHO_SCOPE}"
        f"&redirect_uri={ZOHO_REDIRECT_URI}"
        f"&access_type=offline"
    )
    return RedirectResponse(url)

@router.get("/auth/callback")
async def callback(request: Request, code: str):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(ZOHO_TOKEN_URL, data={
                "code": code,
                "client_id": ZOHO_CLIENT_ID,
                "client_secret": ZOHO_CLIENT_SECRET,
                "redirect_uri": ZOHO_REDIRECT_URI,
                "grant_type": "authorization_code"
            })
            res.raise_for_status()
            tokens = res.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(status_code=400, detail="OAuth failed")

    if "access_token" not in tokens:
        raise HTTPException(status_code=400, detail="OAuth failed")

    user_id = "default_user"  # single user for now
    await save_tokens(user_id, tokens["access_token"], tokens.get("refresh_token"))

    return RedirectResponse("http://localhost:3000?auth=success")

async def refresh_access_token(user_id: str):
    tokens = await get_tokens(user_id)
    if not tokens:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(ZOHO_TOKEN_URL, data={
                "refresh_token": tokens["refresh_token"],
                "client_id": ZOHO_CLIENT_ID,
                "client_secret": ZOHO_CLIENT_SECRET,
                "grant_type": "refresh_token"
            })
            res.raise_for_status()
            new_tokens = res.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(status_code=400, detail="Token refresh failed")

    if "access_token" not in new_tokens:
        raise HTTPException(status_code=400, detail="Token refresh failed")

    await save_tokens(user_id, new_tokens["access_token"], tokens["refresh_token"])
    return new_tokens["access_token"]