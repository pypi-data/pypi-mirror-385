# neuro_simulator/utils/websocket.py
import logging

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages all active WebSocket connections and provides broadcasting capabilities."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.admin_connections: list[WebSocket] = []
        logger.info("WebSocketManager initialized.")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"WebSocket client connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                logger.info(
                    f"WebSocket client disconnected. Total connections: {len(self.active_connections)}"
                )
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect: {e}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(
                    f"Could not send personal message, client likely disconnected: {e}"
                )
                self.disconnect(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await self.send_personal_message(message, connection)

    async def broadcast_to_admins(self, message: dict):
        dead_connections = []
        for connection in self.admin_connections:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)
                else:
                    dead_connections.append(connection)
            except (WebSocketDisconnect, ConnectionResetError):
                dead_connections.append(connection)
            except Exception as e:
                logger.error(f"Failed to send message to admin connection: {e}")
                dead_connections.append(connection)

        for connection in dead_connections:
            if connection in self.admin_connections:
                self.admin_connections.remove(connection)


# Global singleton instance
connection_manager = WebSocketManager()
