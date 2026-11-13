from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class TargetType(str, Enum):
    HTTP = "http"
    TCP = "tcp"


class TargetStatus(str, Enum):
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


class TargetConfig(BaseModel):
    name: str
    type: TargetType = TargetType.HTTP
    url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    expected_status: int = 200
    timeout_seconds: float = 5.0


class CheckResult(BaseModel):
    target_name: str
    status: TargetStatus
    response_time_ms: float
    status_code: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TargetState(BaseModel):
    config: TargetConfig
    current_status: TargetStatus = TargetStatus.UNKNOWN
    last_checked: Optional[datetime] = None
    last_response_time_ms: float = 0.0
    uptime_percentage: float = 100.0
    total_checks: int = 0
    successful_checks: int = 0
    recent_history: List[CheckResult] = Field(default_factory=list)
