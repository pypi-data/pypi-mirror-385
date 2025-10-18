"""WebSocket routes for real-time updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time trace updates.

    Clients can connect to this endpoint to receive real-time notifications about:
    - New traces created
    - Traces updated
    - Traces deleted
    - Statistics updates

    Message format:
    {
        "type": "trace_created" | "trace_updated" | "trace_deleted" | "stats_updated",
        "data": {...}
    }
    """
    manager = websocket.app.state.ws_manager
    await manager.connect(websocket)

    try:
        # Send welcome message
        await manager.send_personal_message(
            {
                "type": "connected",
                "data": {
                    "message": "Connected to msgtrace WebSocket",
                    "connections": manager.connection_count,
                },
            },
            websocket,
        )

        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages from client (ping/pong, subscriptions, etc.)
            data = await websocket.receive_text()

            # Echo back for now (can be extended for subscriptions)
            if data == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "data": {}}, websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
