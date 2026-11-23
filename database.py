from os import getenv

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = URL.create(
    "mysql+aiomysql",
    username=getenv("MYSQL_USER") or "signin",
    password=getenv("MYSQL_PASSWORD") or "signin-local-db",
    host="127.0.0.1",
    port=int(getenv("MYSQL_PORT") or "3307"),
    database=getenv("MYSQL_DATABASE") or "fastapi_demo",
    query={"charset": "utf8mb4"},
)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
