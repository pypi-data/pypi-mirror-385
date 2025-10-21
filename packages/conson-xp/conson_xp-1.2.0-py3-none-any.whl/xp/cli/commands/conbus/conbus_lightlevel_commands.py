"""Conbus lightlevel operations CLI commands."""

import json

import click

from xp.cli.commands.conbus.conbus import conbus_lightlevel
from xp.cli.utils.decorators import (
    connection_command,
    handle_service_errors,
)
from xp.cli.utils.serial_number_type import SERIAL
from xp.models.conbus.conbus_lightlevel import ConbusLightlevelResponse
from xp.services.conbus.conbus_lightlevel_set_service import (
    ConbusLightlevelError,
    ConbusLightlevelSetService,
)


@conbus_lightlevel.command("set")
@click.argument("serial_number", type=SERIAL)
@click.argument("output_number", type=click.IntRange(0, 8))
@click.argument("level", type=click.IntRange(0, 100))
@click.pass_context
@connection_command()
@handle_service_errors(ConbusLightlevelError)
def xp_lightlevel_set(
    ctx: click.Context, serial_number: str, output_number: int, level: int
) -> None:
    r"""Set light level for output_number on XP module serial_number.

    Args:
        ctx: Click context object.
        serial_number: 10-digit module serial number.
        output_number: Output number (0-8).
        level: Light level (0-100).

    Examples:
        \b
        xp conbus lightlevel set 0123450001 2 50   # Set output 2 to 50%
        xp conbus lightlevel set 0011223344 0 100  # Set output 0 to 100%
    """

    def finish(response: "ConbusLightlevelResponse") -> None:
        """Handle successful completion of light level set command.

        Args:
            response: Light level response object.
        """
        click.echo(json.dumps(response.to_dict(), indent=2))

    service = (
        ctx.obj.get("container").get_container().resolve(ConbusLightlevelSetService)
    )

    with service:
        service.set_lightlevel(serial_number, output_number, level, finish, 0.5)


@conbus_lightlevel.command("off")
@click.argument("serial_number", type=SERIAL)
@click.argument("output_number", type=click.IntRange(0, 8))
@click.pass_context
@connection_command()
@handle_service_errors(ConbusLightlevelError)
def xp_lightlevel_off(
    ctx: click.Context, serial_number: str, output_number: int
) -> None:
    r"""Turn off light for output_number on XP module serial_number (set level to 0).

    Args:
        ctx: Click context object.
        serial_number: 10-digit module serial number.
        output_number: Output number (0-8).

    Examples:
        \b
        xp conbus lightlevel off 0123450001 2   # Turn off output 2
        xp conbus lightlevel off 0011223344 0   # Turn off output 0
    """

    def finish(response: "ConbusLightlevelResponse") -> None:
        """Handle successful completion of light level off command.

        Args:
            response: Light level response object.
        """
        click.echo(json.dumps(response.to_dict(), indent=2))

    service = (
        ctx.obj.get("container").get_container().resolve(ConbusLightlevelSetService)
    )

    with service:
        service.turn_off(serial_number, output_number, finish, 0.5)


@conbus_lightlevel.command("on")
@click.argument("serial_number", type=SERIAL)
@click.argument("output_number", type=click.IntRange(0, 8))
@click.pass_context
@connection_command()
@handle_service_errors(ConbusLightlevelError)
def xp_lightlevel_on(
    ctx: click.Context, serial_number: str, output_number: int
) -> None:
    r"""Turn on light for output_number on XP module serial_number (set level to 80%).

    Args:
        ctx: Click context object.
        serial_number: 10-digit module serial number.
        output_number: Output number (0-8).

    Examples:
        \b
        xp conbus lightlevel on 0123450001 2   # Turn on output 2 (80%)
        xp conbus lightlevel on 0011223344 0   # Turn on output 0 (80%)
    """

    def finish(response: "ConbusLightlevelResponse") -> None:
        """Handle successful completion of light level on command.

        Args:
            response: Light level response object.
        """
        click.echo(json.dumps(response.to_dict(), indent=2))

    service = (
        ctx.obj.get("container").get_container().resolve(ConbusLightlevelSetService)
    )

    with service:
        service.turn_on(serial_number, output_number, finish, 0.5)


@conbus_lightlevel.command("get")
@click.argument("serial_number", type=SERIAL)
@click.argument("output_number", type=click.IntRange(0, 8))
@click.pass_context
@connection_command()
@handle_service_errors(ConbusLightlevelError)
def xp_lightlevel_get(
    ctx: click.Context, serial_number: str, output_number: int
) -> None:
    r"""Get current light level for output_number on XP module serial_number.

    Args:
        ctx: Click context object.
        serial_number: 10-digit module serial number.
        output_number: Output number (0-8).

    Examples:
        \b
        xp conbus lightlevel get 0123450001 2   # Get light level for output 2
        xp conbus lightlevel get 0011223344 0   # Get light level for output 0
    """

    def finish(response: "ConbusLightlevelResponse") -> None:
        """Handle successful completion of light level get command.

        Args:
            response: Light level response object.
        """
        click.echo(json.dumps(response.to_dict(), indent=2))

    service = (
        ctx.obj.get("container").get_container().resolve(ConbusLightlevelSetService)
    )

    with service:
        service.get_lightlevel(serial_number, output_number, finish, 0.5)
