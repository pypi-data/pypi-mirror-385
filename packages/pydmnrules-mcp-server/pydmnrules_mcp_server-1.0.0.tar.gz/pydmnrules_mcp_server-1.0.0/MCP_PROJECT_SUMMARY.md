# pyDMNrules MCP Server - 프로젝트 요약

## 프로젝트 개요

pyDMNrules 엔진을 사용하여 DMN (Decision Model Notation) XML 파일을 로드하고 의사결정을 실행하는 FastMCP 기반 MCP 서버입니다.

### 주요 특징

✅ **DMN XML 지원**: DMN 1.1/1.2/1.3 표준 XML 파일 로드 및 실행  
✅ **규칙 관리**: 저장, 로드, 삭제, 목록 조회  
✅ **스키마 자동 추출**: LLM이 이해할 수 있는 입력/출력 스키마 제공  
✅ **의사결정 추적**: 실행 경로 및 결과에 대한 상세 trace  
✅ **FastMCP 기반**: 안정적이고 빠른 MCP 서버  

## 프로젝트 구조

```
pyDMNrules/
├── pydmnrules_mcp_server.py      # MCP 서버 메인 파일 ⭐
├── requirements_mcp.txt          # 의존성 목록
├── README_MCP.md                 # 사용자 문서
├── SETUP_GUIDE.md                # 설정 가이드
├── MCP_PROJECT_SUMMARY.md        # 이 파일
├── claude_desktop_config.json    # Claude Desktop 설정 예제
│
├── test_mcp_server.py            # 기본 테스트
├── test_mcp_with_simulation.py   # 완전한 테스트 ⭐
├── test_pydmnrules_direct.py     # pyDMNrules 직접 테스트
├── test_pydmnrules_direct2.py    # pyDMNrules 직접 테스트 (수정)
│
├── rules/                        # DMN 규칙 저장 디렉토리
│   └── simulation.dmn            # 예제 규칙
│
└── pyDMNrules/                   # pyDMNrules 엔진
    ├── __init__.py
    └── DMNrules.py
```

## 핵심 파일 설명

### 1. `pydmnrules_mcp_server.py` ⭐

MCP 서버의 메인 파일입니다. 다음을 포함합니다:

**클래스**:
- `PyDMNrulesEngine`: pyDMNrules 엔진을 감싸는 래퍼
- `DMNModel`: DMN 규칙 파일 관리
- `DecisionResult`: 의사결정 결과 데이터 모델

**MCP Tools (7개)**:
1. `load_rule` - 규칙 로드
2. `save_rule` - 규칙 저장
3. `list_rules` - 규칙 목록
4. `delete_rule` - 규칙 삭제
5. `get_rule_schema` - 스키마 조회 (중요!)
6. `infer_decision` - 의사결정 실행
7. `check_engine_status` - 엔진 상태

### 2. `test_mcp_with_simulation.py` ⭐

완전한 기능 테스트 스크립트입니다. 다음을 테스트합니다:
- 규칙 저장/로드
- 스키마 조회
- 의사결정 실행 (3가지 시나리오)
- 결과 검증

### 3. `requirements_mcp.txt`

필수 의존성:
```
fastmcp>=0.4.0
pydantic>=2.0.0
aiofiles>=23.0.0
pydmnrules-enhanced>=1.5.0
```

## 구현 세부사항

### 핵심 기능

#### 1. DMN XML 로드
```python
dmn_model = DMN()
status = dmn_model.useXML(xml_content)
```

pyDMNrules의 `useXML()` 메서드를 사용하여 XML 문자열로부터 규칙을 로드합니다.

#### 2. 메타데이터 추출
```python
def _extract_metadata(self, dmn_model: DMN, rule_name: str) -> Dict[str, Any]:
    """
    Glossary로부터 Variable 이름 추출
    Decision Tables 정보 추출
    입력/출력 필드 정보 구성
    """
```

