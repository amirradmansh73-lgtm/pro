import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import httpx
from netbeacon.config import AppConfig
from netbeacon.models import TargetConfig, TargetState, TargetStatus, CheckResult
from netbeacon.checker import run_target_check


class MonitorEngine:
    def __init__(self, config: AppConfig):
        self.config = config
        self.states: Dict[str, TargetState] = {
            t.name: TargetState(config=t) for t in config.targets
        }
        self.running = False
        self._task: Optional[asyncio.Task] = None

    def add_target(self, target: TargetConfig):
        self.states[target.name] = TargetState(config=target)

    def remove_target(self, target_name: str) -> bool:
        if target_name in self.states:
            del self.states[target_name]
            return True
        return False

    def get_states(self) -> List[TargetState]:
        return list(self.states.values())

    async def check_single_target(self, target_name: str) -> Optional[CheckResult]:
        state = self.states.get(target_name)
        if not state:
            return None

        result = await run_target_check(state.config)
        self._record_result(state, result)
        return result

    def _record_result(self, state: TargetState, result: CheckResult):
        prev_status = state.current_status
        state.current_status = result.status
        state.last_checked = result.timestamp
        state.last_response_time_ms = result.response_time_ms
        state.total_checks += 1
        
        if result.status == TargetStatus.UP:
            state.successful_checks += 1
        
        state.uptime_percentage = round(
            (state.successful_checks / state.total_checks) * 100, 2
        )
        
        state.recent_history.append(result)
        if len(state.recent_history) > 30:
            state.recent_history.pop(0)

        # Trigger webhook if status changed and alert webhook configured
        if prev_status != TargetStatus.UNKNOWN and prev_status != result.status:
            asyncio.create_task(self._send_alert(state, result))

    async def _send_alert(self, state: TargetState, result: CheckResult):
        webhook_url = self.config.alerts.webhook_url
        if not webhook_url:
            return

        payload = {
            "target": state.config.name,
            "status": result.status.value,
            "response_time_ms": result.response_time_ms,
            "error": result.error,
            "timestamp": result.timestamp.isoformat()
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(webhook_url, json=payload)
        except Exception:
            pass

    async def run_cycle(self):
        tasks = [run_target_check(state.config) for state in self.states.values()]
        if not tasks:
            return

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, CheckResult) and res.target_name in self.states:
                self._record_result(self.states[res.target_name], res)

    async def start(self):
        self.running = True
        while self.running:
            await self.run_cycle()
            await asyncio.sleep(self.config.settings.check_interval_seconds)

    def stop(self):
        self.running = False
        if self._task and not self._task.done():
            self._task.cancel()
