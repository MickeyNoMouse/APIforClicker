from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy.future import select
from database import get_db
from models.models import Player, PlayerCreate, PlayerAchievement
from typing import List
import uuid
auth_router = APIRouter(prefix="/auth", tags=["Аутентификация"])


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@auth_router.post("/register/", response_model=PlayerCreate, summary="Регистрация нового игрока")
async def create_player(username: str, password: str, db: AsyncSession = Depends(get_db)):
    #new_player = Player(**player.dict())
    new_player = Player()
    new_player.id=uuid.uuid4()
    new_player.username = username
    new_player.hashed_password = get_password_hash(password)
    new_player.current_tool_id = 'a0b73509-72ca-4368-b6c9-16429c37409c'
    new_player.current_location_id = 'fed5b2e9-653a-43f2-a38c-eda266984d9d'
    db.add(new_player)
    await db.commit()
    await db.refresh(new_player)
    return new_player

@auth_router.get("/login/", summary="Вход в игру")
async def login_user(username: str, password: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Player).filter(Player.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    return user

