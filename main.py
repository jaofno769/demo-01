from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import jwt

from pwdlib import PasswordHash

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal, create_tables, engine, get_db
from models import User
from uvicorn import run




SECRET_KEY = "demo-secret-key-please-change"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

# 使用Argon2哈希算法
password_hash = PasswordHash.recommended()

#提取请求头中的token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token"
)



async def init_db():

    await create_tables()

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(User).where(User.username == "admin")
        )

        user = result.scalar_one_or_none()

        if not user:
            user = User(
                username="admin",
                password_hash=password_hash.hash("123456"),
                is_active=True
            )

            db.add(user)
            await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="FastAPI Login Demo",
    lifespan=lifespan
)


# =========================
# 3. 创建 JWT
# =========================

def create_access_token(username: str):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# =========================
# 4. 登录接口
# =========================

@app.post("/token", tags=["认证"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(
            User.username == form_data.username
        )
    )

    user = result.scalar_one_or_none()

    if not user or not password_hash.verify(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="用户已被禁用"
        )

    access_token = create_access_token(user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }




async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=401,
                detail="无效的 Token"
            )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token 无效或已过期"
        )

    result = await db.execute(
        select(User).where(User.username == username)
    )

    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="用户不存在或已被禁用"
        )

    return user



@app.get("/users/me", tags=["用户"])
async def get_user(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "username": current_user.username
    }


