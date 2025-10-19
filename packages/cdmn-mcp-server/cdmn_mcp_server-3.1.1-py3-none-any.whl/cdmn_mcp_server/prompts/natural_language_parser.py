"""
자연어 파싱을 위한 프롬프트 템플릿
"""

NATURAL_LANGUAGE_PARSING_PROMPT = """
당신은 자연어 텍스트를 구조화된 JSON 데이터로 변환하는 전문가입니다.

사용자가 입력한 자연어 텍스트를 분석하여 다음 JSON 형식으로 변환해주세요:

{
    "age": 나이 (숫자, 없으면 null),
    "gender": 성별 ("male" 또는 "female", 없으면 null),
    "smoker": 흡연여부 (true 또는 false, 없으면 null),
    "income": 소득 (숫자, 없으면 null),
    "health_score": 건강점수 (숫자, 없으면 null),
    "vehicle_age": 차량연식 (숫자, 없으면 null),
    "credit_score": 신용점수 (숫자, 없으면 null),
    "employment_years": 근무년수 (숫자, 없으면 null),
    "debt_to_income_ratio": 부채소득비율 (숫자, 없으면 null)
}

파싱 규칙:
1. 나이: "30세", "30살", "age: 30", "나이: 30" 등에서 추출
2. 성별: "남자", "남성", "male", "남" → "male" / "여자", "여성", "female", "여" → "female"
3. 흡연: "흡연", "담배", "smoker", "smoking", "피움" → true / "비흡연", "안 피움", "non-smoker" → false
4. 소득: "소득은 50000", "income: 50000", "50000원", "50000달러" 등에서 추출
5. 건강점수: "건강 점수는 75", "health score: 75" 등에서 추출
6. 신용점수: "신용 점수는 750", "credit score: 750" 등에서 추출
7. 차량연식: "차량 연식은 5년", "vehicle age: 5" 등에서 추출
8. 근무년수: "5년 근무", "employment: 5 years" 등에서 추출
9. 부채소득비율: "부채소득비율은 0.3", "debt ratio: 0.3" 등에서 추출

입력 텍스트: "{text}"

JSON 응답만 반환하고 다른 설명은 포함하지 마세요:
"""

MARKDOWN_GENERATION_PROMPT = """
당신은 의사결정 결과를 마크다운으로 시각화하는 전문가입니다.

다음 정보를 바탕으로 마크다운 형식의 결과를 생성해주세요:

결과 타입: {result_type}
입력 정보: {input_info}
의사결정 과정: {decision_trace}
최종 결과: {final_result}

마크다운 형식:
- 제목은 "## 🧠 Decision Path: [결과타입]" 형식으로 작성
- 입력 정보는 "### 입력 정보" 섹션에 표로 정리
- 의사결정 과정은 "### 의사결정 과정" 섹션에 단계별로 나열
- 최종 결과는 "### 최종 결과" 섹션에 요약
- 마지막에 "---" 구분선과 함께 "✅ **Final Decision**" 요약 추가

이모지와 마크다운 포맷팅을 적절히 사용하여 가독성 좋게 작성해주세요.
"""
