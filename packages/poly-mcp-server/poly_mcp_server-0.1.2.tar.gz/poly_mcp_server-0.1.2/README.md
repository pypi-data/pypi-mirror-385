# Poly MCP Server

다양한 유틸리티 도구를 제공하는 Model Context Protocol (MCP) 서버입니다.

## 설치

### pip로 설치:
```bash
pip install poly-mcp-server
```

### 또는 uv로 로컬 설치:
```bash
uv pip install -e .
```

### 또는 uv를 사용하여 직접 실행:
```bash
uv run poly-mcp-server
```

## 지원하는 도구

### 1. 계산기 (calculator)
기본 수학 계산을 수행합니다.
- **입력**: `expression` - 계산할 수학 표현식 (예: "2 + 3 * 4")
- **예시**: "10 + 5 * 2" → 20

### 2. 텍스트 분석기 (text_analyzer)  
텍스트의 다양한 통계 정보를 분석합니다.
- **입력**: 
  - `text` - 분석할 텍스트
  - `language` - 텍스트 언어 (ko, en 등, 기본값: ko)
- **결과**: 글자 수, 단어 수, 문장 수, 문장당 평균 단어 수

### 3. UUID 생성기 (uuid_generator)
UUID를 생성합니다.
- **입력**:
  - `version` - UUID 버전 (v1, v4, 기본값: v4)  
  - `count` - 생성할 UUID 개수 (기본값: 1)

### 4. 타임스탬프 변환기 (timestamp_converter)
타임스탬프를 다양한 형식으로 변환합니다.
- **입력**:
  - `timestamp` - 변환할 타임스탬프 또는 날짜 문자열
  - `format` - 출력 형식 (iso, unix, korean 등, 기본값: iso)
- **지원 입력**: Unix 타임스탬프 (초/밀리초), 일반 날짜 문자열

### 5. 해시 생성기 (hash_generator)
문자열의 해시값을 생성합니다.
- **입력**:
  - `text` - 해시할 텍스트
  - `algorithm` - 해시 알고리즘 (md5, sha1, sha256, sha512, 기본값: sha256)

## 개발

### 로컬 개발 환경 설정

```bash
git clone <repository-url>
cd poly-mcp-server

# uv를 사용한 설치
uv pip install -e ".[dev]"
```

### 테스트 실행

```bash
# 모든 테스트 실행
uv run pytest

# 특정 테스트 파일 실행
uv run pytest tests/test_calculator.py

# 상세 출력과 함께 실행
uv run pytest -v

# 커버리지와 함께 실행
uv run pytest --cov=poly_mcp_server
```

### 직접 실행

```bash
# uv를 통해 실행
uv run poly-mcp-server

# 또는 Python 모듈로 실행
uv run python -m poly_mcp_server.server
```

## MCP 클라이언트와 연결

### Claude Desktop 설정

Claude Desktop에서 이 서버를 사용하려면 설정 파일을 수정해야 합니다.

#### Windows
설정 파일 위치: `%APPDATA%\Claude\claude_desktop_config.json`

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

또는 전역 설치된 경우:
```json
{
  "mcpServers": {
    "poly-mcp-server": {
      "command": "poly-mcp-server"
    }
  }
}
```

#### macOS
설정 파일 위치: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "poly-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/poly-mcp-server",
        "run",
        "poly-mcp-server"
      ]
    }
  }
}
```

#### Linux
설정 파일 위치: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "poly-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/poly-mcp-server",
        "run",
        "poly-mcp-server"
      ]
    }
  }
}
```

### VSCode에서 사용하기

VSCode에서 MCP 서버를 사용하려면 워크스페이스 설정에 추가하세요.

#### 현재 프로젝트에서 사용 (이미 설정됨)
`.vscode/settings.json` 파일에 다음과 같이 설정되어 있습니다:

```json
{
  "mcp.servers": {
    "poly-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "${workspaceFolder}",
        "run",
        "poly-mcp-server"
      ]
    }
  }
}
```

#### 다른 프로젝트에서 사용하기

##### 방법 1: uvx로 직접 실행 (권장)
`uvx`를 사용하면 npx처럼 패키지를 자동으로 다운로드하고 실행합니다:

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

또는 PyPI에 배포된 경우:
```json
{
  "mcp.servers": {
    "poly-mcp-server": {
      "command": "uvx",
      "args": ["--from", "poly-mcp-server", "poly-mcp-server"]
    }
  }
}
```

##### 방법 2: 로컬 개발 버전 사용
개발 중인 로컬 버전을 사용하려면:

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

##### 방법 3: 전역 설치 후 사용
```bash
# 전역 설치
uv tool install poly-mcp-server

# 그 다음 settings.json에:
```

```json
{
  "mcp.servers": {
    "poly-mcp-server": {
      "command": "poly-mcp-server"
    }
  }
}
```

**참고**: 
- VSCode MCP 확장이 설치되어 있어야 합니다
- `uvx` 방식이 가장 간단하고 npx와 유사합니다
- Windows에서는 경로 구분자로 `/` 또는 `\\`을 사용할 수 있습니다

### Claude Desktop에서 사용하기

#### 방법 1: uvx로 직접 실행 (가장 간단, npx 스타일)

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

#### 방법 2: 로컬 개발 버전 사용

다른 프로젝트의 `.mcp.json` 또는 `mcp.json` 파일에 다음과 같이 추가:

```json
{
  "mcpServers": {
    "poly-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "절대/경로/to/poly-mcp-server",
        "run",
        "poly-mcp-server"
      ],
      "env": {}
    }
  }
}
```

**참고**: 
- `--directory` 경로는 반드시 **절대 경로**를 사용하세요
- Windows에서는 경로 구분자로 `/` 또는 `\\`을 사용할 수 있습니다
- `mcp-config.example.json` 파일을 복사하여 경로만 수정하면 됩니다

### 설정 후 확인

1. Claude Desktop을 재시작합니다
2. 채팅에서 도구 아이콘(🔧)을 클릭하여 `poly-mcp-server`가 표시되는지 확인합니다
3. 사용 가능한 도구: calculator, text_analyzer, uuid_generator, timestamp_converter, hash_generator

## 라이센스

MIT

## 기여

버그 리포트나 기능 제안은 GitHub Issues를 통해 해주세요.