"""
Command line interface for controlling Pax25.
"""

import asyncio
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from typing import cast
from uuid import uuid4

from pax25 import Application, Station
from pax25 import __version__ as pax25_version
from pax25.applications.help import Help
from pax25.applications.parsers import (
    ParseError,
    no_arguments,
    pull_segment,
)
from pax25.applications.router import (
    CommandContext,
    CommandRouter,
    CommandSpec,
    ParserSpec,
)
from pax25.applications.utils import send_message
from pax25.ax25.address import Address
from pax25.ax25.constants import AX25_ENDIAN, AX25_REPEATER_MAX
from pax25.ax25.frame import Frame
from pax25.ax25.utils import roll_back_ssid
from pax25.contrib.command.commands.admin import (
    build_load_command,
    build_name_command,
    build_save_command,
    build_save_file_command,
    build_shutdown_command,
)
from pax25.contrib.command.commands.utilities import (
    build_ports_command,
    build_whoami_command,
)
from pax25.contrib.command.shim import ShimApplication
from pax25.contrib.command.types import (
    CommandLineState,
    CommandSettings,
    RemoteConnectionState,
    ShimSettings,
)
from pax25.interfaces import FileInterface, Interface
from pax25.interfaces.loopback import LoopbackInterface
from pax25.services.connection.connection import (
    Connection,
    ConnectionStatus,
    connection_key,
)
from pax25.types import Version
from pax25.utils import gateways_for


def default_command_line_settings() -> CommandSettings:
    """
    Generate default settings for the command line application.
    """
    return {"auto_quit": False}


def digipeaters_from_string(string: str) -> tuple[Address, ...]:
    """
    Given a string like 'via SOME-1,THING-2,WAT-3', determine digipeaters.
    """
    string = string.strip()
    if not string:
        return tuple()
    try:
        via, *args = string.split(maxsplit=1)
        if not via.lower() == "via" or not args:
            raise ValueError
    except ValueError as err:
        raise ValueError(
            "Digipeater list broken. Try something like 'via NAME-1,NAME-2'."
        ) from err
    string = args[0]
    addresses = tuple(
        Address.from_string(raw_address.strip()) for raw_address in string.split(",")
    )
    if len(addresses) > AX25_REPEATER_MAX:
        raise ValueError(f"Too many digipeaters. Max is {AX25_REPEATER_MAX}.")
    return addresses


def get_indexed_gateway(station: Station, index: int) -> Interface:
    """
    Wrapper for get_nth_gateway that re-raises an IndexError as a parsing error.
    """
    try:
        return station.get_nth_gateway(index)
    except IndexError as err:
        raise ParseError(str(err)) from err


@dataclass(kw_only=True, frozen=True)
class MakeConnectionSpec:
    """
    Used by the connection parser to pass around distilled arguments.
    """

    destination: Address
    digipeaters: tuple[Address, ...]
    interface: Interface
    loopback: bool


def create_connection_parser(
    station: Station,
) -> Callable[[ParserSpec], MakeConnectionSpec]:
    """
    Generate a parser for the connection commands. Has to be generated since the
    available interfaces/ports are station-specific.
    """

    def connection_parser(spec: ParserSpec) -> MakeConnectionSpec:
        raw_args = spec.args.strip()
        if not raw_args:
            raise ParseError("Need station address.")

        explicit_interface = False
        proposed_interface: Interface | None = None
        interface: Interface | None = None
        loopback = False
        first_arg, remainder = pull_segment(raw_args)
        # First arg can be either a port number/alias, or the destination station.
        # If no port/alias is specified, then it grabs the default gateway (the first
        # registered interface where gateway is set to True)
        try:
            port_number = int(first_arg)
            proposed_interface = get_indexed_gateway(station, port_number)
            raw_destination, remainder = pull_segment(remainder)
            explicit_interface = True
        except ValueError:
            if first_arg in station.interfaces:
                proposed_interface = station.interfaces[first_arg]
                raw_destination, remainder = pull_segment(remainder)
            else:
                with suppress(ParseError):
                    proposed_interface = get_indexed_gateway(station, 1)
                raw_destination = first_arg
        try:
            destination = Address.from_string(raw_destination)
        except ValueError as err:
            raise ParseError(str(err)) from err
        if remainder:
            try:
                digipeaters = digipeaters_from_string(remainder)
            except ValueError as err:
                raise ParseError(str(err)) from err
        else:
            digipeaters = tuple()
        if not explicit_interface:
            try:
                application = station.connection.app_for(
                    spec.connection.interface,
                    destination,
                )
                if application == spec.connection.application:
                    # Don't allow connecting back to the current application to
                    # avoid infinite internal traversal.
                    raise ParseError(
                        "Cowardly refusing to connect to the current application "
                        "from the current application."
                    )
                interface = spec.connection.interface
                loopback = True
            except KeyError:
                pass
        if not interface:
            if proposed_interface is not None:
                interface = proposed_interface
            else:
                raise ParseError(
                    "No gateways available, or unrecognized internal address."
                )
        return MakeConnectionSpec(
            destination=destination,
            digipeaters=digipeaters,
            interface=interface,
            loopback=loopback,
        )

    return connection_parser


