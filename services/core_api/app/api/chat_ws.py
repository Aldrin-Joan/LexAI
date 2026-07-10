"""WebSocket chat endpoint — real-time AI and peer-to-peer messaging.

Connection URL
--------------
ws://<host>/ws/chat/<user_id>?token=<firebase_id_token>

Protocol
--------
Client sends a JSON payload::

    {
        "receiver_id": "ai" | "<firebase_uid>",
        "content": "message text",
        "client_msg_id": "<client-generated UUID>"
    }

Server responds with::

    {
        "sender_id": "<uid or 'ai'>",
        "content": "reply text",
        "client_msg_id": "<same or server UUID>",
        "timestamp": "<ISO-8601>"
    }

Session Lifecycle
-----------------
- Token is verified on connection. Mismatched user_id → 4001 (forbidden).
- Sessions expire after 1 hour (matching Firebase ID token lifetime).
  The server closes with code 4001; the frontend should refresh the token
  and reconnect.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select

try:
    from app.core.db import engine
    from app.core.security import _verify_firebase_token
    from app.models.models import Message
except ImportError:
    from core.db import engine
    from core.security import _verify_firebase_token
    from models.models import Message

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# Maximum WebSocket session duration in seconds (matches Firebase token TTL)
_MAX_SESSION_SECONDS = 3600  # 1 hour


# ---------------------------------------------------------------------------
# Connection Manager
# ---------------------------------------------------------------------------

class ConnectionManager:
    """Registry of active WebSocket connections keyed by Firebase UID.

    Attributes:
        active_connections: Mapping from uid (str) to open WebSocket.
    """

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, uid: str, websocket: WebSocket) -> None:
        """Accept and register a WebSocket connection.

        Args:
            uid: Firebase UID of the connecting user.
            websocket: The incoming WebSocket connection.
        """
        await websocket.accept()
        self.active_connections[uid] = websocket
        logger.info("WS connected: uid=%s", uid)

    def disconnect(self, uid: str) -> None:
        """Remove a user's connection from the registry.

        Args:
            uid: Firebase UID of the disconnecting user.
        """
        self.active_connections.pop(uid, None)
        logger.info("WS disconnected: uid=%s", uid)

    async def send_to(self, uid: str, payload: dict) -> bool:
        """Send a JSON payload to a connected user.

        Args:
            uid: Target Firebase UID.
            payload: Dictionary to serialize and send.

        Returns:
            bool: True if the message was delivered, False if the user
                is offline.
        """
        ws = self.active_connections.get(uid)
        if ws:
            await ws.send_text(json.dumps(payload))
            return True
        return False


manager = ConnectionManager()


# ---------------------------------------------------------------------------
# Helper — persist a Message to the database
# ---------------------------------------------------------------------------

def _persist_message(
    sender_id: str,
    receiver_id: str,
    content: str,
    client_msg_id: str,
) -> None:
    """Write a message record to the database before delivery.

    Duplicate ``client_msg_id`` values are silently ignored (idempotent).

    Args:
        sender_id: Firebase UID of the sender.
        receiver_id: Firebase UID of the recipient.
        content: Message text.
        client_msg_id: Client-generated idempotency key.
    """
    with Session(engine) as session:
        existing = session.exec(
            select(Message).where(
                Message.client_msg_id == client_msg_id
            )
        ).first()
        if existing:
            return  # Already persisted — idempotent

        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            client_msg_id=client_msg_id,
        )
        session.add(message)
        try:
            session.commit()
        except Exception as exc:
            logger.warning("Message persistence failed: %s", exc)
            session.rollback()


# ---------------------------------------------------------------------------
# WebSocket Endpoint
# ---------------------------------------------------------------------------

@router.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
) -> None:
    """Handle a WebSocket chat connection for ``user_id``.

    Authentication
    --------------
    The ``?token=<firebase_id_token>`` query parameter is required.
    The decoded uid must match the ``user_id`` path parameter.

    Session Expiry
    --------------
    The connection is forcibly closed with code 4001 after 1 hour to
    match the Firebase ID token lifetime. The client should refresh
    the token and reconnect.

    Args:
        websocket: Incoming WebSocket connection.
        user_id: Firebase UID claimed by the connecting client (from URL).
    """
    token = websocket.query_params.get("token")

    # --- Authentication ---
    if not token:
        await websocket.close(code=4001, reason="Missing auth token.")
        return

    try:
        claims = _verify_firebase_token(token)
        verified_uid: str = claims.get("sub", claims.get("uid", ""))
    except Exception as exc:
        await websocket.close(code=4001, reason=f"Token invalid: {exc}")
        return

    if verified_uid != user_id:
        await websocket.close(
            code=4001,
            reason="Token uid does not match the requested user_id.",
        )
        return

    await manager.connect(verified_uid, websocket)
    session_start = asyncio.get_event_loop().time()

    try:
        while True:
            # --- Session Timeout Check ---
            elapsed = asyncio.get_event_loop().time() - session_start
            if elapsed >= _MAX_SESSION_SECONDS:
                await websocket.close(
                    code=4001, reason="Session expired — please refresh your token."
                )
                break

            raw = await asyncio.wait_for(
                websocket.receive_text(),
                timeout=_MAX_SESSION_SECONDS - elapsed,
            )

            # --- Parse payload ---
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps({"error": "Payload must be valid JSON."})
                )
                continue

            receiver_id: str = payload.get("receiver_id", "")
            content: str = payload.get("content", "").strip()
            client_msg_id: str = payload.get(
                "client_msg_id", str(uuid.uuid4())
            )

            if not content or not receiver_id:
                await websocket.send_text(
                    json.dumps(
                        {"error": "receiver_id and content are required."}
                    )
                )
                continue

            # --- Route message ---
            if receiver_id.lower() in ("ai", "lexai"):
                # AI branch — RAG legal advice (lazy import avoids loading
                # torch/sentence-transformers at module import time)
                try:
                    try:
                        from app.services.ai_service import AIService
                    except ImportError:
                        from services.ai_service import AIService
                    answer, _ = await AIService.get_legal_advice(content)
                except Exception as exc:
                    logger.error("AIService error: %s", exc)
                    answer = (
                        "Sorry, an internal error occurred. "
                        "Please try again shortly."
                    )

                response_payload = {
                    "sender_id": "ai",
                    "content": answer,
                    "client_msg_id": str(uuid.uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await websocket.send_text(json.dumps(response_payload))

            else:
                # P2P branch — persist first, then route
                _persist_message(
                    sender_id=verified_uid,
                    receiver_id=receiver_id,
                    content=content,
                    client_msg_id=client_msg_id,
                )

                p2p_payload = {
                    "sender_id": verified_uid,
                    "content": content,
                    "client_msg_id": client_msg_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                delivered = await manager.send_to(receiver_id, p2p_payload)
                if not delivered:
                    # Recipient offline — message is persisted; they will
                    # retrieve it via GET /legal/chat/history on reconnect.
                    await websocket.send_text(
                        json.dumps(
                            {
                                **p2p_payload,
                                "status": "queued",
                                "note": "Recipient offline; message persisted.",
                            }
                        )
                    )
                else:
                    # Echo back delivery confirmation to the sender
                    await websocket.send_text(
                        json.dumps(
                            {**p2p_payload, "status": "delivered"}
                        )
                    )

    except WebSocketDisconnect:
        pass
    except asyncio.TimeoutError:
        # Socket timed out at the 1-hour mark
        try:
            await websocket.close(
                code=4001,
                reason="Session expired — please refresh your token.",
            )
        except Exception:
            pass
    finally:
        manager.disconnect(verified_uid)
