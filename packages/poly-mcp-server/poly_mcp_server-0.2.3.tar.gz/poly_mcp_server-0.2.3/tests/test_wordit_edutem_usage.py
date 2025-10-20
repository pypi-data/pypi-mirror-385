"""Test cases for Wordit Edutem usage tool"""
import pytest
from unittest.mock import patch, MagicMock
from poly_mcp_server.server import handle_wordit_edutem_usage


@pytest.mark.asyncio
async def test_wordit_edutem_usage_requires_start_date():
    """Test that start_date is required"""
    with pytest.raises(Exception):
        await handle_wordit_edutem_usage({})


@pytest.mark.asyncio
async def test_wordit_edutem_usage_validates_date_format():
    """Test that invalid date format is rejected"""
    with pytest.raises(Exception):
        await handle_wordit_edutem_usage({"start_date": "invalid-date"})


@pytest.mark.asyncio
@patch('psycopg2.connect')
async def test_wordit_edutem_usage_requires_db_credentials(mock_connect):
    """Test that database credentials are required"""
    mock_connect.side_effect = ValueError("Database credentials not set")
    
    with pytest.raises(Exception):
        await handle_wordit_edutem_usage({"start_date": "2025-09-01"})
