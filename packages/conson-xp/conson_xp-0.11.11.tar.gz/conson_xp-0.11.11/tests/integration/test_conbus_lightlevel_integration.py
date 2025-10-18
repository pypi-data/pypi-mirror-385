"""Integration tests for Conbus lightlevel functionality"""

from datetime import datetime
from unittest.mock import Mock, patch

from click.testing import CliRunner

from xp.cli.main import cli
from xp.models.conbus.conbus_lightlevel import ConbusLightlevelResponse
from xp.services.conbus.conbus_lightlevel_service import (
    ConbusLightlevelError,
    ConbusLightlevelService,
)


class TestConbusLightlevelIntegration:
    """Integration test cases for Conbus lightlevel operations"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        self.valid_serial = "0123450001"
        self.invalid_serial = "invalid"
        self.valid_output_number = 2
        self.valid_level = 50

    def test_conbus_lightlevel_set(self):
        """Test setting specific light level"""

        # Mock successful response
        mock_service = Mock()
        mock_service.__enter__ = Mock(return_value=mock_service)
        mock_service.__exit__ = Mock(return_value=None)

        mock_response = ConbusLightlevelResponse(
            success=True,
            serial_number=self.valid_serial,
            output_number=self.valid_output_number,
            level=self.valid_level,
            timestamp=datetime.now(),
        )
        mock_service.set_lightlevel.return_value = mock_response

        # Setup mock container to resolve ConbusLightlevelService
        mock_container = Mock()
        mock_container.resolve.return_value = mock_service
        mock_service_container = Mock()
        mock_service_container.get_container.return_value = mock_container

        # Run CLI command
        result = self.runner.invoke(
            cli,
            [
                "conbus",
                "lightlevel",
                "set",
                self.valid_serial,
                str(self.valid_output_number),
                str(self.valid_level),
            ],
            obj={"container": mock_service_container},
        )

        # Assertions
        assert result.exit_code == 0
        assert '"success": true' in result.output
        assert f'"serial_number": "{self.valid_serial}"' in result.output
        assert f'"output_number": {self.valid_output_number}' in result.output
        assert f'"level": {self.valid_level}' in result.output
        mock_service.set_lightlevel.assert_called_once_with(
            self.valid_serial, self.valid_output_number, self.valid_level
        )

    def test_conbus_lightlevel_off(self):
        """Test turning light off (level 0)"""

        # Mock successful response
        mock_service = Mock()
        mock_service.__enter__ = Mock(return_value=mock_service)
        mock_service.__exit__ = Mock(return_value=None)

        mock_response = ConbusLightlevelResponse(
            success=True,
            serial_number=self.valid_serial,
            output_number=self.valid_output_number,
            level=0,
            timestamp=datetime.now(),
        )
        mock_service.turn_off.return_value = mock_response

        # Setup mock container to resolve ConbusLightlevelService
        mock_container = Mock()
        mock_container.resolve.return_value = mock_service
        mock_service_container = Mock()
        mock_service_container.get_container.return_value = mock_container

        # Run CLI command
        result = self.runner.invoke(
            cli,
            [
                "conbus",
                "lightlevel",
                "off",
                self.valid_serial,
                str(self.valid_output_number),
            ],
            obj={"container": mock_service_container},
        )

        # Assertions
        assert result.exit_code == 0
        assert '"success": true' in result.output
        assert '"level": 0' in result.output
        mock_service.turn_off.assert_called_once_with(
            self.valid_serial, self.valid_output_number
        )

    def test_conbus_lightlevel_on(self):
        """Test turning light on (level 80)"""

        # Mock successful response
        mock_service = Mock()
        mock_service.__enter__ = Mock(return_value=mock_service)
        mock_service.__exit__ = Mock(return_value=None)

        mock_response = ConbusLightlevelResponse(
            success=True,
            serial_number=self.valid_serial,
            output_number=self.valid_output_number,
            level=80,
            timestamp=datetime.now(),
        )
        mock_service.turn_on.return_value = mock_response

        # Setup mock container to resolve ConbusLightlevelService
        mock_container = Mock()
        mock_container.resolve.return_value = mock_service
        mock_service_container = Mock()
        mock_service_container.get_container.return_value = mock_container

        # Run CLI command
        result = self.runner.invoke(
            cli,
            [
                "conbus",
                "lightlevel",
                "on",
                self.valid_serial,
                str(self.valid_output_number),
            ],
            obj={"container": mock_service_container},
        )

        # Assertions
        assert result.exit_code == 0
        assert '"success": true' in result.output
        assert '"level": 80' in result.output
        mock_service.turn_on.assert_called_once_with(
            self.valid_serial, self.valid_output_number
        )

    def test_conbus_lightlevel_get(self):
        """Test querying light level"""

        # Mock successful response
        mock_service = Mock()
        mock_service.__enter__ = Mock(return_value=mock_service)
        mock_service.__exit__ = Mock(return_value=None)

        mock_response = ConbusLightlevelResponse(
            success=True,
            serial_number=self.valid_serial,
            output_number=self.valid_output_number,
            level=75,
            timestamp=datetime.now(),
        )
        mock_service.get_lightlevel.return_value = mock_response

        # Setup mock container to resolve ConbusLightlevelService
        mock_container = Mock()
        mock_container.resolve.return_value = mock_service
        mock_service_container = Mock()
        mock_service_container.get_container.return_value = mock_container

        # Run CLI command
        result = self.runner.invoke(
            cli,
            [
                "conbus",
                "lightlevel",
                "get",
                self.valid_serial,
                str(self.valid_output_number),
            ],
            obj={"container": mock_service_container},
        )

        # Assertions
        assert result.exit_code == 0
        assert '"success": true' in result.output
        assert '"level": 75' in result.output
        mock_service.get_lightlevel.assert_called_once_with(
            self.valid_serial, self.valid_output_number
        )

    def test_conbus_lightlevel_invalid_level(self):
        """Test invalid level values are caught by CLI validation"""

        # Run CLI command with invalid level
        result = self.runner.invoke(
            cli,
            [
                "conbus",
                "lightlevel",
                "set",
                self.valid_serial,
                str(self.valid_output_number),
                "150",
            ],
        )

        # Should be caught by CLI validation before reaching service
        assert result.exit_code == 2  # CLI validation error
        assert "Invalid value for 'LEVEL'" in result.output
        assert "150 is not in the range 0<=x<=100" in result.output

    def test_conbus_lightlevel_connection_error(self):
        """Test handling network connection failures"""

        # Mock service that raises connection error
        mock_service = Mock()
        mock_service.__enter__ = Mock(return_value=mock_service)
        mock_service.__exit__ = Mock(return_value=None)

        mock_service.set_lightlevel.side_effect = ConbusLightlevelError(
            "Connection failed"
        )

        # Setup mock container to resolve ConbusLightlevelService
        mock_container = Mock()
        mock_container.resolve.return_value = mock_service
        mock_service_container = Mock()
        mock_service_container.get_container.return_value = mock_container

        # Run CLI command
        result = self.runner.invoke(
            cli,
            [
                "conbus",
                "lightlevel",
                "set",
                self.valid_serial,
                str(self.valid_output_number),
                "50",
            ],
            obj={"container": mock_service_container},
        )

        # Should handle the error gracefully
        assert "Connection failed" in result.output or "Error" in result.output
        assert result.exit_code != 0

    def test_conbus_lightlevel_invalid_response(self):
        """Test handling invalid responses from the server"""

        # Mock service with failed response
        mock_service = Mock()
        mock_service.__enter__ = Mock(return_value=mock_service)
        mock_service.__exit__ = Mock(return_value=None)

        mock_response = ConbusLightlevelResponse(
            success=False,
            serial_number=self.valid_serial,
            output_number=self.valid_output_number,
            level=None,
            timestamp=datetime.now(),
            error="Invalid response from server",
        )
        mock_service.get_lightlevel.return_value = mock_response

        # Setup mock container to resolve ConbusLightlevelService
        mock_container = Mock()
        mock_container.resolve.return_value = mock_service
        mock_service_container = Mock()
        mock_service_container.get_container.return_value = mock_container

        # Run CLI command
        result = self.runner.invoke(
            cli,
            [
                "conbus",
                "lightlevel",
                "get",
                self.valid_serial,
                str(self.valid_output_number),
            ],
            obj={"container": mock_service_container},
        )

        # Should return the failed response
        assert '"success": false' in result.output
        assert result.exit_code == 0  # CLI succeeds but response indicates failure
        assert "Invalid response from server" in result.output


class TestConbusLightlevelService:
    """Unit tests for ConbusLightlevelService functionality."""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_serial = "0123450001"
        self.valid_output_number = 2
        self.valid_level = 50

    def test_set_lightlevel_success(self):
        """Test successful setting of light level"""

        # Mock service dependencies
        mock_telegram_service = Mock()
        mock_conbus_service = Mock()
        mock_datapoint_service = Mock()

        # Create mock response
        mock_response = Mock()
        mock_response.success = True
        mock_response.sent_telegram = f"<S{self.valid_serial}F04D1502:050FN>"
        mock_response.received_telegrams = [f"<R{self.valid_serial}F18DFI>"]  # ACK
        mock_response.error = None
        mock_response.timestamp = datetime.now()

        mock_conbus_service.send_telegram.return_value = mock_response

        # Test the service with mocked dependencies
        result = ConbusLightlevelService(
            telegram_service=mock_telegram_service,
            conbus_service=mock_conbus_service,
            datapoint_service=mock_datapoint_service,
        ).set_lightlevel(self.valid_serial, self.valid_output_number, self.valid_level)

        # Assertions
        assert result.success is True
        assert result.serial_number == self.valid_serial
        assert result.output_number == self.valid_output_number
        assert result.level == self.valid_level
        assert result.error is None

        # Verify telegram was sent correctly
        from xp.models.telegram.datapoint_type import DataPointType
        from xp.models.telegram.system_function import SystemFunction

        mock_conbus_service.send_telegram.assert_called_once_with(
            self.valid_serial,
            SystemFunction.WRITE_CONFIG,
            f"{DataPointType.MODULE_LIGHT_LEVEL.value}02:050",
        )

    def test_set_lightlevel_invalid_level(self):
        """Test setting invalid light level"""

        # Mock service dependencies
        mock_telegram_service = Mock()
        mock_conbus_service = Mock()
        mock_datapoint_service = Mock()

        # Test the service with invalid level
        result = ConbusLightlevelService(
            telegram_service=mock_telegram_service,
            conbus_service=mock_conbus_service,
            datapoint_service=mock_datapoint_service,
        ).set_lightlevel(
            self.valid_serial, self.valid_output_number, 150  # Invalid level > 100
        )

        # Assertions
        assert result.success is False
        assert result.level == 150
        assert result.error is not None
        assert "Light level must be between 0 and 100" in result.error

    def test_turn_off(self):
        """Test turning light off calls set_lightlevel with level 0"""
        # Mock service dependencies
        mock_telegram_service = Mock()
        mock_conbus_service = Mock()
        mock_datapoint_service = Mock()

        service = ConbusLightlevelService(
            telegram_service=mock_telegram_service,
            conbus_service=mock_conbus_service,
            datapoint_service=mock_datapoint_service,
        )

        # Mock the set_lightlevel method
        with patch.object(service, "set_lightlevel") as mock_set:
            mock_response = ConbusLightlevelResponse(
                success=True,
                serial_number=self.valid_serial,
                output_number=self.valid_output_number,
                level=0,
                timestamp=datetime.now(),
            )
            mock_set.return_value = mock_response

            result = service.turn_off(self.valid_serial, self.valid_output_number)

            mock_set.assert_called_once_with(
                self.valid_serial, self.valid_output_number, 0
            )
            assert result.level == 0

    def test_turn_on(self):
        """Test turning light on calls set_lightlevel with level 80"""
        # Mock service dependencies
        mock_telegram_service = Mock()
        mock_conbus_service = Mock()
        mock_datapoint_service = Mock()

        service = ConbusLightlevelService(
            telegram_service=mock_telegram_service,
            conbus_service=mock_conbus_service,
            datapoint_service=mock_datapoint_service,
        )

        # Mock the set_lightlevel method
        with patch.object(service, "set_lightlevel") as mock_set:
            mock_response = ConbusLightlevelResponse(
                success=True,
                serial_number=self.valid_serial,
                output_number=self.valid_output_number,
                level=80,
                timestamp=datetime.now(),
            )
            mock_set.return_value = mock_response

            result = service.turn_on(self.valid_serial, self.valid_output_number)

            mock_set.assert_called_once_with(
                self.valid_serial, self.valid_output_number, 80
            )
            assert result.level == 80

    def test_get_lightlevel_success(self):
        """Test successful getting of light level"""

        # Mock service dependencies
        mock_telegram_service = Mock()
        mock_conbus_service = Mock()
        mock_datapoint_service = Mock()

        # Create mock datapoint response with multiple links
        mock_datapoint_response = Mock()
        mock_datapoint_response.success = True
        mock_datapoint_response.datapoint_telegram = Mock()
        mock_datapoint_response.datapoint_telegram.data_value = "00:025,01:050,02:075"
        mock_datapoint_response.sent_telegram = f"<S{self.valid_serial}F02D15FG>"
        mock_datapoint_response.received_telegrams = [
            f"<R{self.valid_serial}F02D1500:025,01:050,02:075FH>"
        ]
        mock_datapoint_response.error = None

        mock_datapoint_service.query_datapoint.return_value = mock_datapoint_response

        # Test the service - get level for link 2
        result = ConbusLightlevelService(
            telegram_service=mock_telegram_service,
            conbus_service=mock_conbus_service,
            datapoint_service=mock_datapoint_service,
        ).get_lightlevel(self.valid_serial, 2)

        # Assertions
        assert result.success is True
        assert result.serial_number == self.valid_serial
        assert result.output_number == 2
        assert result.level == 75  # Level for link 02 from the response
        assert result.error is None

        # Verify datapoint service was called correctly
        from xp.models.telegram.datapoint_type import DataPointType

        mock_datapoint_service.query_datapoint.assert_called_once_with(
            DataPointType.MODULE_LIGHT_LEVEL, self.valid_serial
        )

    def test_service_context_manager(self):
        """Test service can be used as context manager"""
        # Mock service dependencies
        mock_telegram_service = Mock()
        mock_conbus_service = Mock()
        mock_datapoint_service = Mock()

        service = ConbusLightlevelService(
            telegram_service=mock_telegram_service,
            conbus_service=mock_conbus_service,
            datapoint_service=mock_datapoint_service,
        )

        with service as s:
            assert s is service
