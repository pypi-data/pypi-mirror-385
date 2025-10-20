"""Tests for timestamp converter tool."""

import pytest
from poly_mcp_server.server import handle_timestamp_converter


@pytest.mark.asyncio
async def test_timestamp_converter_unix_seconds():
    """Unix 타임스탬프(초) 변환 테스트"""
    result = await handle_timestamp_converter({
        "timestamp": "1609459200",  # 2021-01-01 00:00:00 UTC
        "format": "iso"
    })
    assert len(result) == 1
    assert "2021" in result[0].text


@pytest.mark.asyncio
async def test_timestamp_converter_unix_milliseconds():
    """Unix 타임스탬프(밀리초) 변환 테스트"""
    result = await handle_timestamp_converter({
        "timestamp": "1609459200000",  # 2021-01-01 00:00:00 UTC
        "format": "iso"
    })
    assert len(result) == 1
    assert "2021" in result[0].text


@pytest.mark.asyncio
async def test_timestamp_converter_iso_format():
    """ISO 형식 날짜 변환 테스트"""
    result = await handle_timestamp_converter({
        "timestamp": "2021-01-01T00:00:00Z",
        "format": "unix"
    })
    assert len(result) == 1
    assert "1609459200" in result[0].text


@pytest.mark.asyncio
async def test_timestamp_converter_korean_format():
    """한국어 형식 변환 테스트"""
    result = await handle_timestamp_converter({
        "timestamp": "1609459200",
        "format": "korean"
    })
    assert len(result) == 1
    assert "년" in result[0].text or "2021" in result[0].text


@pytest.mark.asyncio
async def test_timestamp_converter_invalid():
    """잘못된 타임스탬프 테스트"""
    with pytest.raises(ValueError):
        await handle_timestamp_converter({
            "timestamp": "invalid_timestamp",
            "format": "iso"
        })
