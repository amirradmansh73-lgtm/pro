import pytest
from netbeacon.checker import check_http, check_tcp
from netbeacon.models import TargetConfig, TargetType, TargetStatus


@pytest.mark.asyncio
async def test_missing_http_url():
    target = TargetConfig(name="Empty", type=TargetType.HTTP, url="")
    result = await check_http(target)
    assert result.status == TargetStatus.DOWN
    assert result.error == "Missing target URL"


@pytest.mark.asyncio
async def test_missing_tcp_host():
    target = TargetConfig(name="EmptyTCP", type=TargetType.TCP, host="", port=80)
    result = await check_tcp(target)
    assert result.status == TargetStatus.DOWN
    assert result.error == "Missing target host or port"
