from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from routes.auth import auth_router
from routes.achievements import achievements_router
from routes.leaderboard import leaderboard_router
from routes.locations import locations_router
from routes.tools import tools_router
from routes.buys import buys_router
from uuid import UUID
from database import get_db
from typing import List
from models.models import Player
import json
app = FastAPI()


app.include_router(auth_router)
app.include_router(achievements_router)
app.include_router(leaderboard_router)
app.include_router(locations_router)
app.include_router(tools_router)
app.include_router(buys_router)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: UUID, db: AsyncSession = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            update_data = json.loads(data)

            stmt = select(Player).where(Player.id == player_id)
            result = await db.execute(stmt)
            player = result.scalars().first()
            if player:
                player.balance = update_data['balance']
                await db.commit()
                await manager.send_personal_message(f"Balance updated to {player.balance}", websocket)
            else:
                await manager.send_personal_message("Player not found", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Player {player_id} left the chat")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)