class CommandLine(Application[CommandSettings]):
    """
    Command line application. Used to handle things like connecting to other nodes
    or changing settings at runtime.
    """

    connections: dict[Connection, CommandLineState]
    frame_log: list[Frame]
    version = Version(major=0, minor=4, patch=0)
    version_string = (
        f"[PAX25-CLI-{version['major']}.{version['minor']}.{version['patch']}]"
    )
    # Used in the station ID beacon. The command line app also acts as the node app.
    short_name = "N"
    auto_quit: bool
    router: CommandRouter

    def setup(self) -> None:
        """
        Initial setup.
        """
        self.connections = {}
        settings = default_command_line_settings()
        settings.update(self.settings or {})
        self.settings = settings
        self.auto_quit = settings["auto_quit"]
        # Need to match all frames when monitoring.
        self.station.monitor.add_listener("cmd_monitor", self.frame_listener)
        self.router = CommandRouter(post_command_func=self.send_prompt)
        self.admin_router = CommandRouter(post_command_func=self.send_prompt)
        self.router.add(Help(self.router).spec)
        self.admin_router.add(Help(self.admin_router).spec)
        commands = (
            CommandSpec(
                command="apps",
                help="\r".join(
                    [
                        "Application lister. Shows all available applications you can "
                        "connect to on the local station, with addresses and info.",
                    ]
                ),
                parser=no_arguments,
                function=self.list_applications,
            ),
            CommandSpec(
                command="connect",
                help="\r".join(
                    [
                        "Use connect to connect to an outbound station. Examples:",
                        "c FOXBOX            # Connect to a station named FOXBOX, by "
                        "default on SSID 0",
                        "c KW6FOX-3          # Connect to SSID 3 on a station named "
                        "KW6FOX",
                        "c KW6FOX-2 via BOOP # Connect to KW6FOX-2 through an "
                        "intermediary station named BOOP",
                        "c 2 KW6FOX-2 via BOOP # Use port 2 to connect to KW6FOX "
                        "through an intermediary station named BOOP",
                        "",
                        "If no port is specified, checks local application "
                        "addresses. If not an internal address, uses port 1.",
                        "See also: PORTS",
                    ]
                ),
                parser=create_connection_parser(self.station),
                function=self.connect,
            ),
            CommandSpec(
                command="discon",
                # Full name is too big for command listing, so making it an alias.
                aliases=("disconnect",),
                help="Drops remote connection, if there is one.",
                parser=no_arguments,
                function=self.disconnect_remote,
            ),
            build_ports_command(self.station),
            CommandSpec(
                command="foreground",
                help="Returns you to the remote connected session, "
                "if one has been backgrounded.",
                parser=no_arguments,
                function=self.foreground_connection,
                aliases=("fg", "k"),
            ),
            build_whoami_command(),
            CommandSpec(
                command="quit",
                help="Closes the session.",
                aliases=("bye",),
                parser=no_arguments,
                function=self.quit,
            ),
            self.station.monitor.command,
        )
        self.router.add(*commands)
        self.admin_router.add(*commands)
        self.admin_router.add(
            build_shutdown_command(self.station),
            build_save_command(self.station),
            build_load_command(self.station),
            build_save_file_command(self.station),
            build_name_command(self.station),
        )

    def prompt_text(self, connection: Connection) -> str:
        """
        Generates the prompt text for the current connection. We serve slightly
        different prompt texts depending on whether this is a superuser connection
        or not.
        """
        if connection.is_admin:
            return "cmd:"
        else:
            return "ENTER COMMAND: B,C,J or Help ?\r"

    def send_prompt(self, connection: Connection) -> None:
        """
        Send the command prompt.
        """
        state = self.connections.get(connection)
        if not state:
            return
        if state.remote_state == RemoteConnectionState.FOREGROUND:
            return
        send_message(connection, self.prompt_text(connection), append_newline=False)

    def frame_listener(self, frame: Frame, _interface: Interface) -> bool:
        """
        Frame listener. Subscribes to the monitoring service and consumes frames in
        real time if there's a suitable, connected user.
        """
        for key, value in self.connections.items():
            if key.is_admin and isinstance(key.interface, FileInterface):  # noqa: SIM102
                if not (
                    value.connection or self.connection_state_table[key]["command"]
                ):
                    # Send any outstanding.
                    self.dump_logs_to_connection(key)
                    send_message(key, str(frame))
                    return True
        return False

    def dump_logs_to_connection(self, connection: Connection) -> None:
        """
        Send every log to the connection specified. Used when we disconnect and want
        to see what happened in the interim.
        """
        if not connection.is_admin and isinstance(connection.interface, FileInterface):
            return
        logs = self.station.monitor.consume_logs()
        if not logs:
            return
        prefix = len(gateways_for(self.station)) > 1
        for logged_frame in logs:
            frame_string = f"{logged_frame.port.number}:" if prefix else ""
            frame_string += str(logged_frame.frame)
            send_message(connection, frame_string)

    def on_proxy_bytes(self, connection: Connection, message: bytes) -> None:
        """
        Called by the shim application to indicate that we need to send bytes downstream
        to the connecting station.
        """
        state = self.connections[connection]
        if state.remote_state == RemoteConnectionState.BACKGROUND:
            state.remote_buffer.extend(message)
            return
        connection.send_bytes(message)

    def list_applications(
        self,
        connection: Connection,
        _context: CommandContext[None],
    ) -> None:
        """
        Lists out all internal applications available to the user.
        """
        apps = self.station.connection.application_map.get(
            connection.interface.name, {}
        )
        results = [
            f"{key}: {value.name}" for key, value in apps.items() if value != self
        ]
        send_message(connection, "\r".join(results))

    def disconnect_remote(
        self,
        connection: Connection,
        _context: CommandContext[None],
    ) -> None:
        """
        Disconnects from the remote station manually.
        """
        state = self.connections[connection]
        if not state.connection:
            send_message(connection, "Not connected. Can't disconnect.")
            return
        state.connection.disconnect()

    def on_proxy_killed(
        self,
        connection: Connection,
        jump_connection: Connection,
    ) -> None:
        """
        Called by the shim application to indicate that the connection has been killed.
        """
        if connection in self.connections:
            state = self.connections[connection]
            state.connection = None
            if state.dest_connection:
                state.dest_connection.disconnect()
            if state.loopback_interface:
                asyncio.ensure_future(state.loopback_interface.shutdown())
            self.dump_connection_buffer(connection)
            state.remote_state = RemoteConnectionState.BACKGROUND
        send_message(
            connection, f"*** Disconnected from {jump_connection.second_party}"
        )
        self.dump_logs_to_connection(connection)
        if self.auto_quit:
            connection.disconnect()

    def set_up_connection(
        self,
        *,
        source_connection: Connection,
        destination: Address,
        interface: Interface,
        digipeaters: tuple[Address, ...],
        loopback: bool,
    ) -> None:
        """
        Set up an outbound connection to route the user through.
        """
        state = self.connections[source_connection]
        if state.connection:
            send_message(
                source_connection,
                "You already have an active outbound connection. Use the 'disconnect' "
                "command to close out that connection before starting a new one.",
            )
            return
        if source_connection.first_party == source_connection.second_party:
            # Internal connection. No need to cycle the SSID.
            source = source_connection.first_party
        else:
            source = roll_back_ssid(source_connection.first_party)
        key = connection_key(source, destination, interface)
        if key in self.station.connection.table:
            send_message(source_connection, "Route busy. Try again later.")
            return
        send_message(source_connection, f"Connecting to {destination}...")
        shim_application = ShimApplication(
            name=f"(Shim for {key})",
            station=self.station,
            settings=ShimSettings(
                proxy_connection=source_connection, upstream_application=self
            ),
        )
        dest_connection: Connection | None = None
        loopback_interface: LoopbackInterface | None = None
        if loopback:
            loopback_interface = LoopbackInterface.install(
                self.station,
                name=f"__loopback-{uuid4()}",
                settings={"connection": source_connection},
            )

            def dest_handle_frame(frame: Frame) -> None:
                assert loopback_interface
                local_connection = cast(Connection, dest_connection)
                local_connection.inbound_frame(frame, loopback_interface)

            def source_handle_frame(frame: Frame) -> None:
                assert loopback_interface
                connection.inbound_frame(frame, loopback_interface)

            source_send_frame = loopback_interface.initialize_first_party(
                source_handle_frame,
            )
            dest_send_frame = loopback_interface.initialize_second_party(
                dest_handle_frame,
            )
            application = self.station.connection.app_for(interface, destination)
            dest_connection = Connection(
                station=self.station,
                first_party=source,
                is_admin=source_connection.is_admin,
                second_party=destination,
                digipeaters=tuple(),
                interface=loopback_interface,
                inbound=True,
                application=application,
                frame_sender=dest_send_frame,
            )
            # Hack the connection status to be where we need it to be upon starting.
            dest_connection.status = ConnectionStatus.CONNECTED
            connection = Connection(
                station=self.station,
                first_party=source,
                second_party=destination,
                is_admin=source_connection.is_admin,
                digipeaters=tuple(),
                interface=loopback_interface,
                inbound=False,
                application=shim_application,
                frame_sender=source_send_frame,
            )
            loopback_interface.register_connections(connection, dest_connection)
        else:
            connection = self.station.connection.add_connection(
                first_party=source,
                second_party=destination,
                digipeaters=digipeaters,
                interface=interface,
                inbound=False,
                application=shim_application,
            )
        state.connection = connection
        state.dest_connection = dest_connection
        state.loopback_interface = loopback_interface
        state.remote_state = RemoteConnectionState.FOREGROUND
        connection.negotiate()

    def connect(
        self,
        connection: Connection,
        context: CommandContext[MakeConnectionSpec],
    ) -> None:
        """
        Connect to a remote station.
        """
        self.set_up_connection(
            source_connection=connection,
            interface=context.args.interface,
            destination=context.args.destination,
            digipeaters=context.args.digipeaters,
            loopback=context.args.loopback,
        )

    def quit(self, connection: Connection, _context: CommandContext[None]) -> None:
        """
        Closes the application.
        """
        send_message(connection, "Goodbye!")
        connection.disconnect()

    def router_for(self, connection: Connection) -> CommandRouter:
        """
        Gets the appropriate router for the current connection.
        """
        if connection.is_admin:
            return self.admin_router
        return self.router

    def run_home_command(self, connection: Connection, message: str) -> None:
        """
        Match a message for a home command.
        """
        self.router_for(connection).route(connection, message)

    def on_startup(self, connection: Connection) -> None:
        """
        Set up the current connection's state.
        """
        self.connections[connection] = CommandLineState()
        self.dump_logs_to_connection(connection)
        if connection.is_admin:
            banner = f"PAX25 v{pax25_version} CLI, AGPLv3"
        else:
            banner = self.version_string
        send_message(
            connection,
            f"{banner}\r{self.prompt_text(connection)}",
            append_newline=False,
        )

    def dump_connection_buffer(self, connection: Connection) -> None:
        """
        Dump any outstanding data from the connected buffer to the user.
        """
        state = self.connections[connection]
        data = bytes(state.remote_buffer)
        state.remote_buffer = bytearray()
        send_message(
            connection,
            data.decode("utf-8", errors="backslashreplace"),
            append_newline=False,
        )

    def foreground_connection(
        self,
        connection: Connection,
        _: CommandContext[None],
    ) -> None:
        """
        Foregrounds a backgrounded connection.
        """
        state = self.connections[connection]
        if not state.connection:
            send_message(connection, "Not connected.")
            return
        state.remote_state = RemoteConnectionState.FOREGROUND
        self.dump_connection_buffer(connection)

    def background_connection(self, connection: Connection) -> None:
        """
        Sends the current connection to the background, if it exists. This brings us
        back to the command line.
        """
        state = self.connections[connection]
        state.remote_state = RemoteConnectionState.BACKGROUND
        self.dump_logs_to_connection(connection)

    def on_bytes(self, connection: Connection, data: bytes) -> None:
        """
        Processes incoming bytes, allowing for an interrupt to pull us out of a proxy
        connection.
        """
        for byte in data:
            if byte == 0x0B:
                self.background_connection(connection)
                continue
            super().on_bytes(connection, byte.to_bytes(1, AX25_ENDIAN))

    def on_message(self, connection: Connection, message: str) -> None:
        """
        Handle command from the user.
        """
        state = self.connections[connection]
        if (jump_connection := state.connection) and (
            state.remote_state == RemoteConnectionState.FOREGROUND
        ):
            jump_connection.send_bytes((message + "\r").encode("utf-8"))
            return
        # Send any outstanding frames that entered while they were typing before
        # giving them a response, so we're not missing any.
        self.dump_logs_to_connection(connection)
        self.run_home_command(connection, message)

    def on_shutdown(self, connection: Connection) -> None:
        """
        Clean up connection state.
        """
        state = self.connections[connection]
        if state.connection:
            state.connection.disconnect()
        if state.dest_connection:
            state.dest_connection.disconnect()
        del self.connections[connection]
