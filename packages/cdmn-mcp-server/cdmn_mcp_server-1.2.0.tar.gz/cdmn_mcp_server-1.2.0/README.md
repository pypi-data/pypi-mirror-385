# CDMN Decision MCP Server

FastMCP 기반 DMN 서버로 자연어 입력을 받아 DMN 규칙을 실행하고 결과를 마크다운으로 반환하는 MCP 서버입니다.

## 🚀 Features

- **완전히 제네릭한 의사결정 엔진**: 고정된 스키마 없이 key-value 형태의 유연한 입력 처리
- **자연어 → DMN 호출 자동화**: LLM 기반 자연어 파싱으로 DMN 인퍼런스를 수행하고 결과를 반환
- **Rule 관리 기능**: DMN XML을 로드, 저장, 조회 가능
- **동적 스키마 조회**: 각 규칙의 입력 요구사항을 런타임에 확인 가능
- **경로 추적 기능**: DMN 실행 시 어떤 decision table과 rule row가 활성화되었는지 추적
- **호출측 LLM 최적화**: 마크다운 생성은 호출측 LLM에서 처리하도록 설계
- **확장 가능한 규칙 시스템**: 새로운 규칙을 동적으로 등록하고 실행 가능
- **MCP 프로토콜 준수**: FastMCP 기반으로 LLM에서 함수 호출 및 응답 처리 가능

## 📋 Requirements

- Python 3.11+
- FastMCP
- OpenAI API Key (자연어 파싱 및 마크다운 생성용)
- CDMN (Decision Model and Notation library)

## 🛠️ Installation

### Using pip

```bash
pip install -r requirements.txt
```

### Using uv (recommended)

```bash
uv pip install -r requirements.txt
```

### Using Docker

```bash
docker build -t cdmn-mcp-server .
docker run -p 8000:8000 cdmn-mcp-server
```

## 🚀 Usage

### 1. uvx를 사용한 MCP 서버 실행 (권장)

uvx를 사용하면 패키지를 설치하지 않고도 바로 실행할 수 있습니다.

#### MCP 설정 파일 생성

```json
{
  "mcpServers": {
    "cdmn-mcp-server": {
      "command": "uvx",
      "args": [
        "cdmn-mcp-server"
      ]
    }
  }
}
```

> **참고**: 이 MCP 서버는 직접 LLM을 사용하지 않습니다. 자연어 처리는 호출측 LLM이 `@prompt` 데코레이터를 통해 처리합니다.

#### uvx 설치 (필요한 경우)
```bash
# uv 설치 (uvx 포함)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 pip로 설치
pip install uv
```

#### MCP 클라이언트에서 사용
1. 위의 JSON 설정을 MCP 클라이언트 설정 파일에 추가
2. MCP 클라이언트 재시작
3. `cdmn-mcp-server` 도구들이 자동으로 사용 가능해집니다

### 2. pip를 사용한 설치 및 실행

```bash
# 패키지 설치
pip install cdmn-mcp-server

# 서버 실행
cdmn-mcp-server
```

### 3. 개발 모드 실행

```bash
# 기존 서버 (정규식 기반)
python server.py

# 리팩토링된 서버 (LLM 기반)
python server_refactored.py

# 완전히 제네릭한 서버 (권장)
python server_fully_generic.py
```

The server will start on `http://localhost:8000`

### MCP 도구 사용 예시

#### 기본 사용법

```python
# 1. 규칙 목록 조회
rules = await list_rules()
print(f"사용 가능한 규칙: {rules}")

# 2. 규칙 스키마 조회
schema = await get_rule_schema("insurance_premium")
print(f"스키마: {schema}")

# 3. 자연어 파싱 (호출측 LLM이 @prompt 사용)
# parse_natural_language는 규칙에 맞는 프롬프트를 반환하므로 호출측 LLM이 처리
prompt = await parse_natural_language("30세 남자이고 흡연자야. 건강 점수는 75야.", "insurance_premium")
# 호출측 LLM이 이 프롬프트를 사용하여 해당 규칙의 스키마에 맞는 JSON으로 변환

# 4. 의사결정 실행 (구조화된 데이터로)
input_data = {
    "age": 30,
    "gender": "male", 
    "smoker": True,
    "health_score": 75.0
}
result = await infer_decision("insurance_premium", input_data)
print(f"의사결정 결과: {result}")
```

#### 고급 사용법

```python
# 1. 새로운 규칙 등록
new_rule_config = {
    "type": "scoring",
    "schema": {
        "description": "신용도 평가 규칙",
        "required_fields": ["credit_score", "income"],
        "optional_fields": ["age", "employment_years"]
    },
    "rules": [
        {
            "description": "신용점수 우수",
            "condition": {"credit_score": {"min": 700}},
            "score": 50
        }
    ],
    "thresholds": {
        "Excellent": 80,
        "Good": 60,
        "Fair": 40
    }
}
await register_rule("credit_evaluation", new_rule_config)

# 2. 등록된 규칙 실행
test_input = {
    "credit_score": 750,
    "income": 60000,
    "age": 35
}
result = await infer_decision("credit_evaluation", test_input)
print(f"신용도 평가 결과: {result}")
```

### MCP Tools Available

#### 1. `load_rule(rule_name: str) -> str`
지정된 이름의 DMN XML 규칙을 로드합니다.

```python
# Example
result = await load_rule("insurance_premium")
```

#### 2. `save_rule(rule_name: str, xml_content: str) -> str`
새로운 DMN 규칙을 저장합니다.

```python
# Example
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/">
  <!-- DMN XML content -->
</definitions>"""
result = await save_rule("my_rule", xml_content)
```

#### 3. `list_rules() -> List[str]`
등록된 DMN 규칙 목록을 조회합니다.

