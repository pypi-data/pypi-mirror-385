from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ConbusRequest:
    """Represents a Conbus send request"""

    serial_number: Optional[str] = None
    function_code: Optional[str] = None
    data: Optional[str] = None
    telegram: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "serial_number": self.serial_number,
            "function_code": self.function_code,
            "data": self.data,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class ConbusResponse:
    """Represents a response from Conbus send operation"""

    success: bool
    request: ConbusRequest
    sent_telegram: Optional[str] = None
    received_telegrams: Optional[list[str]] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.received_telegrams is None:
            self.received_telegrams = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "request": self.request.to_dict(),
            "sent_telegram": self.sent_telegram,
            "received_telegrams": self.received_telegrams,
            "error": self.error,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
