import asyncio
from app.core.database import engine

async def test_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            db_name = result.scalar()
            print(f"✅ Połączenie działa! Używana baza: {db_name}")
    except Exception as e:
        print("❌ Błąd połączenia z bazą danych:", e)

if __name__ == "__main__":
    asyncio.run(test_connection())