**중요**: pyDMNrules는 XML의 input label을 Variable 이름으로 사용합니다.
- XML: `<input label="Season">` → Variable: `"Season"`
- XML: `<input label="How many guests">` → Variable: `"How many guests"` (공백 포함!)

#### 3. 스키마 제공
```python
{
    "rule_name": "simulation",
    "variable_names": ["Season", "How many guests", "Guests with children"],
    "important_note": "⚠️ Use EXACT variable names...",
    "inputs": {
        "Season": {
            "variable_name": "Season",
            "feel_name": "Data.Season",
            "type": "string",
            "required": true
        }
    }
}
```

LLM이 `variable_names`를 보고 정확한 키 이름을 사용할 수 있도록 합니다.

#### 4. 의사결정 실행
```python
(status, result_data) = dmn_model.decide(input_context)
```

pyDMNrules의 `decide()` 메서드를 호출하여 의사결정을 실행합니다.

#### 5. 결과 파싱
```python
def _parse_result(self, result_data: Any) -> Dict[str, Any]:
    """
    단일 decision 또는 여러 decision 처리
    Result, Executed Rule, Annotations 추출
    """
```

### 주요 도전과제 및 해결

#### 문제 1: Variable 이름 불일치

**문제**: 
```python
# ✗ 작동하지 않음
{"season": "Fall", "guestCount": 4}
```

**원인**: pyDMNrules의 Glossary에는 XML의 정확한 label이 저장됨

**해결**:
```python
# ✓ 작동함
{"Season": "Fall", "How many guests": 4}
```

스키마에 `variable_names` 리스트를 추가하고, `important_note`로 강조

#### 문제 2: 결과 구조 다양성

**문제**: pyDMNrules는 상황에 따라 다른 결과 구조 반환
- 단일 decision: `dict`
- 여러 decision: `list[dict]`

**해결**: `_parse_result()`에서 두 가지 경우 모두 처리

```python
if isinstance(result_data, list):
    return {
        "final_result": all_results[-1],
        "all_results": all_results,
        "decision_count": len(all_results)
    }
```

#### 문제 3: Trace 정보 구성

**문제**: pyDMNrules의 결과에서 실행 경로 추출

**해결**: `_build_trace()`에서 `Executed Rule` 정보 파싱

```python
if 'Executed Rule' in result_data:
    executed_rule = result_data['Executed Rule']
    # (description, table_name, rule_id) 튜플 파싱
```

## 테스트 결과

### simulation.dmn 테스트 (성공 ✅)

```bash
$ python3 test_mcp_with_simulation.py

테스트 케이스 1: Fall, 4 guests, with children
  ✓ 결과:
    Dish: Spareribs
    Beverages: ['Aecht Schlenkerla Rauchbier', 'Apple Juice']
    ✓ Dish 일치

테스트 케이스 2: Summer, 10 guests, no children
  ✓ 결과:
    Dish: Light Salad and a nice Steak
    Beverages: ['Water']
    ✓ Dish 일치

테스트 케이스 3: Winter, 2 guests, no children
  ✓ 결과:
    Dish: Roastbeef
    Beverages: ['Water']
    ✓ Dish 일치
```

## 사용 예제

### Claude와 함께 사용

#### 1. 스키마 확인 후 실행
```
Claude, simulation 규칙의 스키마를 먼저 확인하고,
가을에 4명이 방문하는데 아이가 있을 때 추천 요리와 음료를 알려줘.
```

Claude가 자동으로:
1. `get_rule_schema("simulation")` 호출
2. Variable 이름 확인: "Season", "How many guests", "Guests with children"
3. 올바른 형식으로 입력 구성:
   ```python
   {
       "Season": "Fall",
       "How many guests": 4,
       "Guests with children": True
   }
   ```
4. `infer_decision()` 호출
5. 결과 해석 및 제시

