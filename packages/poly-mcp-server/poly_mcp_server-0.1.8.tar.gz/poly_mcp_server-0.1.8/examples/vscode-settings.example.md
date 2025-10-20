# VSCode MCP 설정 예시

## 방법 1: uvx 사용 (NPX 스타일 - 권장)
```json
{
  "mcp.servers": {
    "poly-mcp-server": {
      "command": "uvx",
      "args": ["poly-mcp-server"]
    }
  }
}
```

## 방법 2: 로컬 개발 버전
```json
{
  "mcp.servers": {
    "poly-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "D:/Development/workspace/vscode/study/poly-mcp",
        "run",
        "poly-mcp-server"
      ]
    }
  }
}
```

## 방법 3: 전역 설치
먼저 설치:
```bash
uv tool install poly-mcp-server
```

그 다음 설정:
```json
{
  "mcp.servers": {
    "poly-mcp-server": {
      "command": "poly-mcp-server"
    }
  }
}
```
