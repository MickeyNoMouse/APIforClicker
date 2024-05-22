from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models.models import Player, Location, PlayerLocation
from uuid import UUID

locations_router = APIRouter(prefix="/locations", tags=["Локации"])

@locations_router.get("/", summary="Получение информации о локациях")
async def get_all_players(db: AsyncSession = Depends(get_db)):
    stmt = select(Location)
    result = await db.execute(stmt)
    locations = result.scalars().all()
    return locations

@locations_router.put("/change/{player_id}", summary="Изменение текущей локации игрока")
async def change_location(player_id: UUID, location_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt_player = select(Player).where(Player.id == player_id)
    result_player = await db.execute(stmt_player)
    player = result_player.scalars().first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    stmt_location = select(Location).where(Location.id == location_id)
    result_location = await db.execute(stmt_location)
    location = result_location.scalars().first()

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    player.current_location_id = location_id

    new_player_location = PlayerLocation(player_id=player_id, location_id=location_id)
    db.add(new_player_location)

    await db.commit()

    return {"message": "Location changed successfully", "new_location_id": str(location.id)}
