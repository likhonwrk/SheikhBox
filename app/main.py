from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import websockets
from app.application.services.session_service import SessionService
from app.application.services.chat_service import ChatService
import json

app = FastAPI(
    title="SheikhBox: Intelligent Conversation Agent API",
    description="A DDD-based AI agent system with sandboxed tool execution.",
    version="1.0.0"
)

session_service = SessionService()
chat_service = ChatService(session_service)

# --- Pydantic Models for API ---
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class SessionResponse(BaseModel):
    session_id: str

# --- API Endpoints ---

@app.put("/api/v1/sessions", response_model=SessionResponse, status_code=201)
async def create_session():
    session_id = await session_service.create_session()
    return {"session_id": session_id}

@app.delete("/api/v1/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str):
    await session_service.delete_session(session_id)
    return {}

@app.post("/api/v1/sessions/{session_id}/chat")
async def chat_with_session(session_id: str, request: ChatRequest):
    async def event_stream():
        async for event in chat_service.chat(session_id, request.message):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
    
    return EventSourceResponse(event_stream())

@app.websocket("/api/v1/sessions/{session_id}/vnc")
async def vnc_proxy(session_id: str, websocket: WebSocket):
    await websocket.accept(subprotocol="binary")
    try:
        sandbox = await session_service.get_session_sandbox(session_id)
        # The sandbox's _vnc_url is a ws:// URL
        vnc_url = sandbox._vnc_url 
        
        async with websockets.connect(vnc_url, subprotocols=["binary"]) as remote_ws:
            # Forward messages in both directions
            consumer_task = asyncio.create_task(
                _forward_messages(websocket, remote_ws, "client_to_server")
            )
            producer_task = asyncio.create_task(
                _forward_messages(remote_ws, websocket, "server_to_client")
            )
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

    except WebSocketDisconnect:
        print(f"Client disconnected from VNC for session {session_id}")
    except Exception as e:
        print(f"An error occurred in VNC proxy for session {session_id}: {e}")
    finally:
        if not websocket.client_state == "DISCONNECTED":
            await websocket.close()

async def _forward_messages(source: WebSocket, dest: WebSocket, direction: str):
    while True:
        try:
            message = await source.receive_bytes()
            await dest.send_bytes(message)
        except (WebSocketDisconnect, websockets.exceptions.ConnectionClosed):
            print(f"Connection closed in direction: {direction}")
            break
        except Exception as e:
            print(f"Error forwarding message in {direction}: {e}")
            break

# --- Exception Handling ---
@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=404,
        content={"code": 404, "msg": str(exc), "data": None},
    )
