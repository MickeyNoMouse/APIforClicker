from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select

from database import get_db
from models.models import Player


leaderboard_router = APIRouter(prefix="/leaderboard", tags=["Статистика"])

@leaderboard_router.get("/players", summary="Получение информации о всех игроках")
async def get_all_players(db: AsyncSession = Depends(get_db)):
    stmt = select(Player)
    result = await db.execute(stmt)
    players = result.scalars().all()
    return players
