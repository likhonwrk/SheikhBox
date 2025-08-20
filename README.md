# SheikhBox: Intelligent Conversation Agent API

An intelligent conversation agent system based on FastAPI and the Gemini API. The backend adopts Domain-Driven Design (DDD) architecture, supporting intelligent dialogue, file operations, Shell command execution, and browser automation within a secure sandbox environment.

## Core Features

- **Session Management**: Create and manage persistent conversation session instances.
- **Real-time Conversation**: Implements real-time, streaming conversation through Server-Sent Events (SSE).
- **Tool Invocation**: Supports a variety of tool calls, including:
    - Browser automation operations (using Playwright)
    - Shell command execution and viewing
    - File read/write/search operations
    - Web search integration
- **Sandbox Environment**: Uses Docker containers to provide isolated and secure execution environments for each session.
- **VNC Visualization**: Supports remote viewing of the sandbox desktop environment via a WebSocket connection.

## API Specification (v1)

**Base URL**: `/api/v1`

### 1. Create Session

- **Endpoint**: `PUT /api/v1/sessions`
- **Description**: Creates a new conversation session and its associated sandbox environment.
- **Request Body**: None
- **Response**:
  ```json
  {
    "code": 0,
    "msg": "success",
    "data": {
      "session_id": "string"
    }
  }
  ```

### 2. Get Session

- **Endpoint**: `GET /api/v1/sessions/{session_id}`
- **Description**: Retrieves session information, including conversation history.
- **Path Parameters**:
    - `session_id`: The ID of the session.
- **Response**:
  ```json
  {
    "code": 0,
    "msg": "success",
    "data": {
      "session_id": "string",
      "title": "string",
      "events": []
    }
  }
  ```

### 3. List All Sessions

- **Endpoint**: `GET /api/v1/sessions`
- **Description**: Gets a list of all active and past sessions.
- **Response**:
  ```json
  {
    "code": 0,
    "msg": "success",
    "data": {
      "sessions": [
        {
          "session_id": "string",
          "title": "string",
          "latest_message": "string",
          "latest_message_at": 1234567890,
          "status": "string",
          "unread_message_count": 0
        }
      ]
    }
  }
  ```

### 4. Delete Session

- **Endpoint**: `DELETE /api/v1/sessions/{session_id}`
- **Description**: Deletes a session and cleans up its sandbox environment.
- **Path Parameters**:
    - `session_id`: The ID of the session.
- **Response**:
  ```json
  {
    "code": 0,
    "msg": "success",
    "data": null
  }
  ```

### 5. Stop Session

- **Endpoint**: `POST /api/v1/sessions/{session_id}/stop`
- **Description**: Stops any active, long-running tasks within a session.
- **Path Parameters**:
    - `session_id`: The ID of the session.
- **Response**:
  ```json
  {
    "code": 0,
    "msg": "success",
    "data": null
  }
  ```

### 6. Chat with Session

- **Endpoint**: `POST /api/v1/sessions/{session_id}/chat`
- **Description**: Sends a message to the session and receives a streaming response.
- **Path Parameters**:
    - `session_id`: The ID of the session.
- **Request Body**:
  ```json
  {
    "message": "User message content",
    "timestamp": 1234567890,
    "event_id": "optional event ID"
  }
  ```
- **Response**: A Server-Sent Events (SSE) stream with the following event types:
    - `message`: Text message from the assistant.
    - `title`: Session title update.
    - `plan`: The agent's execution plan.
    - `step`: Status update for a step in the plan.
    - `tool`: Information about a tool invocation.
    - `error`: Error information.
    - `done`: Conversation completion signal.

### 7. VNC Connection

- **Endpoint**: `WebSocket /api/v1/sessions/{session_id}/vnc`
- **Description**: Establishes a VNC WebSocket connection to the session's sandbox environment for remote viewing.
- **Path Parameters**:
    - `session_id`: The ID of the session.
- **Protocol**: WebSocket (binary mode)
- **Subprotocol**: `binary`

### Error Handling

All APIs return responses in a unified format when errors occur:

```json
{
  "code": 400,
  "msg": "Error description",
  "data": null
}
```

**Common error codes**:
- `400`: Bad Request (e.g., parameter error)
- `404`: Not Found (e.g., session not found)
- `500`: Internal Server Error
