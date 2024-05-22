from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import Achievement, Player, PlayerAchievement
from uuid import UUID

achievements_router = APIRouter(prefix="/achievements", tags=["Достижения"])


@achievements_router.get("/player/{player_id}", summary="Получение всех достижений игрока с их описанием")
async def get_player_achievements(player_id: UUID, db: AsyncSession = Depends(get_db)):
    # Получение списка ачивок у игрока
    stmt_player_achievements = select(PlayerAchievement).where(PlayerAchievement.player_id == player_id)
    result_player_achievements = await db.execute(stmt_player_achievements)
    player_achievements = result_player_achievements.scalars().all()

    if not player_achievements:
        raise HTTPException(status_code=404, detail="No achievements found for player")

    # Извлечение ID ачивок
    achievement_ids = [pa.achievement_id for pa in player_achievements]

    # Получение полной информации о каждой ачивке
    stmt_achievements = select(Achievement).where(Achievement.id.in_(achievement_ids))
    result_achievements = await db.execute(stmt_achievements)
    achievements = result_achievements.scalars().all()

    # Формирование ответа
    achievements_data = [
        {
            "id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "reward": achievement.reward,
            "image_url": achievement.image_url
        } for achievement in achievements
    ]

    return {"achievements": achievements_data}


@achievements_router.post("/assign/", summary="Прсиваивание игроку определенного достижения")
async def assign_achievement_to_player(player_id: UUID, achievement_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt_achievement = select(Achievement).where(Achievement.id == achievement_id)
    result_achievement = await db.execute(stmt_achievement)
    achievement = result_achievement.scalars().first()

    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    stmt_player = select(Player).where(Player.id == player_id)
    result_player = await db.execute(stmt_player)
    player = result_player.scalars().first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    player.balance += achievement.reward

    new_player_achievement = PlayerAchievement(player_id=player_id, achievement_id=achievement_id)
    db.add(new_player_achievement)
    await db.commit()

    return {"message": "Achievement assigned to player"}

@achievements_router.get("/", summary="Получение информации о достижениях")
async def get_all_players(db: AsyncSession = Depends(get_db)):
    stmt = select(Achievement)
    result = await db.execute(stmt)
    achievements = result.scalars().all()
    return achievements

