"""
WebSocket endpoint for real-time live news feed.
Broadcasts new_article, new_deal, and new_alert events to all connected clients.
"""

import json
from typing import List
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts events."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: dict):
        """Broadcast an event to all connected clients."""
        message = json.dumps(
            {
                "event": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            },
            default=str,
        )
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.active_connections.remove(conn)

    @property
    def client_count(self) -> int:
        return len(self.active_connections)


# Singleton manager — importable from other modules to broadcast events
manager = ConnectionManager()


@router.websocket("/ws/live-feed")
async def live_feed(websocket: WebSocket):
    """
    WebSocket endpoint for real-time news feed.

    Connect to receive live events:
    - ``new_article`` — when a new article is ingested
    - ``new_deal``    — when a deal is detected
    - ``new_alert``   — when a new alert is generated

    Example client (JavaScript)::

        const ws = new WebSocket("ws://localhost:8000/ws/live-feed");
        ws.onmessage = (e) => console.log(JSON.parse(e.data));
    """
    await manager.connect(websocket)
    try:
        # Send welcome message
        await websocket.send_text(
            json.dumps(
                {
                    "event": "connected",
                    "data": {"message": "Connected to Banking News live feed"},
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )
        # Keep connection alive — listen for client pings
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(
                    json.dumps({"event": "pong", "timestamp": datetime.utcnow().isoformat()})
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
