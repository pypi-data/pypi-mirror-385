"""Tests for hash generator tool."""

import pytest
from poly_mcp_server.server import handle_hash_generator


@pytest.mark.asyncio
async def test_hash_generator_sha256():
    """SHA256 해시 생성 테스트"""
    result = await handle_hash_generator({
        "text": "hello",
        "algorithm": "sha256"
    })
    assert len(result) == 1
    assert "SHA256" in result[0].text
    # SHA256은 64자리 16진수
    assert "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824" in result[0].text


@pytest.mark.asyncio
async def test_hash_generator_md5():
    """MD5 해시 생성 테스트"""
    result = await handle_hash_generator({
        "text": "hello",
        "algorithm": "md5"
    })
    assert len(result) == 1
    assert "MD5" in result[0].text
    # MD5는 32자리 16진수
    assert "5d41402abc4b2a76b9719d911017c592" in result[0].text


@pytest.mark.asyncio
async def test_hash_generator_sha1():
    """SHA1 해시 생성 테스트"""
    result = await handle_hash_generator({
        "text": "hello",
        "algorithm": "sha1"
    })
    assert len(result) == 1
    assert "SHA1" in result[0].text
    # SHA1은 40자리 16진수
    assert "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d" in result[0].text


@pytest.mark.asyncio
async def test_hash_generator_sha512():
    """SHA512 해시 생성 테스트"""
    result = await handle_hash_generator({
        "text": "hello",
        "algorithm": "sha512"
    })
    assert len(result) == 1
    assert "SHA512" in result[0].text
    # SHA512는 128자리 16진수
    assert len([c for c in result[0].text if c in '0123456789abcdef']) >= 128


@pytest.mark.asyncio
async def test_hash_generator_invalid_algorithm():
    """지원하지 않는 알고리즘 테스트"""
    with pytest.raises(ValueError):
        await handle_hash_generator({
            "text": "hello",
            "algorithm": "invalid"
        })


@pytest.mark.asyncio
async def test_hash_generator_default():
    """기본 알고리즘(SHA256) 테스트"""
    result = await handle_hash_generator({
        "text": "hello"
    })
    assert len(result) == 1
    assert "SHA256" in result[0].text or "sha256" in result[0].text.lower()


@pytest.mark.asyncio
async def test_hash_generator_empty_string():
    """빈 문자열 해시 테스트"""
    result = await handle_hash_generator({
        "text": "",
        "algorithm": "sha256"
    })
    assert len(result) == 1
    # 빈 문자열의 SHA256
    assert "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" in result[0].text
