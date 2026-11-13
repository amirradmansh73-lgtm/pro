import pytest
from netbeacon.config import AppConfig
from netbeacon.models import TargetConfig, TargetType, TargetStatus, CheckResult
from netbeacon.monitor import MonitorEngine


def test_monitor_state_tracking():
    config = AppConfig(
        targets=[
            TargetConfig(name="Dummy", type=TargetType.HTTP, url="https://example.com")
        ]
    )
    engine = MonitorEngine(config)
    assert len(engine.get_states()) == 1

    # Simulate recording check results
    res_up = CheckResult(
        target_name="Dummy",
        status=TargetStatus.UP,
        response_time_ms=25.0
    )
    engine._record_result(engine.states["Dummy"], res_up)

    state = engine.states["Dummy"]
    assert state.current_status == TargetStatus.UP
    assert state.total_checks == 1
    assert state.successful_checks == 1
    assert state.uptime_percentage == 100.0

    # Simulate down check
    res_down = CheckResult(
        target_name="Dummy",
        status=TargetStatus.DOWN,
        response_time_ms=50.0,
        error="Timeout"
    )
    engine._record_result(engine.states["Dummy"], res_down)
    assert state.total_checks == 2
    assert state.successful_checks == 1
    assert state.uptime_percentage == 50.0
