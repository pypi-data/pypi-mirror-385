import logging
from datetime import datetime
from typing import Callable, Optional

from twisted.internet.posixbase import PosixReactorBase

from xp.models import ConbusClientConfig, ConbusDatapointResponse
from xp.models.protocol.conbus_protocol import TelegramReceivedEvent
from xp.models.telegram.datapoint_type import DataPointType
from xp.models.telegram.reply_telegram import ReplyTelegram
from xp.models.telegram.system_function import SystemFunction
from xp.models.telegram.telegram_type import TelegramType
from xp.services import TelegramService
from xp.services.protocol import ConbusProtocol


class ConbusDatapointQueryAllService(ConbusProtocol):
    """
    Utility service for querying all datapoints from a module.

    This service orchestrates multiple ConbusDatapointService calls to query
    all available datapoint types sequentially.
    """

    def __init__(
        self,
        telegram_service: TelegramService,
        cli_config: ConbusClientConfig,
        reactor: PosixReactorBase,
    ) -> None:
        """Initialize the query all service

        Args:
            telegram_service: TelegramService for dependency injection
            cli_config: ConbusClientConfig for connection settings
            reactor: PosixReactorBase for async operations
        """
        super().__init__(cli_config, reactor)
        self.telegram_service = telegram_service
        self.serial_number: str = ""
        self.finish_callback: Optional[Callable[[ConbusDatapointResponse], None]] = None
        self.progress_callback: Optional[Callable[[ReplyTelegram], None]] = None
        self.service_response: ConbusDatapointResponse = ConbusDatapointResponse(
            success=False,
            serial_number=self.serial_number,
        )
        self.datapoint_types = list(DataPointType)
        self.current_index = 0

        # Set up logging
        self.logger = logging.getLogger(__name__)

    def connection_established(self) -> None:
        datapoint_type_code = self.datapoint_types[self.current_index]
        datapoint_type = DataPointType(datapoint_type_code)
        self.logger.debug(
            f"Connection established, querying datapoint {datapoint_type}..."
        )

        self.send_telegram(
            telegram_type=TelegramType.SYSTEM,
            serial_number=self.serial_number,
            system_function=SystemFunction.READ_DATAPOINT,
            data_value=str(datapoint_type.value),
        )

    def telegram_sent(self, telegram_sent: str) -> None:
        self.service_response.sent_telegram = telegram_sent

    def telegram_received(self, telegram_received: TelegramReceivedEvent) -> None:

        self.logger.debug(f"Telegram received: {telegram_received}")
        if not self.service_response.received_telegrams:
            self.service_response.received_telegrams = []
        self.service_response.received_telegrams.append(telegram_received.frame)

        if (
            not telegram_received.checksum_valid
            or telegram_received.telegram_type != TelegramType.REPLY
            or telegram_received.serial_number != self.serial_number
        ):
            self.logger.debug("Not a reply for our serial number")
            return

        # Parse the reply telegram
        datapoint_telegram = self.telegram_service.parse_reply_telegram(
            telegram_received.frame
        )
        datapoint_type_code = self.datapoint_types[self.current_index]
        datapoint_type = DataPointType(datapoint_type_code)
        if (
            not datapoint_telegram
            or datapoint_telegram.system_function != SystemFunction.READ_DATAPOINT
            or datapoint_telegram.datapoint_type != datapoint_type
        ):
            self.logger.debug("Not a reply for our datapoint type")
            return

        self.current_index += 1
        if self.current_index >= len(self.datapoint_types):
            if self.finish_callback:
                self.logger.debug("Received all datapoints telegram")
                self.service_response.success = True
                self.service_response.timestamp = datetime.now()
                self.service_response.serial_number = self.serial_number
                self.service_response.system_function = SystemFunction.READ_DATAPOINT
                self.service_response.datapoint_type = datapoint_telegram.datapoint_type
                self.service_response.datapoint_telegram = datapoint_telegram

                self.finish_callback(self.service_response)
                return

        self.logger.debug("Received a datapoint telegram")
        if self.progress_callback:
            self.progress_callback(datapoint_telegram)

    def failed(self, message: str) -> None:
        self.logger.debug(f"Failed with message: {message}")
        self.service_response.success = False
        self.service_response.timestamp = datetime.now()
        self.service_response.error = message
        if self.finish_callback:
            self.finish_callback(self.service_response)

    def query_all_datapoints(
        self,
        serial_number: str,
        finish_callback: Callable[[ConbusDatapointResponse], None],
        progress_callback: Callable[[ReplyTelegram], None],
        timeout_seconds: Optional[float] = None,
    ) -> None:
        """
        Query a specific datapoint from a module.

        Args:
            serial_number: 10-digit module serial number
            finish_callback: callback function to call when all the datapoint are received
            progress_callback: callback function to call when a datapoint is received
            timeout_seconds: timeout in seconds

        Returns:
            ConbusDatapointResponse with operation result and datapoint value
        """

        self.logger.info("Starting query_datapoint")
        if timeout_seconds:
            self.timeout_seconds = timeout_seconds
        self.finish_callback = finish_callback
        self.progress_callback = progress_callback
        self.serial_number = serial_number
        self.start_reactor()
