"""
WebSocket endpoints for real-time data streaming.
"""

import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from cc_balancer.core.metrics import metrics_collector


async def websocket_realtime_metrics(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time metrics streaming.

    Sends metrics updates every second to connected clients.

    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()

    try:
        while websocket.client_state == WebSocketState.CONNECTED:
            # Gather latest metrics
            data = {
                "type": "metrics_update",
                "timestamp": asyncio.get_event_loop().time(),
                "data": {
                    "total_requests": metrics_collector.total_requests,
                    "success_rate": metrics_collector.success_rate,
                    "avg_latency_ms": metrics_collector.avg_latency_ms,
                    "latest_requests": metrics_collector.get_latest(limit=10),
                    "provider_stats": metrics_collector.get_provider_stats(),
                },
            }

            # Send to client
            await websocket.send_json(data)

            # Wait 1 second before next update
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    except Exception:
        # Client disconnected or error occurred
        pass
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
