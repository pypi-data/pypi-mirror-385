# CDMN MCP Server 사용 가이드 (호출측 LLM용)

## 개요

CDMN MCP Server는 완전히 제네릭한 방식으로 의사결정 규칙을 실행하는 서버입니다. 이 가이드는 호출측 LLM이 이 서버를 효과적으로 사용하는 방법을 설명합니다.

## 주요 특징

- **제네릭 입력**: 고정된 스키마 대신 key-value 형태의 유연한 입력
- **규칙 기반**: 다양한 의사결정 규칙을 동일한 방식으로 처리
- **스키마 조회**: 각 규칙의 입력 요구사항을 동적으로 확인 가능
- **추적 가능**: 의사결정 과정을 단계별로 추적

## 사용 가능한 도구

### 1. `list_rules()` -> List[str]
사용 가능한 규칙 목록을 조회합니다.

### 2. `get_rule_schema(rule_name: str)` -> Dict[str, Any]
특정 규칙의 입력 스키마를 조회합니다.

### 3. `infer_decision(rule_name: str, context_input: Union[str, Dict[str, Any]])` -> Dict[str, Any]
의사결정을 실행합니다.

### 4. `parse_natural_language(text: str)` -> Dict[str, Any]
자연어를 구조화된 데이터로 변환합니다.

## 사용 패턴

### 패턴 1: 규칙 조회 후 실행

```python
# 1. 사용 가능한 규칙 조회
rules = await list_rules()
print(f"Available rules: {rules}")

# 2. 특정 규칙의 스키마 조회
schema = await get_rule_schema("insurance_premium")
print(f"Schema: {schema}")

# 3. 의사결정 실행
result = await infer_decision("insurance_premium", {
    "age": 30,
    "gender": "male",
    "smoker": True,
    "health_score": 75
})
```

### 패턴 2: 자연어 입력 처리

```python
# 자연어 입력을 구조화된 데이터로 변환
parsed = await parse_natural_language("30세 남자이고 흡연자야. 건강 점수는 75야.")

# 변환된 데이터로 의사결정 실행
result = await infer_decision("insurance_premium", parsed)
```

## 결과 데이터 구조

```json
{
    "result": {
        "total_score": 65,
        "category": "Medium",
        "premium": 75000,
        "rule_name": "insurance_premium"
    },
    "trace": [
        {
            "step": 1,
            "rule": "나이 위험도 (중간)",
            "condition": {"age": {"min": 40, "max": 59}},
            "result": "+15",
            "matched": true
        },
        {
            "step": 2,
            "rule": "흡연 위험도",
            "condition": {"smoker": true},
            "result": "+40",
            "matched": true
        }
    ],
    "input_context": {
        "age": 30,
        "gender": "male",
        "smoker": true,
        "health_score": 75
    },
    "rule_name": "insurance_premium",
    "execution_time": 0.001,
    "rule_schema": {
        "description": "보험료 계산 규칙",
        "required_fields": ["age", "gender", "smoker"],
        "optional_fields": ["health_score", "income", "vehicle_age", "credit_score"]
    }
}
```

## 마크다운 생성 가이드

호출측 LLM은 다음과 같은 구조로 마크다운을 생성해야 합니다:

### 기본 구조

```markdown
## 🧠 Decision Path: [규칙명]

### 입력 정보
| 항목 | 값 |
|------|-----|
| [필드명] | [값] |

### 의사결정 과정
1. **[규칙명]**: [조건] → [결과]
2. **[규칙명]**: [조건] → [결과]

### 최종 결과
- **[결과키]**: [값]
- **[결과키]**: [값]

---
✅ **Final Decision**: [최종결과]
```

### 예시: 보험료 계산

```markdown
## 🧠 Decision Path: 보험료 산정

### 입력 정보
| 항목 | 값 |
|------|-----|
| 나이 | 30세 |
| 성별 | 남성 |
| 흡연여부 | 예 |
| 건강점수 | 75점 |

### 의사결정 과정
1. **나이 위험도 (중간)**: 40-59세 → +15점
2. **흡연 위험도**: 흡연자 → +40점
3. **건강 위험도**: 75점 (양호) → +0점

### 최종 결과
- **총 점수**: 55점
- **위험도 분류**: Medium
- **계산된 보험료**: ₩75,000

---
✅ **Final Decision**: Medium Risk, ₩75,000
```

## 에러 처리

서버는 다음과 같은 에러 상황을 처리합니다:

- **규칙 없음**: `{"error": "Rule 'unknown_rule' not configured"}`
- **실행 실패**: `{"error": "Rule execution failed: [상세오류]"}`
- **파싱 실패**: `{"error": "Error parsing natural language: [상세오류]"}`

## 모범 사례

1. **항상 스키마를 먼저 확인**: `get_rule_schema()`로 입력 요구사항 확인
2. **자연어 처리 활용**: 복잡한 입력은 `parse_natural_language()` 사용
3. **결과 검증**: `trace` 배열로 의사결정 과정 검증
4. **에러 처리**: `error` 필드 확인 후 적절한 메시지 제공
5. **마크다운 생성**: 일관된 구조와 이모지 사용

## 확장 가능성

새로운 규칙을 추가하려면:

1. `register_rule()` 도구 사용
2. 규칙 설정에 `type`, `schema`, `rules`, `thresholds` 포함
3. 제네릭 규칙 엔진이 자동으로 처리

이러한 방식으로 MCP 서버는 완전히 제네릭하고 확장 가능한 의사결정 플랫폼이 됩니다.
