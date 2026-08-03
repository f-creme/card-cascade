import asyncpg

from asyncpg import Pool

from app.config import settings

_pool : Pool | None = None

async def init_pool() -> None:
    global _pool
    _pool = await asyncpg.create_pool(settings.database_url)

async def close_pool() -> None: 
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

def get_pool() -> Pool: 
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    return _pool

async def ensure_user(pool: Pool, user_id: str, username: str, avatar: str | None = None) -> None: 
    """Create user's row if it doesn't exist or update it's username"""
    await pool.execute(
        "INSERT INTO users (uuid, username, avatar) " \
        "VALUES ($1, $2, $3) " \
        "ON CONFLICT (uuid) DO UPDATE SET username = EXCLUDED.username, avatar = EXCLUDED.avatar", 
        user_id, username, avatar
    )

async def get_user(pool: Pool, user_id: str) -> dict | None:
    row = await pool.fetchrow(
        "SELECT uuid, username, avatar, games_played, games_won FROM users WHERE uuid = $1",
        user_id
    )
    return dict(row) if row is not None else None

async def record_game_result(pool: Pool, player_ids: list[str], winner_id: str) -> None:
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.executemany(
                "UPDATE users SET games_played = games_played + 1 WHERE uuid = $1",
                [(pid, ) for pid in player_ids]
            )
            await conn.execute(
                "UPDATE users SET games_won = games_won + 1 WHERE uuid = $1",
                winner_id
            )