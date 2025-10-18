"""API-based remote workspace implementation using runtime API."""

import uuid
from typing import Any
from urllib.request import urlopen

import httpx
import tenacity
from pydantic import Field, PrivateAttr

from openhands.sdk.logger import get_logger
from openhands.sdk.workspace.remote.base import RemoteWorkspace


logger = get_logger(__name__)


class APIRemoteWorkspace(RemoteWorkspace):
    """Remote workspace using OpenHands runtime API.

    Runtime API: https://runtime.all-hands.dev/

    Example:
        workspace = APIRemoteWorkspace(
            runtime_api_url="https://runtime.eval.all-hands.dev",
            runtime_api_key="your-api-key",
            server_image="ghcr.io/all-hands-ai/agent-server:lastest-python",
        )
    """  # noqa: E501

    # Parent fields
    working_dir: str = Field(
        default="/workspace",
        description="Working directory inside the remote workspace",
    )
    host: str = Field(
        default="undefined",
        description="The remote host URL for the workspace."
        " It will be set to the runtime URL after connecting.",
    )

    # Runtime API fields
    runtime_api_url: str = Field(description="Base URL of the runtime API")
    runtime_api_key: str = Field(description="API key for authentication")
    server_image: str = Field(
        description="Container image for the agent server. "
        "It must be a public image or in a registry accessible by runtime API."
    )
    session_id: str | None = Field(
        default_factory=lambda: f"agent-server-{uuid.uuid4()}",
        description="Session ID (auto-generated if None)",
    )
    resource_factor: int = Field(
        default=1, description="Resource scaling (1, 2, 4, or 8)"
    )
    runtime_class: str | None = Field(
        default="sysbox", description="Runtime class (e.g., 'sysbox')"
    )
    init_timeout: float = Field(
        default=300.0, description="Runtime init timeout (seconds)"
    )
    api_timeout: float = Field(
        default=60.0, description="API request timeout (seconds)"
    )
    keep_alive: bool = Field(default=False, description="Keep runtime alive on cleanup")
    pause_on_close: bool = Field(
        default=False, description="Pause instead of stop on cleanup"
    )

    _runtime_id: str | None = PrivateAttr(default=None)
    _runtime_url: str | None = PrivateAttr(default=None)
    _session_api_key: str | None = PrivateAttr(default=None)

    def model_post_init(self, context: Any) -> None:
        """Set up the remote runtime and initialize the workspace."""
        if self.resource_factor not in [1, 2, 4, 8]:
            raise ValueError(
                f"resource_factor must be 1, 2, 4, or 8, got {self.resource_factor}"
            )

        self.runtime_api_url = self.runtime_api_url.rstrip("/")

        try:
            self._start_or_attach_to_runtime()
            super().model_post_init(context)
        except Exception:
            self.cleanup()
            raise

    def _start_or_attach_to_runtime(self) -> None:
        """Start or attach to an existing runtime."""
        if not self._check_existing_runtime():
            self._start_runtime()

        assert self._runtime_id and self._runtime_url, "Runtime ID/URL not set"
        self._wait_until_runtime_alive()
        logger.info(f"Runtime ready at {self._runtime_url}")
        self.host = self._runtime_url.rstrip("/")
        self.api_key: str = self._session_api_key

    def _check_existing_runtime(self) -> bool:
        """Check if there's an existing runtime for this session."""
        try:
            resp = self._send_api_request(
                "GET", f"{self.runtime_api_url}/sessions/{self.session_id}"
            )
            data = resp.json()
            status = data.get("status")
            logger.info(f"Runtime status: {status}")

            if status in ("running", "paused"):
                self._parse_runtime_response(resp)
                if status == "paused":
                    try:
                        self._resume_runtime()
                    except Exception as e:
                        logger.error(f"Resume failed: {e}")
                        return False
                return True
            return False
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise

    def _start_runtime(self) -> None:
        """Start a new runtime."""
        # For binary target, use the standalone binary
        payload: dict[str, Any] = {
            "image": self.server_image,
            "command": "/usr/local/bin/openhands-agent-server --port 60000",
            "working_dir": "/",  # Match Dockerfile WORKDIR
            "environment": {},
            "session_id": self.session_id,
            "run_as_user": 10001,
            "fs_group": 10001,
            # "environment": {"DEBUG": "true"},
        }

        if self.runtime_class:
            payload["runtime_class"] = self.runtime_class
        if self.resource_factor != 1:
            payload["resource_factor"] = self.resource_factor

        logger.info(f"Starting runtime with {self.server_image}")
        logger.info(f"Payload: {payload}")
        resp = self._send_api_request(
            "POST",
            f"{self.runtime_api_url}/start",
            json=payload,
            timeout=self.init_timeout,
        )
        self._parse_runtime_response(resp)
        logger.info(f"Runtime {self._runtime_id} at {self._runtime_url}")

    def _resume_runtime(self) -> None:
        """Resume a paused runtime."""
        resp = self._send_api_request(
            "POST",
            f"{self.runtime_api_url}/resume",
            json={"runtime_id": self._runtime_id},
            timeout=self.init_timeout,
        )
        self._parse_runtime_response(resp)

    def _parse_runtime_response(self, response: httpx.Response) -> None:
        """Parse the runtime response and extract connection info."""
        data = response.json()
        self._runtime_id = data.get("runtime_id") or data.get("id")
        self._runtime_url = data.get("url")
        self._session_api_key = data.get("session_api_key")
        if not self._runtime_id or not self._runtime_url:
            raise ValueError(f"Invalid runtime response: {data}")

    @tenacity.retry(
        stop=tenacity.stop_after_delay(300),
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
        retry=tenacity.retry_if_exception_type(RuntimeError),
        reraise=True,
    )
    def _wait_until_runtime_alive(self) -> None:
        """Wait until the runtime becomes alive and responsive."""
        logger.info("Waiting for runtime to become alive...")

        resp = self._send_api_request(
            "GET", f"{self.runtime_api_url}/sessions/{self.session_id}"
        )
        data = resp.json()
        pod_status = data.get("pod_status", "").lower()
        logger.info(f"Pod status: {pod_status}")

        # Log additional details for debugging
        if pod_status == "pending":
            container_statuses = data.get("container_statuses", [])
            events = data.get("events", [])
            if container_statuses:
                logger.warning(f"Container statuses: {container_statuses}")
            if events:
                logger.warning(f"Pod events: {events}")
            logger.debug(f"Full response: {data}")

        restart_count = data.get("restart_count", 0)
        if restart_count > 0:
            restart_reasons = data.get("restart_reasons", [])
            logger.warning(f"Pod restarts: {restart_count}, reasons: {restart_reasons}")

        # Handle different pod states
        if pod_status == "ready":
            # Pod is ready, check health endpoint
            health_url = f"{self._runtime_url}/health"
            logger.info(f"Checking health at: {health_url}")
            try:
                with urlopen(health_url, timeout=5.0) as resp:
                    status = getattr(resp, "status", 200)
                    logger.info(f"Health check response: {status}")
                    if 200 <= status < 300:
                        logger.info("Runtime is alive!")
                        return
                    raise RuntimeError(f"Health check failed with status: {status}")
            except Exception as e:
                logger.warning(f"Health check failed: {e}")
                raise RuntimeError(f"Runtime /health failed: {e}")
        elif pod_status in ("not found", "pending", "running"):
            # Transient states - continue retrying
            logger.debug(f"Runtime not yet ready. Status: {pod_status}")
            raise RuntimeError(f"Runtime not yet ready (status: {pod_status})")
        elif pod_status in ("failed", "unknown", "crashloopbackoff"):
            # Terminal failure states
            pod_logs = data.get("pod_logs", "")
            error_msg = f"Runtime failed (status: {pod_status})"
            if pod_logs:
                logger.error(f"Pod logs: {pod_logs}")
                error_msg += f"\nPod logs: {pod_logs}"
            if pod_status == "crashloopbackoff":
                error_msg = (
                    "Runtime crashed and is restarting (possibly OOM). Try again."
                )
            raise ValueError(error_msg)
        else:
            # Unknown status - log and retry
            logger.warning(f"Unknown pod status: {pod_status}, full response: {data}")
            raise RuntimeError(f"Unknown pod status: {pod_status}")

    def _send_api_request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Send an API request with error handling."""
        logger.debug(f"Sending {method} request to {url}")
        logger.debug(f"Client headers: {self._headers}")
        response = self.client.request(method, url, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.debug(f"Request headers: {response.request.headers}")
            try:
                error_detail = response.json()
                logger.info(f"API request failed: {error_detail}")
            except Exception:
                logger.info(f"API request failed: {response.text}")
            raise
        return response

    def cleanup(self) -> None:
        """Clean up the remote runtime."""
        if not self._runtime_id:
            return

        try:
            if self.keep_alive:
                return

            action = "pause" if self.pause_on_close else "stop"
            logger.info(f"{action.capitalize()}ing runtime {self._runtime_id}")
            self._send_api_request(
                "POST",
                f"{self.runtime_api_url}/{action}",
                json={"runtime_id": self._runtime_id},
                timeout=30.0,
            )
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        finally:
            self._runtime_id = None
            self._runtime_url = None
            self._session_api_key = None
            try:
                self.client.close()
            except Exception:
                pass

    def __del__(self) -> None:
        self.cleanup()

    def __enter__(self) -> "APIRemoteWorkspace":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.cleanup()
