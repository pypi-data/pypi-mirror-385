"""Tests for calculator tool."""

import pytest
from poly_mcp_server.server import handle_calculator


@pytest.mark.asyncio
async def test_calculator_addition():
    """덧셈 테스트"""
    result = await handle_calculator({"expression": "2 + 3"})
    assert len(result) == 1
    assert "5" in result[0].text


@pytest.mark.asyncio
async def test_calculator_multiplication():
    """곱셈 테스트"""
    result = await handle_calculator({"expression": "4 * 5"})
    assert len(result) == 1
    assert "20" in result[0].text


@pytest.mark.asyncio
async def test_calculator_complex():
    """복잡한 수식 테스트"""
    result = await handle_calculator({"expression": "2 + 3 * 4"})
    assert len(result) == 1
    assert "14" in result[0].text


@pytest.mark.asyncio
async def test_calculator_division():
    """나눗셈 테스트"""
    result = await handle_calculator({"expression": "10 / 2"})
    assert len(result) == 1
    assert "5" in result[0].text


@pytest.mark.asyncio
async def test_calculator_invalid_expression():
    """잘못된 수식 테스트"""
    with pytest.raises(ValueError):
        await handle_calculator({"expression": "import os"})


@pytest.mark.asyncio
async def test_calculator_invalid_characters():
    """허용되지 않는 문자 테스트"""
    with pytest.raises(ValueError):
        await handle_calculator({"expression": "2 + abc"})
