"""Tests for text analyzer tool."""

import pytest
from poly_mcp_server.server import handle_text_analyzer


@pytest.mark.asyncio
async def test_text_analyzer_korean():
    """한국어 텍스트 분석 테스트"""
    result = await handle_text_analyzer({
        "text": "안녕하세요. 반갑습니다.",
        "language": "ko"
    })
    assert len(result) == 1
    assert "글자 수" in result[0].text
    assert "단어 수" in result[0].text
    assert "문장 수" in result[0].text


@pytest.mark.asyncio
async def test_text_analyzer_english():
    """영어 텍스트 분석 테스트"""
    result = await handle_text_analyzer({
        "text": "Hello world. Nice to meet you.",
        "language": "en"
    })
    assert len(result) == 1
    assert "글자 수" in result[0].text
    assert "영어" in result[0].text


@pytest.mark.asyncio
async def test_text_analyzer_empty():
    """빈 텍스트 테스트"""
    result = await handle_text_analyzer({
        "text": "",
        "language": "ko"
    })
    assert len(result) == 1
    assert "0" in result[0].text


@pytest.mark.asyncio
async def test_text_analyzer_multiline():
    """여러 줄 텍스트 테스트"""
    result = await handle_text_analyzer({
        "text": "첫 번째 줄입니다.\n두 번째 줄입니다.\n세 번째 줄입니다.",
        "language": "ko"
    })
    assert len(result) == 1
    assert "문장 수" in result[0].text