```python
# Example
rules = await list_rules()
# Returns: ["insurance_premium", "loan_approval"]
```

#### 4. `delete_rule(rule_name: str) -> str`
DMN 규칙을 삭제합니다.

```python
# Example
result = await delete_rule("my_rule")
```

#### 5. `infer_decision(rule_name: str, context_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]`
지정된 DMN 규칙을 기반으로 의사결정을 실행합니다.

```python
# Natural language input
result = await infer_decision("insurance_premium", "30세 남자이고 흡연자야")

# Structured input
context = {
    "age": 30,
    "gender": "male",
    "smoker": True,
    "health_score": 75
}
result = await infer_decision("insurance_premium", context)
```

#### 6. `get_rule_schema(rule_name: str) -> Dict[str, Any]`
규칙의 입력 스키마를 조회합니다.

```python
# Example
schema = await get_rule_schema("insurance_premium")
# Returns: {"description": "보험료 계산 규칙", "required_fields": [...], ...}
```

#### 7. `register_rule(rule_name: str, rule_config: Dict[str, Any]) -> str`
새로운 규칙을 등록합니다.

```python
# Example
config = {
    "type": "scoring",
    "schema": {"description": "신용도 평가", ...},
    "rules": [...],
    "thresholds": {...}
}
await register_rule("credit_evaluation", config)
```

#### 8. `parse_natural_language(text: str, rule_name: str) -> str`
자연어 텍스트를 지정된 규칙의 스키마에 맞는 구조화된 컨텍스트로 변환하는 프롬프트를 반환합니다. 호출측 LLM이 이 프롬프트를 사용하여 자연어를 해당 규칙의 JSON으로 변환합니다.

```python
# Example
prompt = await parse_natural_language("30세 남자이고 흡연자야", "insurance_premium")
# Returns: 규칙 스키마에 맞는 프롬프트 텍스트
```

## 📁 Project Structure

```
dmn_mcp/
├── server.py                    # 기존 FastMCP 서버 (정규식 기반)
├── server_refactored.py         # 리팩토링된 FastMCP 서버 (LLM 기반)
├── server_fully_generic.py      # 완전히 제네릭한 FastMCP 서버 (권장)
├── business_rules/              # 비즈니스 로직 모듈 (레거시)
│   ├── __init__.py
│   ├── insurance.py            # 보험료 계산 로직
│   └── loan.py                 # 대출 승인 로직
├── prompts/                     # 프롬프트 템플릿
│   ├── __init__.py
│   ├── natural_language_parser.py
│   └── llm_usage_guide.md      # 호출측 LLM 사용 가이드
├── llm_client.py               # LLM 클라이언트 (OpenAI)
├── llm_client_mock.py          # Mock LLM 클라이언트
├── rules/                      # DMN XML 규칙 저장소
│   ├── insurance_premium.dmn.xml
│   └── loan_approval.dmn.xml
├── tests/                      # 테스트 코드
├── scripts/                    # 테스트 스크립트
├── pyproject.toml              # 프로젝트 설정
├── requirements.txt            # 의존성 목록
├── Dockerfile                  # Docker 설정
├── docker-compose.yml          # Docker Compose 설정
├── .gitignore                 # Git 무시 파일
└── README.md                  # 이 파일
```

## 🧪 Example Usage

### 1. 보험료 계산

```python
# 자연어 입력
result = await infer_decision("insurance_premium", "30세 남자이고 흡연자야")

# 결과
{
    "result": {
        "risk_category": "High",
        "risk_score": 55,
        "premium": 150000
    },
    "trace": [
        {"step": 1, "rule": "age_risk", "condition": "age > 40 (30)", "result": "+15"},
        {"step": 2, "rule": "smoker_risk", "condition": "smoker = true", "result": "+40"}
    ],
    "markdown_output": "## 🧠 Decision Path: 보험료 산정\n\n..."
}
```

### 2. 대출 승인

```python
# 구조화된 입력
context = {
    "credit_score": 750,
    "income": 60000,
    "age": 35
}
result = await infer_decision("loan_approval", context)

# 결과
{
    "result": {
        "approved": True,
        "approval_score": 90,
        "max_amount": 1000000,
        "interest_rate": 3.5
    },
    "trace": [...],
    "markdown_output": "## 🧠 Decision Path: 대출 승인\n\n..."
}
```

## 🔧 Configuration

### Environment Variables

- `PYTHONPATH`: Python 경로 설정
- `PYTHONUNBUFFERED`: Python 출력 버퍼링 비활성화

### Rules Directory

DMN XML 파일은 `rules/` 디렉토리에 저장되며, 파일명은 `{rule_name}.dmn.xml` 형식이어야 합니다.

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=server tests/
```

## 📊 Natural Language Processing

서버는 다음과 같은 자연어 패턴을 인식합니다:

### 나이
- "30세", "30살", "age: 30", "나이: 30"

### 성별
- "남자", "남성", "male", "남"
- "여자", "여성", "female", "여"

### 흡연 여부
- "흡연", "담배", "smoker", "smoking", "피움"
- "비흡연", "안 피움", "non-smoker", "non-smoking"

### 소득
- "소득: 50000", "income: 50000", "50000원", "50000달러"

### 건강 점수
- "건강 점수: 75", "health score: 75"

### 신용 점수
- "신용 점수: 750", "credit score: 750"

## 🚀 Future Enhancements

- [ ] DMN XML 시각화 UI (bpmn.io DMN Viewer 통합)
- [ ] 자연어 규칙 생성 (LLM → DMN XML)
- [ ] Trace to BPMN Mapping 기능
- [ ] Rule versioning (Git storage backend)
- [ ] 실제 CDMN 라이브러리 통합

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions, please open an issue on GitHub.
