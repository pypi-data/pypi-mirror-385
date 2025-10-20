# Claude Desktop 설정 예시

## 방법 1: uvx 사용 (NPX 스타일 - 권장)
가장 간단하고 npx와 유사한 방식입니다.

```json
{
  "mcpServers": {
    "poly-mcp-server": {
      "command": "uvx",
      "args": ["poly-mcp-server"]
    }
  }
}
```

## 방법 2: 로컬 개발 버전
개발 중인 로컬 버전을 사용할 때:

```json
{
  "mcpServers": {
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

## 설정 파일 위치

### Windows
`%APPDATA%\Claude\claude_desktop_config.json`

### macOS
`~/Library/Application Support/Claude/claude_desktop_config.json`

### Linux
`~/.config/Claude/claude_desktop_config.json`
