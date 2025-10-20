"""
Commands for administrative tasks.
"""

import asyncio
import json
from pathlib import Path

from pax25 import Station
from pax25.applications.parsers import (
    call_sign_parser,
    file_path_parser,
    no_arguments,
    optional,
    requires_full_name,
    string_parser,
)
from pax25.applications.router import CommandContext, CommandSpec
from pax25.applications.utils import send_message
from pax25.ax25.address import Address
from pax25.services.connection.connection import Connection
from pax25.types import StationConfig
from pax25.utils import safe_save


def build_shutdown_command(station: Station) -> CommandSpec[None]:
    def shutdown(connection: Connection, _context: CommandContext[None]) -> None:
        """
        Shuts down the station.
        """
        send_message(connection, "Shutting down station.")
        asyncio.ensure_future(station.shutdown())

    return CommandSpec(
        command="shutdown",
        help="Shuts down the station",
        parser=requires_full_name(no_arguments),
        function=shutdown,
    )


def build_save_command(station: Station) -> CommandSpec[str | None]:
    def save(connection: Connection, context: CommandContext[str | None]) -> None:
        """
        Saves the station's configuration to a config file.
        """
        file_path = context.args or station.config_file_path
        if not file_path:
            send_message(
                connection, "Please provide a save file path, such as './config.json'"
            )
            return
        try:
            safe_save(path=Path(file_path), data=station.settings, debug=True)
        except OSError as err:
            send_message(connection, str(err))
        send_message(connection, "Saved.")

    return CommandSpec(
        command="save",
        help="Saves the current station configuration",
        parser=optional(string_parser),
        function=save,
    )


def build_name_command(station: Station) -> CommandSpec[Address | None]:
    async def update_settings(
        previous_name: str, connection: Connection, settings: StationConfig
    ) -> None:
        await station.reload_settings(settings)
        send_message(
            connection,
            f"Station name is now {settings['name']} (was {previous_name}.)",
        )

    def name(connection: Connection, context: CommandContext[Address | None]) -> None:
        """
        Sets the name of the station, or if no name is provided, returns it.
        """
        current_name = station.name
        if context.args is None:
            send_message(connection, current_name)
            return
        settings = station.settings
        settings["name"] = str(context.args)
        asyncio.ensure_future(update_settings(current_name, connection, settings))

    return CommandSpec(
        command="name",
        help="Retrieves (or sets) the name of the current station",
        parser=optional(call_sign_parser),
        function=name,
    )


def build_save_file_command(station: Station) -> CommandSpec[Path | None]:
    def save_file(connection: Connection, context: CommandContext[Path | None]) -> None:
        """
        Set the default configuration file for saving/loading the state of the station.
        """
        if context.args is None:
            if not station.config_file_path:
                send_message(connection, "None set")
                return
            send_message(connection, str(station.config_file_path))
            return
        old_path = station.config_file_path
        station.config_file_path = str(context.args)
        send_message(
            connection,
            f"Set to {repr(str(context.args))}. Was {repr(old_path)}",
        )

    return CommandSpec(
        command="setsave",
        help="Displays (or sets) the station configuration file path",
        parser=optional(file_path_parser),
        function=save_file,
    )


def build_load_command(station: Station) -> CommandSpec[Path | None]:
    async def reload_settings(connection: Connection, settings: StationConfig) -> None:
        await station.reload_settings(settings)
        send_message(
            connection,
            "Loaded.",
        )

    def load(connection: Connection, context: CommandContext[Path | None]) -> None:
        """
        Loads a configuration file, updating the station's settings.
        """
        if context.args is None:
            if not station.config_file_path:
                send_message(connection, "Config file not specified.")
                return
            path = Path(station.config_file_path)
        else:
            path = context.args
        try:
            with open(path) as file:
                settings = json.load(file)
        except (OSError, ValueError) as err:
            send_message(
                connection,
                f"Error when loading {repr(str(path))}. {err.__class__}: {err}",
            )
        asyncio.ensure_future(reload_settings(connection, settings))

    return CommandSpec(
        command="load",
        help="Load settings from the default file, or a specific file if specified.",
        parser=optional(file_path_parser),
        function=load,
    )
