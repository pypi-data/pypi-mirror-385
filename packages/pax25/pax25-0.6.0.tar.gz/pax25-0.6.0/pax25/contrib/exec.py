import asyncio
import contextlib
import logging
import os
from asyncio import StreamReader, StreamWriter, subprocess
from asyncio.subprocess import Process
from typing import TypedDict

from pax25 import Application
from pax25.services.connection.connection import Connection

logger = logging.getLogger()


class ExecSettings(TypedDict):
    """
    Settings for the exec app.
    """

    path: str
    args: list[str]
    working_directory: str
    environment: dict[str, str]


class ManagedProcess:
    """
    Process manager class that handles starting and communicating with the process, and
    then sends any data to the Exec app.
    """

    stdin: StreamWriter | None
    stdout: StreamReader | None
    proc: Process | None

    def __init__(self, connection: Connection, settings: ExecSettings):
        self.stdin = None
        self.stdout = None
        self.proc = None
        self.prebuffer = b""
        self.connection = connection
        self.settings = settings
        self._initialization = asyncio.ensure_future(self.initialize_process())

    def gen_environment(self) -> dict[str, str]:
        """
        Generate environment variables for the subprocess we'll be creating.
        """
        environment = {
            "PAX25_FIRST_PARTY": str(self.connection.first_party),
            "PAX25_SECOND_PARTY": str(self.connection.second_party),
            "PAX25_INTERFACE_NAME": self.connection.interface.name,
            "PAX25_INTERFACE_TYPE": self.connection.interface.type,
        }
        environment.update(self.settings["environment"])
        return environment

    def close(self) -> None:
        if self.proc:
            with contextlib.suppress(ProcessLookupError):
                self.proc.terminate()

    async def initialize_process(self) -> None:
        """
        Initialize the subprocess that will handle the connection, and start the
        read loop.
        """
        try:
            self.proc = await asyncio.create_subprocess_exec(
                self.settings["path"],
                *self.settings["args"],
                cwd=self.settings["working_directory"] or os.getcwd(),
                stderr=subprocess.STDOUT,
                stdout=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                limit=1,
                env=self.gen_environment(),
            )
            self.stdin, self.stdout = self.proc.stdin, self.proc.stdout
            assert self.stdin
            assert self.stdout
            self.stdin.write(self.prebuffer)
            await self.stdin.drain()
            self.prebuffer = b""
            while self.proc.returncode is None:
                data = await self.stdout.read(1000)
                if data == b"":
                    break
                self.connection.send_bytes(data)
            # Send any remainder.
            self.connection.send_bytes(await self.stdout.read())
        except Exception as err:
            logger.exception(err)
        self.connection.disconnect()

    def send_bytes(self, data: bytes) -> None:
        """
        Write to the external process, or prebuffer if we're still launching.
        """
        if self.stdin is None:
            self.prebuffer += data
            return
        try:
            self.stdin.write(data)
        except OSError:
            self.connection.disconnect()
        except Exception as err:
            logger.exception(err)
            self.connection.disconnect()


class Exec(Application[ExecSettings]):
    """
    The Exec app is a shim application that allows you to make any connection launch
    an executable and redirect its input and output to the connected client.
    """

    connections: dict[Connection, ManagedProcess]
    manager_class = ManagedProcess

    def setup(self) -> None:
        self.connections = {}

    def on_startup(self, connection: "Connection") -> None:
        self.connections[connection] = ManagedProcess(connection, self.settings)

    def on_message(
        self,
        connection: "Connection",
        message: str,
    ) -> None:
        self.connections[connection].send_bytes((message + os.linesep).encode("utf-8"))

    def on_shutdown(self, connection: "Connection") -> None:
        if connection in self.connections:
            self.connections[connection].close()
            del self.connections[connection]
