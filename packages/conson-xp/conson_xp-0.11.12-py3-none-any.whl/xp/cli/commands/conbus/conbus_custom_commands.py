"""Conbus client operations CLI commands."""

import json

import click
from click import Context

from xp.cli.commands.conbus.conbus import conbus
from xp.cli.utils.decorators import (
    connection_command,
    handle_service_errors,
)
from xp.cli.utils.error_handlers import CLIErrorHandler
from xp.cli.utils.serial_number_type import SERIAL
from xp.services.conbus.conbus_custom_service import ConbusCustomService
from xp.services.conbus.conbus_datapoint_service import (
    ConbusDatapointError,
)


@conbus.command("custom")
@click.argument("serial_number", type=SERIAL)
@click.argument("function_code")
@click.argument("datapoint_code")
@click.pass_context
@connection_command()
@handle_service_errors(ConbusDatapointError)
def send_custom_telegram(
    ctx: Context, serial_number: str, function_code: str, datapoint_code: str
) -> None:
    """
    Send custom telegram with specified function and data point codes.

    Examples:

    \b
        xp conbus custom 0012345011 02 E2
        xp conbus custom 0012345011 17 AA
    """
    service = ctx.obj.get("container").get_container().resolve(ConbusCustomService)

    try:
        with service:
            response = service.send_custom_telegram(
                serial_number, function_code, datapoint_code
            )

        click.echo(json.dumps(response.to_dict(), indent=2))

    except ConbusDatapointError as e:
        CLIErrorHandler.handle_service_error(
            e,
            "custom telegram send",
            {
                "serial_number": serial_number,
                "function_code": function_code,
                "datapoint_code": datapoint_code,
            },
        )
