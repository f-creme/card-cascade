import asyncio
import uuid

from app.db import close_pool, ensure_user, get_pool, init_pool, record_game_result


def run(coro):
    return asyncio.run(coro)


def test_ensure_user_creates_a_row():
    async def scenario():
        await init_pool()
        pool = get_pool()
        user_id = str(uuid.uuid4())

        await ensure_user(pool, user_id, "Alice")

        row = await pool.fetchrow("SELECT username, games_played, games_won FROM users WHERE uuid = $1", user_id)
        await close_pool()
        return row

    row = run(scenario())

    assert row["username"] == "Alice"
    assert row["games_played"] == 0
    assert row["games_won"] == 0


def test_ensure_user_is_idempotent():
    async def scenario():
        await init_pool()
        pool = get_pool()
        user_id = str(uuid.uuid4())

        await ensure_user(pool, user_id, "Alice")
        await ensure_user(pool, user_id, "Alice")

        count = await pool.fetchval("SELECT count(*) FROM users WHERE uuid = $1", user_id)
        await close_pool()
        return count

    count = run(scenario())

    assert count == 1


def test_record_game_result_increments_played_and_won():
    async def scenario():
        await init_pool()
        pool = get_pool()
        alice, bob = str(uuid.uuid4()), str(uuid.uuid4())

        await ensure_user(pool, alice, "Alice")
        await ensure_user(pool, bob, "Bob")

        await record_game_result(pool, [alice, bob], winner_id=alice)

        row_alice = await pool.fetchrow("SELECT games_played, games_won FROM users WHERE uuid = $1", alice)
        row_bob = await pool.fetchrow("SELECT games_played, games_won FROM users WHERE uuid = $1", bob)
        await close_pool()
        return row_alice, row_bob

    row_alice, row_bob = run(scenario())

    assert dict(row_alice) == {"games_played": 1, "games_won": 1}
    assert dict(row_bob) == {"games_played": 1, "games_won": 0}


def test_record_game_result_accumulates_across_multiple_games():
    async def scenario():
        await init_pool()
        pool = get_pool()
        alice, bob = str(uuid.uuid4()), str(uuid.uuid4())

        await ensure_user(pool, alice, "Alice")
        await ensure_user(pool, bob, "Bob")

        await record_game_result(pool, [alice, bob], winner_id=alice)
        await record_game_result(pool, [alice, bob], winner_id=bob)
        await record_game_result(pool, [alice, bob], winner_id=bob)

        row_alice = await pool.fetchrow("SELECT games_played, games_won FROM users WHERE uuid = $1", alice)
        row_bob = await pool.fetchrow("SELECT games_played, games_won FROM users WHERE uuid = $1", bob)
        await close_pool()
        return row_alice, row_bob

    row_alice, row_bob = run(scenario())

    assert dict(row_alice) == {"games_played": 3, "games_won": 1}
    assert dict(row_bob) == {"games_played": 3, "games_won": 2}