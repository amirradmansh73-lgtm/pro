from pathlib import Path
from typing import List, Optional
import yaml
from pydantic import BaseModel, Field
from netbeacon.models import TargetConfig


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080


class MonitoringSettings(BaseModel):
    check_interval_seconds: int = 30
    timeout_seconds: float = 5.0


class AlertsSettings(BaseModel):
    webhook_url: Optional[str] = None


class AppConfig(BaseModel):
    server: ServerSettings = Field(default_factory=ServerSettings)
    settings: MonitoringSettings = Field(default_factory=MonitoringSettings)
    targets: List[TargetConfig] = Field(default_factory=list)
    alerts: AlertsSettings = Field(default_factory=AlertsSettings)


def load_config(path: str | Path = "netbeacon.yaml") -> AppConfig:
    config_file = Path(path)
    if not config_file.exists():
        return AppConfig()
    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return AppConfig.model_validate(data)
