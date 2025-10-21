"""Docker-based remote workspace implementation."""

import os
import subprocess
import sys
import threading
import time
import uuid
from typing import Any
from urllib.request import urlopen

from pydantic import Field, PrivateAttr, model_validator

from openhands.agent_server.docker.build import (
    BuildOptions,
    PlatformType,
    TargetType,
    build,
)
from openhands.sdk.logger import get_logger
from openhands.sdk.utils.command import execute_command
from openhands.sdk.workspace import RemoteWorkspace


logger = get_logger(__name__)


def check_port_available(port: int) -> bool:
    """Check if a port is available for binding."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", port))
        return True
    except OSError:
        time.sleep(0.1)
        return False
    finally:
        sock.close()


def find_available_tcp_port(
    min_port: int = 30000, max_port: int = 39999, max_attempts: int = 50
) -> int:
    """Find an available TCP port in a specified range."""
    import random

    rng = random.SystemRandom()
    ports = list(range(min_port, max_port + 1))
    rng.shuffle(ports)

    for port in ports[:max_attempts]:
        if check_port_available(port):
            return port
    return -1


class DockerWorkspace(RemoteWorkspace):
    """Remote workspace that sets up and manages a Docker container.

    This workspace creates a Docker container running the OpenHands agent server,
    waits for it to become healthy, and then provides remote workspace operations
    through the container's HTTP API.

    Example:
        with DockerWorkspace(base_image="python:3.12") as workspace:
            result = workspace.execute_command("ls -la")
    """

    # Override parent fields with defaults
    working_dir: str = Field(
        default="/workspace",
        description="Working directory inside the container.",
    )
    host: str = Field(
        default="",
        description=("Remote host URL (set automatically during container startup)."),
    )

    # Docker-specific configuration
    base_image: str | None = Field(
        default=None,
        description="Base Docker image to use for the agent server container. "
        "Mutually exclusive with server_image.",
    )
    server_image: str | None = Field(
        default=None,
        description=(
            "Pre-built agent server image to use. If None, builds from base_image."
            "Mutually exclusive with base_image."
        ),
    )
    host_port: int | None = Field(
        default=None,
        description="Port to bind the container to. If None, finds available port.",
    )
    forward_env: list[str] = Field(
        default_factory=lambda: ["DEBUG"],
        description="Environment variables to forward to the container.",
    )
    mount_dir: str | None = Field(
        default=None,
        description="Optional host directory to mount into the container.",
    )
    detach_logs: bool = Field(
        default=True, description="Whether to stream Docker logs in background."
    )
    target: TargetType = Field(
        default="source", description="Build target for the Docker image."
    )
    platform: PlatformType = Field(
        default="linux/amd64", description="Platform for the Docker image."
    )
    extra_ports: bool = Field(
        default=False,
        description="Whether to expose additional ports (VSCode, VNC).",
    )

    _container_id: str | None = PrivateAttr(default=None)
    _logs_thread: threading.Thread | None = PrivateAttr(default=None)
    _stop_logs: threading.Event = PrivateAttr(default_factory=threading.Event)
    _image: str = PrivateAttr()

    @model_validator(mode="after")
    def _validate_images(self):
        """Ensure exactly one of base_image or server_image is provided; cache it."""
        if (self.base_image is None) == (self.server_image is None):
            raise ValueError(
                "Exactly one of 'base_image' or 'server_image' must be set."
            )
        return self

    def model_post_init(self, context: Any) -> None:
        """Set up the Docker container and initialize the remote workspace."""
        # Determine port
        if self.host_port is None:
            self.host_port = find_available_tcp_port()
        else:
            self.host_port = int(self.host_port)

        if not check_port_available(self.host_port):
            raise RuntimeError(f"Port {self.host_port} is not available")

        if self.extra_ports:
            if not check_port_available(self.host_port + 1):
                raise RuntimeError(
                    f"Port {self.host_port + 1} is not available for VSCode"
                )
            if not check_port_available(self.host_port + 2):
                raise RuntimeError(
                    f"Port {self.host_port + 2} is not available for VNC"
                )

        # Ensure docker is available
        docker_ver = execute_command(["docker", "version"]).returncode
        if docker_ver != 0:
            raise RuntimeError(
                "Docker is not available. Please install and start "
                "Docker Desktop/daemon."
            )

        # Build image if needed

        if self.base_image:
            if "ghcr.io/all-hands-ai/agent-server" in self.base_image:
                raise RuntimeError(
                    "base_image cannot be a pre-built agent-server image. "
                    "Use server_image=... instead."
                )
            build_opts = BuildOptions(
                base_image=self.base_image,
                target=self.target,
                platforms=[self.platform],
            )
            tags = build(opts=build_opts)
            assert tags and len(tags) > 0, "Build failed, no image tags returned"
            self._image = tags[0]

        elif self.server_image:
            self._image = self.server_image
        else:
            raise RuntimeError("Unreachable: one of base_image or server_image is set")

        # Prepare Docker run flags
        flags: list[str] = []
        for key in self.forward_env:
            if key in os.environ:
                flags += ["-e", f"{key}={os.environ[key]}"]

        if self.mount_dir:
            mount_path = "/workspace"
            flags += ["-v", f"{self.mount_dir}:{mount_path}"]
            logger.info(
                "Mounting host dir %s to container path %s",
                self.mount_dir,
                mount_path,
            )

        ports = ["-p", f"{self.host_port}:8000"]
        if self.extra_ports:
            ports += [
                "-p",
                f"{self.host_port + 1}:8001",  # VSCode
                "-p",
                f"{self.host_port + 2}:8002",  # Desktop VNC
            ]
        flags += ports

        # Run container
        run_cmd = [
            "docker",
            "run",
            "-d",
            "--platform",
            self.platform,
            "--rm",
            "--name",
            f"agent-server-{uuid.uuid4()}",
            *flags,
            self._image,
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ]
        proc = execute_command(run_cmd)
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to run docker container: {proc.stderr}")

        self._container_id = proc.stdout.strip()
        logger.info("Started container: %s", self._container_id)

        # Optionally stream logs in background
        if self.detach_logs:
            self._logs_thread = threading.Thread(
                target=self._stream_docker_logs, daemon=True
            )
            self._logs_thread.start()

        # Set host for RemoteWorkspace to use
        # The container exposes port 8000, mapped to self.host_port
        # Override parent's host initialization
        object.__setattr__(self, "host", f"http://localhost:{self.host_port}")
        object.__setattr__(self, "api_key", None)

        # Wait for container to be healthy
        self._wait_for_health()
        logger.info("Docker workspace is ready at %s", self.host)

        # Now initialize the parent RemoteWorkspace with the container URL
        super().model_post_init(context)

    def _stream_docker_logs(self) -> None:
        """Stream Docker logs to stdout in the background."""
        if not self._container_id:
            return
        try:
            p = subprocess.Popen(
                ["docker", "logs", "-f", self._container_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            if p.stdout is None:
                return
            for line in iter(p.stdout.readline, ""):
                if self._stop_logs.is_set():
                    break
                if line:
                    sys.stdout.write(f"[DOCKER] {line}")
                    sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error streaming docker logs: {e}\n")
        finally:
            try:
                self._stop_logs.set()
            except Exception:
                pass

    def _wait_for_health(self, timeout: float = 120.0) -> None:
        """Wait for the Docker container to become healthy."""
        start = time.time()
        health_url = f"http://127.0.0.1:{self.host_port}/health"

        while time.time() - start < timeout:
            try:
                with urlopen(health_url, timeout=1.0) as resp:
                    if 200 <= getattr(resp, "status", 200) < 300:
                        return
            except Exception:
                pass

            # Check if container is still running
            if self._container_id:
                ps = execute_command(
                    [
                        "docker",
                        "inspect",
                        "-f",
                        "{{.State.Running}}",
                        self._container_id,
                    ]
                )
                if ps.stdout.strip() != "true":
                    logs = execute_command(["docker", "logs", self._container_id])
                    msg = (
                        "Container stopped unexpectedly. Logs:\n"
                        f"{logs.stdout}\n{logs.stderr}"
                    )
                    raise RuntimeError(msg)
            time.sleep(1)
        raise RuntimeError("Container failed to become healthy in time")

    def __enter__(self) -> "DockerWorkspace":
        """Context manager entry - returns the workspace itself."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Context manager exit - cleans up the Docker container."""
        self.cleanup()

    def __del__(self) -> None:
        """Clean up the Docker container when the workspace is destroyed."""
        self.cleanup()

    def cleanup(self) -> None:
        """Stop and remove the Docker container."""
        if self._container_id:
            # Stop logs streaming
            self._stop_logs.set()
            if self._logs_thread and self._logs_thread.is_alive():
                self._logs_thread.join(timeout=2)

            # Stop and remove the container
            logger.info("Stopping container: %s", self._container_id)
            execute_command(["docker", "stop", self._container_id])
            self._container_id = None