#### 2. 새 규칙 생성
```
고객 등급(Gold, Silver, Bronze)과 구매 금액에 따라 
할인율을 결정하는 DMN 규칙을 만들어줘.
"discount_rules"로 저장해.
```

Claude가:
1. DMN XML 생성
2. `save_rule("discount_rules", xml_content)` 호출
3. 저장 확인

## API 요약

### Tool: `get_rule_schema` (가장 중요!)

**왜 중요한가?**
- LLM이 올바른 입력 형식을 알 수 있음
- Variable 이름의 정확한 철자/대소문자/공백 확인 가능
- FEEL 표현식 이름도 제공

**반환 예시**:
```json
{
  "rule_name": "simulation",
  "engine_type": "pyDMNrules",
  "variable_names": ["Season", "How many guests", "Guests with children"],
  "important_note": "⚠️ Use EXACT variable names...",
  "inputs": {
    "Season": {
      "variable_name": "Season",
      "feel_name": "Data.Season",
      "description": "Data.Data.Season",
      "type": "string",
      "required": true
    }
  },
  "decision_tables": [
    {"name": "Dish", "hit_policy": "U"},
    {"name": "Beverages", "hit_policy": "C"}
  ],
  "example_input": {
    "Season": null,
    "How many guests": null,
    "Guests with children": null
  }
}
```

### Tool: `infer_decision`

**입력**:
```python
{
    "rule_name": "simulation",
    "context_input": {
        "Season": "Fall",
        "How many guests": 4,
        "Guests with children": True
    }
}
```

**출력**:
```python
{
    "result": {
        "final_result": {
            "Dish": "Spareribs",
            "Beverages": ["Aecht Schlenkerla Rauchbier", "Apple Juice"]
        },
        "all_results": [...],
        "decision_count": 2
    },
    "trace": [
        {"step": 1, "action": "input", "data": {...}},
        {"step": 2, "action": "decision_table", "table": "Dish", "rule_id": "Rule.1"},
        {"step": 3, "action": "decision_table", "table": "Beverages", ...}
    ],
    "input_context": {...},
    "rule_name": "simulation",
    "execution_time": 0.0035,
    "rule_schema": {...},
    "engine_used": "pyDMNrules"
}
```

## 설정 방법

### 1. 의존성 설치
```bash
cd /Users/uengine/dmn_mcp/pyDMNrules
pip install -r requirements_mcp.txt
```

### 2. 테스트
```bash
python3 test_mcp_with_simulation.py
```

### 3. Claude Desktop 설정

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

### 4. Claude Desktop 재시작

## 다음 단계

### 개선 가능한 점

1. **타입 정보 강화**
   - 현재: 모든 타입을 "string"으로 표시
   - 개선: DMN XML의 typeRef 활용

2. **입력/출력 구분**
   - 현재: 모든 Glossary 항목을 입력으로 간주
   - 개선: Decision Table 분석하여 실제 입력만 표시

3. **에러 메시지 개선**
   - pyDMNrules의 에러를 더 친화적으로 변환

4. **캐싱**
   - 로드된 규칙을 메모리에 캐싱하여 성능 향상

5. **Excel 지원**
   - pyDMNrules는 Excel도 지원하므로 추가 가능

## 결론

pyDMNrules MCP Server는 DMN XML 규칙을 LLM이 쉽게 사용할 수 있도록 하는 완전한 MCP 서버입니다.

**핵심 성공 요소**:
- ✅ pyDMNrules의 XML 로드 기능 활용
- ✅ Glossary에서 정확한 Variable 이름 추출
- ✅ LLM 친화적인 스키마 제공
- ✅ 상세한 실행 trace
- ✅ 포괄적인 테스트

**사용 준비 완료**:
- 모든 기능 테스트 완료
- 문서화 완료
- Claude Desktop 설정 가이드 제공

---

**작성일**: 2025-10-19  
**버전**: 1.0.0  
**엔진**: pyDMNrules  
**프레임워크**: FastMCP

