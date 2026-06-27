import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from auth import router as auth_router, refresh_access_token
from agents.router import route
from memory.store import init_db, get_tokens, get_memory, save_memory
from zoho_client import ZohoClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        tokens = await get_tokens(req.user_id)
        if not tokens:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated. Please connect your Zoho account first."
            )

        client = ZohoClient(tokens["access_token"])
        memory = await get_memory(req.user_id)

        try:
            response, updated_memory = await route(req.message, client, memory)
        except HTTPException as exc:
            if exc.status_code == 401:
                new_token = await refresh_access_token(req.user_id)
                if not new_token:
                    raise HTTPException(
                        status_code=401,
                        detail="Zoho session expired. Please reconnect your account."
                    )
                client = ZohoClient(new_token)
                response, updated_memory = await route(req.message, client, memory)
            else:
                raise

        await save_memory(req.user_id, updated_memory)

        return ChatResponse(response=response)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unhandled error in /chat: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Internal error: {str(e)}"
        )


@app.get("/")
async def root():
    return {"status": "Zoho Chatbot running", "version": "1.0.1"}
