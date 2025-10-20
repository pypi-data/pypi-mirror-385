"""FastAPI router for Conbus operations."""

import logging
from typing import Union

from fastapi import Request
from fastapi.responses import JSONResponse

from xp.api.models.api import ApiErrorResponse, ApiResponse
from xp.api.routers.conbus import router
from xp.api.routers.errors import handle_service_error
from xp.models.telegram.datapoint_type import DataPointType
from xp.services.conbus.conbus_datapoint_service import ConbusDatapointService

logger = logging.getLogger(__name__)


@router.get(
    "/datapoint/{datapoint}/{serial_number}",
    response_model=Union[ApiResponse, ApiErrorResponse],
    responses={
        200: {"model": ApiResponse, "description": "Datapoint completed successfully"},
        400: {"model": ApiErrorResponse, "description": "Connection or request error"},
        408: {"model": ApiErrorResponse, "description": "Request timeout"},
        500: {"model": ApiErrorResponse, "description": "Internal server error"},
    },
)
async def datapoint_devices(
    request: Request,
    datapoint: DataPointType = DataPointType.SW_VERSION,
    serial_number: str = "1702033007",
) -> Union[ApiResponse, ApiErrorResponse, JSONResponse]:
    """
    Initiate a Datapoint operation to find devices on the network.

    Sends a broadcastDatapoint telegram and collects responses from all connected devices.
    """
    service = request.app.state.container.get_container().resolve(
        ConbusDatapointService
    )
    # SendDatapoint telegram and receive responses
    with service:
        response = service.query_datapoint(
            datapoint_type=datapoint, serial_number=serial_number
        )

    if not response.success:
        return handle_service_error(response.error or "Unknown error")

    if response.datapoint_telegram is None:
        return ApiErrorResponse(
            success=False,
            error=response.error or "Unknown error",
        )

    # Build successful response
    if response.datapoint_telegram and response.datapoint_telegram.datapoint_type:
        return ApiResponse(
            success=True,
            result=response.datapoint_telegram.data_value,
            description=response.datapoint_telegram.datapoint_type.name,
        )
    return ApiResponse(
        success=True,
        result=response.datapoint_telegram.data_value,
        description="Datapoint value retrieved",
    )
