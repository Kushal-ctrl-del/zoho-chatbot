import aiosqlite
import json

DB_PATH = "memory.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                user_id TEXT PRIMARY KEY,
                access_token TEXT,
                refresh_token TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                user_id TEXT PRIMARY KEY,
                data TEXT
            )
        """)
        await db.commit()

async def save_tokens(user_id: str, access_token: str, refresh_token: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO tokens (user_id, access_token, refresh_token)
            VALUES (?, ?, ?)
        """, (user_id, access_token, refresh_token))
        await db.commit()

async def get_tokens(user_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async for row in await db.execute(
            "SELECT access_token, refresh_token FROM tokens WHERE user_id=?", (user_id,)
        ):
            return {"access_token": row[0], "refresh_token": row[1]}
    return None

async def save_memory(user_id: str, data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO memory (user_id, data)
            VALUES (?, ?)
        """, (user_id, json.dumps(data)))
        await db.commit()

async def get_memory(user_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async for row in await db.execute(
            "SELECT data FROM memory WHERE user_id=?", (user_id,)
        ):
            return json.loads(row[0])
    return {}