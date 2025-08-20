from app.domain.external.sandbox import Sandbox
from app.infrastructure.external.sandbox.docker_sandbox import DockerSandbox

class SessionService:
    """
    Service for managing conversation sessions.
    """

    # In a real application, you would have a repository to store session state.
    # For this example, we'll just manage the sandbox.
    _active_sandboxes = {}

    async def create_session(self) -> str:
        """
        Creates a new session, which includes a new sandbox.
        Returns the session ID (which is the sandbox ID in this case).
        """
        sandbox = await DockerSandbox.create()
        self._active_sandboxes[sandbox.id] = sandbox
        return sandbox.id

    async def get_session_sandbox(self, session_id: str) -> Sandbox:
        """
        Gets the sandbox associated with a session.
        """
        if session_id in self._active_sandboxes:
            return self._active_sandboxes[session_id]
        
        # In a real app, you might try to reconnect to an existing container
        try:
            sandbox = await DockerSandbox.get(session_id)
            self._active_sandboxes[session_id] = sandbox
            return sandbox
        except Exception:
            raise ValueError("Session not found")

    async def delete_session(self, session_id: str):
        """
        Deletes a session and its associated sandbox.
        """
        if session_id in self._active_sandboxes:
            sandbox = self._active_sandboxes.pop(session_id)
            await sandbox.destroy()
        else:
            # Try to delete even if not in active memory
            try:
                sandbox = await DockerSandbox.get(session_id)
                await sandbox.destroy()
            except Exception:
                # Session might have already been deleted
                pass
