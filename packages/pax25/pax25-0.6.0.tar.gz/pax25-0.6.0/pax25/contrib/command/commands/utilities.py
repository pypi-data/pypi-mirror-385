"""
Utility commands, as opposed to utility functions, which would be put in a file
named 'utils' instead.
"""

import itertools

from pax25 import Station
from pax25.applications.parsers import no_arguments
from pax25.applications.router import CommandContext, CommandSpec
from pax25.applications.utils import build_columns, send_message
from pax25.services.connection.connection import Connection
from pax25.utils import gateways_for


def build_whoami_command() -> CommandSpec[None]:
    def whoami(connection: Connection, _context: CommandContext[None]) -> None:
        """
        Tells the user who they are.
        """
        send_message(connection, str(connection.first_party))

    return CommandSpec(
        command="whoami",
        help="Tells you what your current connected station name is.",
        parser=no_arguments,
        function=whoami,
    )


def build_ports_command(station: Station) -> CommandSpec[None]:
    def ports(connection: Connection, _context: CommandContext[None]) -> None:
        """
        List all ports (interfaces) available for connecting outward.
        """
        headers = ["PORT", "ALIAS", "TYPE"]
        source_gateways = gateways_for(station)
        if not source_gateways:
            send_message(
                connection,
                "No gateways configured. You may not connect to outbound stations.",
            )
            return
        gateways = [
            (str(port.number), port.name, port.type)
            for port in source_gateways.values()
        ]
        columns = build_columns(itertools.chain(headers, *gateways), num_columns=3)
        send_message(connection, "\r".join(columns))

    return CommandSpec(
        command="ports",
        help="\r".join(
            [
                "Usage: PORTS",
                "",
                "Lists all available interfaces/ports for connecting to "
                "outbound stations, including aliases. Aliases are case-"
                "sensitive.",
            ]
        ),
        parser=no_arguments,
        function=ports,
    )
