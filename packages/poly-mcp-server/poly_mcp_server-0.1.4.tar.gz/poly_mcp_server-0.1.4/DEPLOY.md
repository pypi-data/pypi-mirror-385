# PyPI 배포 가이드

## 사전 준비

1. PyPI 계정 생성: https://pypi.org/account/register/
2. API 토큰 생성: https://pypi.org/manage/account/token/
3. `.env` 파일 생성:
   ```bash
   # .env.template을 복사
   cp .env.template .env
   
   # .env 파일을 열고 토큰 입력
   # UV_PUBLISH_TOKEN=pypi-YOUR_ACTUAL_TOKEN_HERE
   ```

## 배포 방법

### 간단한 방법 (자동 스크립트)
```powershell
# PowerShell에서 실행
.\deploy.ps1
```

이 스크립트는 자동으로:
1. ✅ 테스트 실행
2. 🔨 빌드
3. 🚀 PyPI 배포

### 수동 배포

### 1. 패키지 빌드
```bash
uv build
```

이 명령은 `dist/` 디렉토리에 다음 파일들을 생성합니다:
- `poly_mcp_server-0.1.0.tar.gz` (소스 배포)
- `poly_mcp_server-0.1.0-py3-none-any.whl` (휠 배포)

### 2. TestPyPI에 먼저 배포 (권장)
실제 PyPI에 배포하기 전에 테스트:

```bash
# TestPyPI 배포
uv publish --publish-url https://test.pypi.org/legacy/
```

설치 테스트:
```bash
uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ poly-mcp-server
```

### 3. PyPI에 배포
```bash
uv publish
```

또는 토큰 사용:
```bash
uv publish --token pypi-YOUR_API_TOKEN_HERE
```

### 4. 배포 확인
```bash
# 설치 테스트
uvx poly-mcp-server

# 또는
uv tool install poly-mcp-server
poly-mcp-server
```

## 배포 전 체크리스트

- [ ] 버전 번호 확인 (`pyproject.toml`의 `version`)
- [ ] README.md 업데이트
- [ ] 테스트 통과 확인 (`uv run pytest`)
- [ ] .gitignore에 `dist/`, `*.egg-info/` 추가
- [ ] GitHub 저장소 URL 업데이트 (선택사항)
- [ ] LICENSE 파일 확인

## 새 버전 배포

1. `pyproject.toml`에서 버전 업데이트
2. 변경사항 커밋
3. Git 태그 생성: `git tag v0.1.1`
4. 빌드 및 배포: `uv build && uv publish`

## 주의사항

⚠️ **한번 배포한 버전은 삭제할 수 없습니다!**
- 같은 버전 번호로 재배포 불가
- 실수로 배포했다면 버전을 올려서 다시 배포해야 함
- 그래서 TestPyPI에서 먼저 테스트하는 것이 중요합니다

## 환경 변수 설정 (선택사항)

`.env` 파일 또는 시스템 환경 변수:
```bash
UV_PUBLISH_TOKEN=pypi-YOUR_API_TOKEN_HERE
```

그러면 `uv publish` 실행 시 자동으로 토큰 사용
