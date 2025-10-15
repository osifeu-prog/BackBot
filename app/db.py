import asyncio, aiosqlite, os
from pathlib import Path

DATA_DIR = Path('data')
DB_PATH = DATA_DIR / 'seleb0t.sqlite3'

SCHEMA = [
    'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, tg_id INTEGER UNIQUE, username TEXT, first_name TEXT, last_name TEXT, joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);',
    'CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, tg_id INTEGER, amount_nis REAL, tx_hash TEXT, status TEXT DEFAULT "pending", created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);',
    'CREATE TABLE IF NOT EXISTS nfts (id INTEGER PRIMARY KEY, tg_id INTEGER, image_url TEXT, token_id TEXT, tx_hash TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'
]

async def migrate():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        for s in SCHEMA:
            await db.execute(s)
        await db.commit()

def migrate_sync():
    asyncio.run(migrate())

if __name__ == '__main__':
    migrate_sync()
