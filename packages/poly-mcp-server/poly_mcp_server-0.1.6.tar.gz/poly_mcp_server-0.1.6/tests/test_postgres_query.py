"""PostgreSQL 쿼리 도구 테스트"""

import os
import pytest
from unittest.mock import patch, MagicMock
from poly_mcp_server.server import handle_postgres_query


@pytest.mark.asyncio
async def test_postgres_query_security_check():
    """SELECT 쿼리만 허용되는지 테스트"""
    # INSERT 시도 (거부되어야 함)
    with pytest.raises(ValueError, match="SELECT 쿼리만 허용"):
        await handle_postgres_query({"query": "INSERT INTO users VALUES (1, 'test')"})
    
    # DELETE 시도 (거부되어야 함)
    with pytest.raises(ValueError, match="SELECT 쿼리만 허용"):
        await handle_postgres_query({"query": "DELETE FROM users WHERE id=1"})
    
    # UPDATE 시도 (거부되어야 함)
    with pytest.raises(ValueError, match="SELECT 쿼리만 허용"):
        await handle_postgres_query({"query": "UPDATE users SET name='test'"})
    
    # DROP 시도 (거부되어야 함)
    with pytest.raises(ValueError, match="SELECT 쿼리만 허용"):
        await handle_postgres_query({"query": "DROP TABLE users"})


@pytest.mark.asyncio
async def test_postgres_query_missing_credentials():
    """환경변수 누락 시 오류 메시지 테스트"""
    # 환경변수 제거
    env_vars = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    original_values = {var: os.environ.get(var) for var in env_vars}
    
    try:
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
        
        with pytest.raises(ValueError, match="연결 정보가 설정되지 않았습니다"):
            await handle_postgres_query({"query": "SELECT 1"})
    
    finally:
        # 환경변수 복원
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value


@pytest.mark.asyncio
async def test_postgres_query_with_mock():
    """Mock을 사용한 쿼리 실행 테스트"""
    # 환경변수 설정
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_PORT"] = "5432"
    os.environ["POSTGRES_DB"] = "testdb"
    os.environ["POSTGRES_USER"] = "testuser"
    os.environ["POSTGRES_PASSWORD"] = "testpass"
    
    # psycopg2 mock
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",), ("name",), ("age",)]
    mock_cursor.fetchmany.return_value = [
        (1, "Alice", 30),
        (2, "Bob", 25),
    ]
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    with patch("psycopg2.connect", return_value=mock_conn):
        result = await handle_postgres_query({
            "query": "SELECT id, name, age FROM users",
            "limit": 10
        })
        
        assert len(result) == 1
        assert "2개 행" in result[0].text
        assert "Alice" in result[0].text
        assert "Bob" in result[0].text
        assert "id" in result[0].text
        assert "name" in result[0].text
        assert "age" in result[0].text


@pytest.mark.asyncio
async def test_postgres_query_empty_result():
    """빈 결과 테스트"""
    # 환경변수 설정
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_PORT"] = "5432"
    os.environ["POSTGRES_DB"] = "testdb"
    os.environ["POSTGRES_USER"] = "testuser"
    os.environ["POSTGRES_PASSWORD"] = "testpass"
    
    # psycopg2 mock - 빈 결과
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",), ("name",)]
    mock_cursor.fetchmany.return_value = []
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    with patch("psycopg2.connect", return_value=mock_conn):
        result = await handle_postgres_query({
            "query": "SELECT * FROM users WHERE id = 999",
        })
        
        assert len(result) == 1
        assert "데이터가 없습니다" in result[0].text


@pytest.mark.asyncio
async def test_postgres_query_limit():
    """LIMIT 제한 테스트"""
    # 환경변수 설정
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_PORT"] = "5432"
    os.environ["POSTGRES_DB"] = "testdb"
    os.environ["POSTGRES_USER"] = "testuser"
    os.environ["POSTGRES_PASSWORD"] = "testpass"
    
    # psycopg2 mock - 정확히 limit만큼 반환
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",)]
    mock_cursor.fetchmany.return_value = [(i,) for i in range(5)]
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    with patch("psycopg2.connect", return_value=mock_conn):
        result = await handle_postgres_query({
            "query": "SELECT id FROM users",
            "limit": 5
        })
        
        assert len(result) == 1
        assert "5개 행" in result[0].text
        assert "5개로 제한" in result[0].text


@pytest.mark.asyncio
async def test_postgres_query_connection_error():
    """DB 연결 오류 테스트"""
    # 환경변수 설정
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_PORT"] = "5432"
    os.environ["POSTGRES_DB"] = "testdb"
    os.environ["POSTGRES_USER"] = "testuser"
    os.environ["POSTGRES_PASSWORD"] = "testpass"
    
    # psycopg2 연결 오류 mock
    with patch("psycopg2.connect", side_effect=Exception("Connection refused")):
        with pytest.raises(ValueError, match="PostgreSQL 오류"):
            await handle_postgres_query({
                "query": "SELECT 1",
            })
