from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ConbusLightlevelResponse:
    """Represents a response from Conbus lightlevel operation"""

    success: bool
    serial_number: str
    output_number: int
    level: Optional[int]
    timestamp: datetime
    sent_telegram: Optional[str] = None
    received_telegrams: Optional[list[str]] = None
    error: Optional[str] = None

    def __post_init__(self) -> None:
        if self.received_telegrams is None:
            self.received_telegrams = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "serial_number": self.serial_number,
            "output_number": self.output_number,
            "level": self.level,
            "sent_telegram": self.sent_telegram,
            "received_telegrams": self.received_telegrams,
            "error": self.error,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
