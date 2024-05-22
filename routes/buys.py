from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from database import get_db
from models.models import Player, Tool, PlayerTool
from uuid import UUID

buys_router = APIRouter(prefix="/buy", tags=["Покупки"])

@buys_router.put("/tool/{player_id}", summary="Покупка нового инструмента для игрока")
async def buy_tool(player_id: UUID, tool_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt_player = select(Player).where(Player.id == player_id).options(joinedload(Player.current_tool))
    result_player = await db.execute(stmt_player)
    player = result_player.scalars().first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")


    stmt_tool = select(Tool).where(Tool.id == tool_id)
    result_tool = await db.execute(stmt_tool)
    tool = result_tool.scalars().first()

    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")


    if player.balance < tool.cost:
        raise HTTPException(status_code=400, detail="Insufficient balance")


    player.current_tool_id = tool_id
    player.balance -= tool.cost

    new_player_tool = PlayerTool(player_id=player_id, tool_id=tool_id)
    db.add(new_player_tool)

    await db.commit()

    return {"message": "Tool purchased successfully", "new_balance": player.balance}
