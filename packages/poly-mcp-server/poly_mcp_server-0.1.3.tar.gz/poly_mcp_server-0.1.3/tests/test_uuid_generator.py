"""Tests for UUID generator tool."""

import pytest
import re
from poly_mcp_server.server import handle_uuid_generator


UUID_V4_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    re.IGNORECASE
)


@pytest.mark.asyncio
async def test_uuid_generator_v4_single():
    """UUID v4 단일 생성 테스트"""
    result = await handle_uuid_generator({"version": "v4", "count": 1})
    assert len(result) == 1
    assert "v4" in result[0].text
    # UUID 형식 확인
    lines = result[0].text.split('\n')
    uuid_line = [line for line in lines if UUID_V4_PATTERN.search(line)]
    assert len(uuid_line) == 1


@pytest.mark.asyncio
async def test_uuid_generator_v4_multiple():
    """UUID v4 복수 생성 테스트"""
    result = await handle_uuid_generator({"version": "v4", "count": 3})
    assert len(result) == 1
    # 3개의 UUID가 생성되었는지 확인
    lines = result[0].text.split('\n')
    uuid_lines = [line for line in lines if UUID_V4_PATTERN.search(line)]
    assert len(uuid_lines) == 3


@pytest.mark.asyncio
async def test_uuid_generator_v1():
    """UUID v1 생성 테스트"""
    result = await handle_uuid_generator({"version": "v1", "count": 1})
    assert len(result) == 1
    assert "v1" in result[0].text
    # UUID가 포함되어 있는지만 확인
    assert "-" in result[0].text


@pytest.mark.asyncio
async def test_uuid_generator_default():
    """기본값으로 UUID 생성 테스트"""
    result = await handle_uuid_generator({})
    assert len(result) == 1
    # 기본값은 v4, count=1
    lines = result[0].text.split('\n')
    uuid_lines = [line for line in lines if UUID_V4_PATTERN.search(line)]
    assert len(uuid_lines) == 1
