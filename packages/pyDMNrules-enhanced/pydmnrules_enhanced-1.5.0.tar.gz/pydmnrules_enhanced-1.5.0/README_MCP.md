# pyDMNrules MCP Server

pyDMNrules 엔진을 사용하여 DMN XML 파일을 로드하고 의사결정을 실행하는 MCP (Model Context Protocol) 서버입니다.

[![PyPI version](https://badge.fury.io/py/pydmnrules-mcp-server.svg)](https://badge.fury.io/py/pydmnrules-mcp-server)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 특징

- **DMN XML 지원**: DMN 1.1/1.2/1.3 표준 XML 파일 로드 및 실행
- **규칙 관리**: DMN 규칙의 저장, 로드, 삭제, 목록 조회
- **스키마 자동 추출**: LLM이 이해할 수 있는 입력/출력 스키마 제공
- **의사결정 추적**: 실행된 규칙과 결과에 대한 상세한 trace 정보 제공
- **FastMCP 기반**: 빠르고 안정적인 MCP 서버 구현

## 빠른 시작

### PyPI에서 설치 (권장) 🚀

```bash
pip install pydmnrules-mcp-server
```

이 명령 하나로 모든 의존성이 자동으로 설치됩니다!

### 개발 버전 설치

```bash
pip install -r requirements_mcp.txt
```

또는 개별 설치:

```bash
pip install fastmcp pydantic aiofiles pydmnrules-enhanced
```

### 2. 서버 실행 확인

```bash
# PyPI 설치 후
pydmnrules-mcp-server

# 또는 Python 모듈로
python -m pydmnrules_mcp.server

# 또는 개발 버전
python pydmnrules_mcp_server.py
```

## 사용법

### 서버 실행

```bash
# PyPI 설치 후 (가장 간단)
pydmnrules-mcp-server

# Python 모듈로
python -m pydmnrules_mcp.server

# 개발 버전
python pydmnrules_mcp_server.py
```

### Claude Desktop 설정

Claude Desktop에서 사용하려면 설정 파일에 추가하세요:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### 방법 1: uvx 사용 (권장) ⭐

```json
{
  "mcpServers": {
    "pydmnrules": {
      "command": "uvx",
      "args": ["pydmnrules-mcp-server"]
    }
  }
}
```

**장점**: 
- 설치 불필요
- 자동으로 격리된 환경에서 실행
- 빠른 속도

**사전 요구사항**: [uv 설치](https://github.com/astral-sh/uv)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

자세한 내용: [UVX_SETUP_GUIDE.md](UVX_SETUP_GUIDE.md)

#### 방법 2: pip 설치 후 직접 실행

```json
{
  "mcpServers": {
    "pydmnrules": {
      "command": "pydmnrules-mcp-server"
    }
  }
}
```

**사전 요구사항**: `pip install pydmnrules-mcp-server`

#### 방법 3: Python 모듈로 실행

```json
{
  "mcpServers": {
    "pydmnrules": {
      "command": "python",
      "args": ["-m", "pydmnrules_mcp.server"]
    }
  }
}
```

#### 방법 4: 개발 버전 사용

```json
{
  "mcpServers": {
    "pydmnrules": {
      "command": "python",
      "args": ["/path/to/pydmnrules_mcp_server.py"]
    }
  }
}
```

## MCP Tools

서버는 다음 6개의 tool을 제공합니다:

### 1. `load_rule`

저장된 DMN 규칙을 로드합니다.

**Parameters**:
- `rule_name` (string): 로드할 규칙의 이름 (확장자 제외)

**Returns**: 로드 결과 메시지

**Example**:
```python
load_rule(rule_name="discount_rules")
```

### 2. `save_rule`

새로운 DMN 규칙을 저장합니다.

**Parameters**:
- `rule_name` (string): 저장할 규칙의 이름
- `xml_content` (string): DMN XML 내용

**Returns**: 저장 결과 메시지

**Example**:
```python
save_rule(
    rule_name="discount_rules",
    xml_content="<?xml version='1.0' encoding='UTF-8'?>..."
)
```

### 3. `list_rules`

등록된 DMN 규칙 목록을 조회합니다.

**Returns**: 규칙 이름 목록

**Example**:
```python
rules = list_rules()
# Returns: ["discount_rules", "pricing_rules", ...]
```

### 4. `delete_rule`

DMN 규칙을 삭제합니다.

**Parameters**:
- `rule_name` (string): 삭제할 규칙의 이름

**Returns**: 삭제 결과 메시지

**Example**:
```python
delete_rule(rule_name="old_rules")
```

### 5. `get_rule_schema`

규칙의 입력/출력 스키마를 조회합니다. LLM이 올바른 형식으로 입력을 구성할 수 있도록 도와줍니다.

**Parameters**:
- `rule_name` (string): 규칙 이름

**Returns**: 스키마 정보 (inputs, outputs, decision_tables 등)

**Example**:
```python
schema = get_rule_schema(rule_name="discount_rules")
# Returns:
# {
#   "rule_name": "discount_rules",
#   "engine_type": "pyDMNrules",
#   "inputs": {
#     "Customer": {"description": "Customer.sector", "type": "string", "required": true},
#     "OrderSize": {"description": "Order.orderSize", "type": "string", "required": true}
#   },
#   "outputs": {
#     "Discount": {"description": "Discount.discount", "type": "string"}
#   },
#   "decision_tables": [
#     {"name": "DiscountDecision", "hit_policy": "U", "description": "..."}
#   ],
#   "example_input": {
#     "Customer": null,
#     "OrderSize": null
#   }
# }
```

### 6. `infer_decision`

DMN 규칙을 실행하여 의사결정을 수행합니다.

**Parameters**:
- `rule_name` (string): 사용할 DMN 규칙의 이름
- `context_input` (dict): key-value 딕셔너리 형태의 입력 데이터

**Returns**: 의사결정 결과

**Example**:
```python
result = infer_decision(
    rule_name="discount_rules",
    context_input={
        "Customer": "Business",
        "OrderSize": 15
    }
)
# Returns:
# {
#   "result": {
#     "final_result": {"Discount": 0.15, ...},
#     "all_results": [...],
#     "decision_count": 1
#   },
#   "trace": [
#     {"step": 1, "action": "input", "data": {...}},
#     {"step": 2, "action": "decision_table", "table": "DiscountDecision", "rule_id": "1", ...}
#   ],
#   "input_context": {"Customer": "Business", "OrderSize": 15},
#   "rule_name": "discount_rules",
#   "execution_time": 0.023,
#   "rule_schema": {...},
#   "engine_used": "pyDMNrules"
# }
```

### 7. `check_engine_status`

엔진의 상태를 확인합니다.

**Returns**: 엔진 상태 정보

**Example**:
```python
status = check_engine_status()
# Returns:
# {
#   "pydmnrules_available": true,
#   "message": "pyDMNrules Engine - Available: True",
#   "loaded_models": ["discount_rules", "pricing_rules"],
#   "total_loaded_models": 2,
#   "rules_directory": "/path/to/rules"
# }
```

## Claude와 함께 사용하기

### 1. DMN 규칙 저장

```
나에게 고객 유형과 주문 크기에 따라 할인율을 결정하는 DMN 규칙을 만들어줘.
그리고 "discount_rules"라는 이름으로 저장해줘.
```

Claude가 DMN XML을 생성하고 `save_rule`을 호출합니다.

### 2. 규칙 로드 및 스키마 확인

```
discount_rules의 입력 스키마를 보여줘.
```

Claude가 `get_rule_schema`를 호출하여 어떤 입력이 필요한지 확인합니다.

### 3. 의사결정 실행

```
고객이 "Business"이고 주문 크기가 15일 때 할인율을 계산해줘.
discount_rules를 사용해.
```

Claude가 적절한 형태로 입력을 구성하고 `infer_decision`을 호출합니다.

### 4. 규칙 관리

```
현재 저장된 모든 규칙을 보여줘.
```

Claude가 `list_rules`를 호출합니다.

## DMN XML 파일 형식

pyDMNrules는 다음 형식의 DMN XML 파일을 지원합니다:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/"
             xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/"
             xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/"
             id="Definitions_discount"
             name="Discount Decision"
             namespace="http://camunda.org/schema/1.0/dmn">
  
  <decision id="Decision_discount" name="Discount">
    <decisionTable id="DecisionTable_discount">
      <input id="Input_1" label="Customer">
        <inputExpression id="InputExpression_1" typeRef="string">
          <text>Customer</text>
        </inputExpression>
      </input>
      <input id="Input_2" label="Order Size">
        <inputExpression id="InputExpression_2" typeRef="number">
          <text>OrderSize</text>
        </inputExpression>
      </input>
      <output id="Output_1" label="Discount" name="discount" typeRef="number"/>
      
      <rule id="Rule_1">
        <inputEntry id="InputEntry_1">
          <text>"Business"</text>
        </inputEntry>
        <inputEntry id="InputEntry_2">
          <text>&gt;= 10</text>
        </inputEntry>
        <outputEntry id="OutputEntry_1">
          <text>0.15</text>
        </outputEntry>
      </rule>
      
      <!-- More rules... -->
    </decisionTable>
  </decision>
</definitions>
```

## 예제

예제 DMN 파일들이 프로젝트 디렉토리에 포함되어 있습니다:

- `Example1.xlsx` - Excel 형식 DMN 규칙
- `ExampleHPV.xlsx` - HPV 검사 의사결정 규칙
- `Therapy.xlsx` - 치료 추천 규칙
- `simulation.dmn` - 시뮬레이션 DMN XML

Excel 파일을 사용하는 경우, pyDMNrules의 `load()` 메서드를 사용할 수 있습니다.

## 디렉토리 구조

```
pyDMNrules/
├── pydmnrules_mcp_server.py  # MCP 서버 메인 파일
├── requirements_mcp.txt       # 의존성 목록
├── README_MCP.md             # 이 파일
├── rules/                    # DMN 규칙 저장 디렉토리
│   ├── discount_rules.dmn
│   ├── pricing_rules.dmn
│   └── ...
└── pyDMNrules/              # pyDMNrules 엔진
    └── DMNrules.py
```

## 트러블슈팅

### pyDMNrules를 찾을 수 없음

```bash
pip install pydmnrules-enhanced
```

### XML 파싱 에러

- DMN XML이 유효한지 확인하세요
- XML 네임스페이스가 올바른지 확인하세요
- pyDMNrules가 지원하는 DMN 버전(1.1/1.2/1.3)인지 확인하세요

### 규칙 실행 에러

- `get_rule_schema`로 필요한 입력 필드를 확인하세요
- 입력 데이터 타입이 스키마와 일치하는지 확인하세요
- Glossary의 Variable 이름과 일치하는지 확인하세요

## 라이선스

이 프로젝트는 pyDMNrules의 라이선스를 따릅니다.

## 관련 링크

- [pyDMNrules GitHub](https://github.com/russellmcdonell/pyDMNrules)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)

