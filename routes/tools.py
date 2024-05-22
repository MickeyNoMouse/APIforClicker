from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select

from database import get_db
from models.models import Tool


tools_router = APIRouter(prefix="/tools", tags=["Инструменты добычи"])

@tools_router.get("/", summary="Получение информации об инструментах для добычи")
async def get_all_players(db: AsyncSession = Depends(get_db)):
    stmt = select(Tool)
    result = await db.execute(stmt)
    tools = result.scalars().all()
    return tools
