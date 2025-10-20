"""
Types for the command line app.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, TypedDict

from pax25.interfaces.loopback import LoopbackInterface
from pax25.services.connection.connection import Connection
from pax25.utils import EnumReprMixin

if TYPE_CHECKING:  # pragma: no cover
    from pax25.contrib.command.command import CommandLine


class CommandSettings(TypedDict, total=False):
    """
    Settings for the command line application.
    """

    # Whether to automatically drop a user after they've disconnected from a remote.
    # Used mostly for testing, but may also work when acting as a node in the future.
    auto_quit: bool


class RemoteConnectionState(EnumReprMixin, Enum):
    """
    Enum for remote connection state.
    """

    FOREGROUND = 0
    BACKGROUND = 1


@dataclass()
class CommandLineState:
    """
    Keeps track of the current state for connected sessions.
    """

    remote_state: RemoteConnectionState = RemoteConnectionState.BACKGROUND
    remote_buffer: bytearray = field(default_factory=bytearray)
    connection: Connection | None = None
    # Used in loopbacks.
    dest_connection: Connection | None = None
    loopback_interface: LoopbackInterface | None = None


@dataclass()
class ShimSettings:
    """
    Settings for the shim application.
    """

    proxy_connection: Connection
    upstream_application: "CommandLine"
