from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
from app.services.ai_service import AIService

router = APIRouter(tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)

    try:
        while True:
            # Receive message from user
            user_message = await websocket.receive_text()

            try:
                # Call AI service (RAG runs in background thread)
                ai_response = await AIService.get_legal_advice(user_message)

            except Exception as e:
                # Prevent crash if AI fails
                ai_response = "Sorry, an internal AI error occurred."
                print(f"AI Error: {e}")

            # Send response back to user
            await manager.send_personal_message(ai_response, user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"User {user_id} disconnected.")
