#!/usr/bin/env python3
"""
Poly MCP Server - 다양한 유틸리티 도구를 제공하는 MCP 서버
"""

import asyncio
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult, INVALID_PARAMS, INTERNAL_ERROR


# 서버 인스턴스 생성
app = Server("poly-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """사용 가능한 도구 목록을 반환합니다."""
    return [
        Tool(
            name="calculator",
            description="기본 수학 계산을 수행합니다 (덧셈, 뺄셈, 곱셈, 나눗셈)",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "계산할 수학 표현식 (예: '2 + 3 * 4')",
                    }
                },
                "required": ["expression"],
            },
        ),
        Tool(
            name="text_analyzer",
            description="텍스트 분석 도구 (글자 수, 단어 수, 문장 수 등)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "분석할 텍스트",
                    },
                    "language": {
                        "type": "string",
                        "description": "텍스트 언어 (ko, en 등)",
                        "default": "ko",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="uuid_generator",
            description="UUID를 생성합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "version": {
                        "type": "string",
                        "description": "UUID 버전 (v1, v4)",
                        "default": "v4",
                    },
                    "count": {
                        "type": "integer",
                        "description": "생성할 UUID 개수",
                        "default": 1,
                    },
                },
            },
        ),
        Tool(
            name="timestamp_converter",
            description="타임스탬프를 다양한 형식으로 변환합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "description": "변환할 타임스탬프 또는 날짜 문자열",
                    },
                    "format": {
                        "type": "string",
                        "description": "출력 형식 (iso, unix, korean 등)",
                        "default": "iso",
                    },
                },
                "required": ["timestamp"],
            },
        ),
        Tool(
            name="hash_generator",
            description="문자열의 해시값을 생성합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "해시할 텍스트",
                    },
                    "algorithm": {
                        "type": "string",
                        "description": "해시 알고리즘 (md5, sha1, sha256, sha512)",
                        "default": "sha256",
                    },
                },
                "required": ["text"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """도구를 호출하고 결과를 반환합니다."""
    try:
        if name == "calculator":
            return await handle_calculator(arguments)
        elif name == "text_analyzer":
            return await handle_text_analyzer(arguments)
        elif name == "uuid_generator":
            return await handle_uuid_generator(arguments)
        elif name == "timestamp_converter":
            return await handle_timestamp_converter(arguments)
        elif name == "hash_generator":
            return await handle_hash_generator(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        raise RuntimeError(f"Tool execution failed: {str(e)}")


async def handle_calculator(args: dict) -> list[TextContent]:
    """계산기 도구를 처리합니다."""
    expression = args.get("expression", "")
    
    # 안전한 수학 표현식만 허용
    allowed_chars = set("0123456789+-*/()%. ")
    if not all(c in allowed_chars for c in expression):
        raise ValueError(f"잘못된 수학 표현식입니다: {expression}")
    
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return [
            TextContent(
                type="text",
                text=f"계산 결과: {expression} = {result}"
            )
        ]
    except Exception as e:
        raise ValueError(f"계산 오류: {str(e)}")


async def handle_text_analyzer(args: dict) -> list[TextContent]:
    """텍스트 분석 도구를 처리합니다."""
    text = args.get("text", "")
    language = args.get("language", "ko")
    
    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
    
    if language == "ko":
        # 한국어: 공백, 구두점으로 단어 분리
        import re
        words = [w for w in re.split(r'[\s,，.。!！?？;；:：]+', text) if w]
        sentences = [s for s in re.split(r'[.。!！?？]+', text) if s.strip()]
    else:
        # 영어: 공백으로 단어 분리
        words = [w for w in text.split() if w]
        sentences = [s for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    word_count = len(words)
    sentence_count = len(sentences)
    avg_words = round(word_count / sentence_count, 1) if sentence_count > 0 else 0
    
    result = f"""텍스트 분석 결과:
📊 기본 통계:
- 전체 글자 수: {char_count}자
- 공백 제외 글자 수: {char_count_no_spaces}자
- 단어 수: {word_count}개
- 문장 수: {sentence_count}개
- 문장당 평균 단어 수: {avg_words}개

📝 언어: {'한국어' if language == 'ko' else '영어'}"""
    
    return [TextContent(type="text", text=result)]


async def handle_uuid_generator(args: dict) -> list[TextContent]:
    """UUID 생성기 도구를 처리합니다."""
    version = args.get("version", "v4")
    count = args.get("count", 1)
    
    uuids = []
    for _ in range(count):
        if version == "v1":
            uuids.append(str(uuid.uuid1()))
        else:  # v4
            uuids.append(str(uuid.uuid4()))
    
    result = f"생성된 UUID ({version}):\n" + "\n".join(uuids)
    return [TextContent(type="text", text=result)]


async def handle_timestamp_converter(args: dict) -> list[TextContent]:
    """타임스탬프 변환기 도구를 처리합니다."""
    timestamp_str = args.get("timestamp", "")
    format_type = args.get("format", "iso")
    
    # 타임스탬프 파싱
    try:
        if timestamp_str.isdigit():
            # Unix 타임스탬프
            ts_int = int(timestamp_str)
            if ts_int > 10000000000:  # 밀리초
                dt = datetime.fromtimestamp(ts_int / 1000, tz=timezone.utc)
            else:  # 초
                dt = datetime.fromtimestamp(ts_int, tz=timezone.utc)
        else:
            # ISO 형식 또는 일반 날짜 문자열
            from dateutil import parser
            dt = parser.parse(timestamp_str)
    except Exception as e:
        raise ValueError(f"잘못된 타임스탬프 형식입니다: {timestamp_str}")
    
    # 형식에 따라 변환
    if format_type == "iso":
        formatted = dt.isoformat()
    elif format_type == "unix":
        formatted = str(int(dt.timestamp()))
    elif format_type == "korean":
        formatted = dt.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
    else:
        formatted = str(dt)
    
    # 현재 시간과의 차이 계산
    now = datetime.now(timezone.utc)
    diff_seconds = (now - dt.replace(tzinfo=timezone.utc)).total_seconds()
    diff_days = int(diff_seconds / 86400)
    
    if diff_days > 0:
        time_diff = f"{diff_days}일 전"
    elif diff_days < 0:
        time_diff = f"{abs(diff_days)}일 후"
    else:
        time_diff = "오늘"
    
    result = f"""타임스탬프 변환 결과:
🕒 입력: {timestamp_str}
📅 변환된 시간: {formatted}
⏰ Unix 타임스탬프: {int(dt.timestamp())}
🌏 ISO 형식: {dt.isoformat()}
📊 현재로부터: {time_diff}"""
    
    return [TextContent(type="text", text=result)]


async def handle_hash_generator(args: dict) -> list[TextContent]:
    """해시 생성기 도구를 처리합니다."""
    text = args.get("text", "")
    algorithm = args.get("algorithm", "sha256").lower()
    
    valid_algorithms = ["md5", "sha1", "sha256", "sha512"]
    if algorithm not in valid_algorithms:
        raise ValueError(
            f"지원되지 않는 해시 알고리즘입니다. "
            f"지원 알고리즘: {', '.join(valid_algorithms)}"
        )
    
    # 해시 생성
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    hash_value = hash_obj.hexdigest()
    
    result = f"""해시 생성 결과:
📝 원본 텍스트: "{text}"
🔒 알고리즘: {algorithm.upper()}
🔑 해시값: {hash_value}
📏 길이: {len(hash_value)}자"""
    
    return [TextContent(type="text", text=result)]


def main():
    """메인 함수 - stdio로 서버를 실행합니다."""
    import sys
    from mcp.server.stdio import stdio_server
    
    # stderr로 로그 출력
    print("Poly MCP Server running on stdio", file=sys.stderr)
    sys.stderr.flush()
    
    # stdio 서버 실행
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
