# pyDMNrules MCP Server 설정 가이드

## 빠른 시작

### 1. 의존성 설치

```bash
cd /Users/uengine/dmn_mcp/pyDMNrules
pip install -r requirements_mcp.txt
```

### 2. 테스트 실행

서버가 올바르게 작동하는지 확인:

```bash
python3 test_mcp_with_simulation.py
```

성공적으로 실행되면 다음과 같은 출력이 나타납니다:
- ✓ Rule 'simulation' loaded successfully
- ✓ 의사결정 실행 성공
- ✓ Dish 일치

### 3. Claude Desktop 설정

#### macOS

1. Claude Desktop 설정 파일 열기:
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

또는 다음 명령으로 디렉토리 열기:
```bash
open ~/Library/Application\ Support/Claude/
```

2. 다음 내용을 추가:
```json
{
  "mcpServers": {
    "pydmnrules": {
      "command": "python3",
      "args": [
        "/Users/uengine/dmn_mcp/pyDMNrules/pydmnrules_mcp_server.py"
      ]
    }
  }
}
```

3. Claude Desktop 재시작

#### Windows

1. 설정 파일 위치: `%APPDATA%\Claude\claude_desktop_config.json`

2. 다음 내용을 추가:
```json
{
  "mcpServers": {
    "pydmnrules": {
      "command": "python",
      "args": [
        "C:\\Users\\YourUsername\\dmn_mcp\\pyDMNrules\\pydmnrules_mcp_server.py"
      ]
    }
  }
}
```

3. Claude Desktop 재시작

### 4. 가상환경 사용 (권장)

가상환경을 사용하는 경우:

```json
{
  "mcpServers": {
    "pydmnrules": {
      "command": "/Users/uengine/dmn_mcp/pyDMNrules/venv/bin/python3",
      "args": [
        "/Users/uengine/dmn_mcp/pyDMNrules/pydmnrules_mcp_server.py"
      ]
    }
  }
}
```

## Claude에서 사용하기

### 예제 1: 규칙 저장

```
나에게 나이에 따라 카테고리를 분류하는 DMN 규칙을 만들어줘:
- 18세 미만: Minor
- 18-65세: Adult
- 65세 초과: Senior

그리고 "age_category"라는 이름으로 저장해줘.
```

### 예제 2: 규칙 목록 확인

```
현재 저장된 DMN 규칙들을 보여줘.
```

### 예제 3: 스키마 확인

```
simulation 규칙의 입력 스키마를 보여줘.
```

### 예제 4: 의사결정 실행

```
simulation 규칙을 사용해서 다음 상황의 추천 요리와 음료를 알려줘:
- 계절: Fall
- 손님 수: 4명
- 아이 동반: 예
```

Claude가 자동으로:
1. `get_rule_schema`를 호출하여 정확한 변수 이름 확인
2. 올바른 형식으로 입력 데이터 구성
3. `infer_decision`을 호출하여 결과 반환

## 문제 해결

### 서버가 시작되지 않음

1. Python 버전 확인:
```bash
python3 --version
```
Python 3.8 이상이어야 합니다.

2. 의존성 확인:
```bash
pip list | grep -E "fastmcp|pydmnrules|pydantic|aiofiles"
```

3. 서버 직접 실행 테스트:
```bash
cd /Users/uengine/dmn_mcp/pyDMNrules
python3 pydmnrules_mcp_server.py
```

### pyDMNrules를 찾을 수 없음

```bash
pip install pydmnrules-enhanced
```

### Variable not in Glossary 에러

이 에러는 입력 데이터의 키 이름이 Glossary의 Variable 이름과 일치하지 않을 때 발생합니다.

해결 방법:
1. `get_rule_schema`를 먼저 호출하여 정확한 Variable 이름 확인
2. `variable_names` 리스트에 있는 정확한 이름 사용 (공백, 대소문자 포함)

예시:
```python
# ✗ 틀린 예
{"season": "Fall", "guestCount": 4}

# ✓ 올바른 예
{"Season": "Fall", "How many guests": 4}
```

### Claude Desktop에서 도구가 보이지 않음

1. Claude Desktop 완전히 종료 후 재시작
2. 설정 파일 경로 확인:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
3. JSON 문법 오류 확인
4. 절대 경로 사용 확인

### MCP 서버 로그 확인

macOS/Linux:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

Windows:
```powershell
Get-Content "$env:APPDATA\Claude\logs\mcp*.log" -Wait
```

## 고급 사용법

### 규칙 직접 저장

DMN XML 파일이 있는 경우:

```bash
cd /Users/uengine/dmn_mcp/pyDMNrules
cp your_rule.dmn rules/
```

그런 다음 Claude에서:
```
"your_rule" 규칙을 로드해줘.
```

### 여러 규칙 관리

rules 디렉토리에 여러 DMN 파일을 저장할 수 있습니다:

```
rules/
├── discount_rules.dmn
├── pricing_rules.dmn
├── validation_rules.dmn
└── simulation.dmn
```

### 스키마 기반 입력 생성

Claude에게 스키마를 먼저 확인하도록 요청:

```
"discount_rules"의 스키마를 확인하고,
고객이 "Business"이고 주문 크기가 100일 때의 할인을 계산해줘.
```

Claude가 자동으로:
1. 스키마 조회
2. 필요한 입력 필드 확인
3. 올바른 형식으로 입력 구성
4. 의사결정 실행

## API 참고

### load_rule(rule_name: str) -> str
규칙 로드

### save_rule(rule_name: str, xml_content: str) -> str
규칙 저장

### list_rules() -> List[str]
규칙 목록 조회

### delete_rule(rule_name: str) -> str
규칙 삭제

### get_rule_schema(rule_name: str) -> Dict
스키마 조회 (가장 중요!)

### infer_decision(rule_name: str, context_input: Dict) -> Dict
의사결정 실행

### check_engine_status() -> Dict
엔진 상태 확인

## 추가 리소스

- [pyDMNrules 문서](https://pydmnrules.readthedocs.io/)
- [DMN 표준](https://www.omg.org/dmn/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 지원

문제가 발생하면 다음을 확인하세요:

1. 테스트 스크립트 실행: `python3 test_mcp_with_simulation.py`
2. 서버 직접 실행: `python3 pydmnrules_mcp_server.py`
3. 로그 확인
4. 의존성 재설치: `pip install -r requirements_mcp.txt --force-reinstall`


