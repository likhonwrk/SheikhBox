from typing import Dict, Any, Optional, List, BinaryIO
import uuid
import httpx
import docker
import socket
import logging
import asyncio
import io
from async_lru import alru_cache
from app.domain.models.tool_result import ToolResult
from app.domain.external.sandbox import Sandbox
from app.infrastructure.external.browser.playwright_browser import PlaywrightBrowser
from app.domain.external.browser import Browser

logger = logging.getLogger(__name__)

# A placeholder for a settings object
class Settings:
    sandbox_image = "accetto/ubuntu-vnc-xfce-chromium-g3"
    sandbox_name_prefix = "sheikhbox-sandbox"
    sandbox_ttl_minutes = "60"
    sandbox_chrome_args = ""
    sandbox_https_proxy = ""
    sandbox_http_proxy = ""
    sandbox_no_proxy = ""
    sandbox_network = "bridge"
    sandbox_address = None

def get_settings():
    return Settings()

class DockerSandbox(Sandbox):
    def __init__(self, ip: str = None, container_name: str = None):
        self.client = httpx.AsyncClient(timeout=600)
        self.ip = ip
        self.base_url = f"http://{self.ip}:8080"
        self._vnc_url = f"ws://{self.ip}:5901"
        self._cdp_url = f"http://{self.ip}:9222"
        self._container_name = container_name
    
    @property
    def id(self) -> str:
        return self._container_name or "dev-sandbox"

    @staticmethod
    def _get_container_ip(container) -> str:
        network_settings = container.attrs['NetworkSettings']
        ip_address = network_settings['IPAddress']
        if not ip_address and 'Networks' in network_settings:
            networks = network_settings['Networks']
            for network_config in networks.values():
                if 'IPAddress' in network_config and network_config['IPAddress']:
                    ip_address = network_config['IPAddress']
                    break
        return ip_address

    @staticmethod
    def _create_task() -> 'DockerSandbox':
        settings = get_settings()
        container_name = f"{settings.sandbox_name_prefix}-{str(uuid.uuid4())[:8]}"
        try:
            docker_client = docker.from_env()
            container_config = {
                "image": settings.sandbox_image, "name": container_name,
                "detach": True, "remove": True,
                "environment": {
                    "VNC_PW": "password",
                    "SERVICE_TIMEOUT_MINUTES": settings.sandbox_ttl_minutes,
                },
                "ports": {'5901/tcp': None, '9222/tcp': None, '8080/tcp': None}
            }
            if settings.sandbox_network:
                container_config["network"] = settings.sandbox_network
            
            container = docker_client.containers.run(**container_config)
            container.reload()
            ip_address = DockerSandbox._get_container_ip(container)
            return DockerSandbox(ip=ip_address, container_name=container_name)
        except Exception as e:
            raise Exception(f"Failed to create Docker sandbox: {e}")

    async def destroy(self) -> bool:
        try:
            if self.client:
                await self.client.aclose()
            if self._container_name:
                docker_client = docker.from_env()
                docker_client.containers.get(self._container_name).remove(force=True)
            return True
        except Exception as e:
            logger.error(f"Failed to destroy Docker sandbox: {e}")
            return False
    
    async def get_browser(self) -> Browser:
        return PlaywrightBrowser(self._cdp_url)

    @classmethod
    async def create(cls) -> Sandbox:
        return await asyncio.to_thread(cls._create_task)
    
    @classmethod
    async def get(cls, id: str) -> Sandbox:
        docker_client = docker.from_env()
        container = docker_client.containers.get(id)
        container.reload()
        ip_address = cls._get_container_ip(container)
        return DockerSandbox(ip=ip_address, container_name=id)

    # --- Placeholder methods for other sandbox interactions ---
    async def exec_command(self, session_id: str, exec_dir: str, command: str) -> ToolResult:
        return ToolResult(success=False, message="Not implemented")

    async def file_write(self, file: str, content: str) -> ToolResult:
        return ToolResult(success=False, message="Not implemented")

    async def file_read(self, file: str) -> ToolResult:
        return ToolResult(success=False, message="Not implemented")
