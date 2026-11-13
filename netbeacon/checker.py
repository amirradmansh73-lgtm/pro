import time
import asyncio
import httpx
from netbeacon.models import TargetConfig, TargetType, TargetStatus, CheckResult


async def check_http(target: TargetConfig) -> CheckResult:
    if not target.url:
        return CheckResult(
            target_name=target.name,
            status=TargetStatus.DOWN,
            response_time_ms=0.0,
            error="Missing target URL"
        )
    
    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=target.timeout_seconds, follow_redirects=True) as client:
            resp = await client.get(target.url)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            
            is_ok = (resp.status_code == target.expected_status)
            return CheckResult(
                target_name=target.name,
                status=TargetStatus.UP if is_ok else TargetStatus.DOWN,
                response_time_ms=elapsed_ms,
                status_code=resp.status_code,
                error=None if is_ok else f"Expected status {target.expected_status}, got {resp.status_code}"
            )
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return CheckResult(
            target_name=target.name,
            status=TargetStatus.DOWN,
            response_time_ms=elapsed_ms,
            error=str(exc)
        )


async def check_tcp(target: TargetConfig) -> CheckResult:
    if not target.host or not target.port:
        return CheckResult(
            target_name=target.name,
            status=TargetStatus.DOWN,
            response_time_ms=0.0,
            error="Missing target host or port"
        )

    start_time = time.perf_counter()
    try:
        conn = asyncio.open_connection(target.host, target.port)
        _, writer = await asyncio.wait_for(conn, timeout=target.timeout_seconds)
        writer.close()
        await writer.wait_closed()
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return CheckResult(
            target_name=target.name,
            status=TargetStatus.UP,
            response_time_ms=elapsed_ms
        )
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return CheckResult(
            target_name=target.name,
            status=TargetStatus.DOWN,
            response_time_ms=elapsed_ms,
            error=str(exc)
        )


async def run_target_check(target: TargetConfig) -> CheckResult:
    if target.type == TargetType.TCP:
        return await check_tcp(target)
    return await check_http(target)
