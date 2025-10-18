#!/usr/bin/env python3
"""
CDMN Decision MCP Server - Fully Generic Version

FastMCP 기반 DMN 서버로 자연어 입력을 받아 DMN 규칙을 실행하고
결과 데이터를 반환하는 MCP 서버입니다. (완전히 제네릭한 방식)
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# LLM 클라이언트 제거 - 호출측 LLM이 @prompt로 처리


class DecisionResult(BaseModel):
    """의사결정 결과를 나타내는 모델 (완전히 제네릭)"""
    result: Dict[str, Any] = Field(description="의사결정 결과")
    trace: List[Dict[str, Any]] = Field(description="의사결정 경로 추적")
    input_context: Dict[str, Any] = Field(description="입력 컨텍스트 (key-value)")
    rule_name: str = Field(description="사용된 규칙 이름")
    execution_time: Optional[float] = Field(None, description="실행 시간 (초)")
    rule_schema: Optional[Dict[str, Any]] = Field(None, description="규칙별 입력 스키마")


class GenericRuleEngine:
    """제네릭 규칙 엔진 - 모든 규칙을 동일한 방식으로 처리"""
    
    def __init__(self):
        # 규칙별 설정을 외부에서 주입받을 수 있도록 구성
        self.rule_configs = {}
    
    def register_rule(self, rule_name: str, config: Dict[str, Any]):
        """규칙을 등록합니다"""
        self.rule_configs[rule_name] = config
    
    async def execute_rule(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """규칙을 실행합니다 (제네릭)"""
        import time
        start_time = time.time()
        
        if rule_name not in self.rule_configs:
            execution_time = time.time() - start_time
            return DecisionResult(
                result={"error": f"Rule '{rule_name}' not configured"},
                trace=[{"step": 1, "rule": "error", "condition": "rule_not_found", "result": "error"}],
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema={"error": "Rule not configured"}
            )
        
        config = self.rule_configs[rule_name]
        
        try:
            # 제네릭 규칙 실행 로직
            result = await self._execute_generic_rule(rule_name, input_context, config)
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            return DecisionResult(
                result={"error": f"Rule execution failed: {str(e)}"},
                trace=[{"step": 1, "rule": "error", "condition": "execution_failed", "result": str(e)}],
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema=config.get("schema", {})
            )
    
    async def _execute_generic_rule(self, rule_name: str, input_context: Dict[str, Any], config: Dict[str, Any]) -> DecisionResult:
        """제네릭 규칙 실행"""
        # 규칙 타입에 따라 다른 처리
        rule_type = config.get("type", "generic")
        
        if rule_type == "scoring":
            return await self._execute_scoring_rule(rule_name, input_context, config)
        elif rule_type == "classification":
            return await self._execute_classification_rule(rule_name, input_context, config)
        elif rule_type == "calculation":
            return await self._execute_calculation_rule(rule_name, input_context, config)
        else:
            return await self._execute_generic_rule_default(rule_name, input_context, config)
    
    async def _execute_scoring_rule(self, rule_name: str, input_context: Dict[str, Any], config: Dict[str, Any]) -> DecisionResult:
        """스코어링 규칙 실행"""
        rules = config.get("rules", [])
        trace = []
        total_score = 0
        
        for i, rule in enumerate(rules, 1):
            condition = rule.get("condition", {})
            score = rule.get("score", 0)
            description = rule.get("description", f"Rule {i}")
            
            # 조건 평가 (간단한 예시)
            if self._evaluate_condition(input_context, condition):
                total_score += score
                trace.append({
                    "step": i,
                    "rule": description,
                    "condition": condition,
                    "result": f"+{score}",
                    "matched": True
                })
            else:
                trace.append({
                    "step": i,
                    "rule": description,
                    "condition": condition,
                    "result": "+0",
                    "matched": False
                })
        
        # 최종 결과 결정
        thresholds = config.get("thresholds", {})
        result_category = self._determine_category(total_score, thresholds)
        
        result = {
            "total_score": total_score,
            "category": result_category,
            "thresholds": thresholds,
            "rule_name": rule_name
        }
        
        # 추가 결과 필드들
        if "additional_fields" in config:
            for field_name, field_config in config["additional_fields"].items():
                result[field_name] = self._calculate_additional_field(input_context, field_config)
        
        return DecisionResult(
            result=result,
            trace=trace,
            input_context=input_context,
            rule_name=rule_name,
            rule_schema=config.get("schema", {})
        )
    
    async def _execute_classification_rule(self, rule_name: str, input_context: Dict[str, Any], config: Dict[str, Any]) -> DecisionResult:
        """분류 규칙 실행"""
        rules = config.get("rules", [])
        trace = []
        
        for i, rule in enumerate(rules, 1):
            condition = rule.get("condition", {})
            classification = rule.get("classification", "unknown")
            description = rule.get("description", f"Rule {i}")
            
            if self._evaluate_condition(input_context, condition):
                trace.append({
                    "step": i,
                    "rule": description,
                    "condition": condition,
                    "result": classification,
                    "matched": True
                })
                
                return DecisionResult(
                    result={
                        "classification": classification,
                        "matched_rule": i,
                        "rule_name": rule_name
                    },
                    trace=trace,
                    input_context=input_context,
                    rule_name=rule_name,
                    rule_schema=config.get("schema", {})
                )
            else:
                trace.append({
                    "step": i,
                    "rule": description,
                    "condition": condition,
                    "result": "no_match",
                    "matched": False
                })
        
        # 기본 분류
        default_classification = config.get("default_classification", "unknown")
        return DecisionResult(
            result={
                "classification": default_classification,
                "matched_rule": None,
                "rule_name": rule_name
            },
            trace=trace,
            input_context=input_context,
            rule_name=rule_name,
            rule_schema=config.get("schema", {})
        )
    
    async def _execute_calculation_rule(self, rule_name: str, input_context: Dict[str, Any], config: Dict[str, Any]) -> DecisionResult:
        """계산 규칙 실행"""
        formula = config.get("formula", {})
        trace = []
        
        # 기본값 설정
        base_value = formula.get("base_value", 0)
        multipliers = formula.get("multipliers", {})
        adjustments = formula.get("adjustments", [])
        
        result_value = base_value
        trace.append({
            "step": 1,
            "rule": "base_value",
            "condition": "initialization",
            "result": f"base: {base_value}"
        })
        
        # 승수 적용
        for field, multiplier in multipliers.items():
            if field in input_context:
                value = input_context[field]
                adjustment = value * multiplier
                result_value += adjustment
                trace.append({
                    "step": len(trace) + 1,
                    "rule": f"{field}_multiplier",
                    "condition": f"{field} = {value}",
                    "result": f"+{adjustment} (x{multiplier})"
                })
        
        # 조정값 적용
        for adjustment in adjustments:
            condition = adjustment.get("condition", {})
            value = adjustment.get("value", 0)
            
            if self._evaluate_condition(input_context, condition):
                result_value += value
                trace.append({
                    "step": len(trace) + 1,
                    "rule": adjustment.get("description", "adjustment"),
                    "condition": condition,
                    "result": f"+{value}"
                })
        
        return DecisionResult(
            result={
                "calculated_value": result_value,
                "base_value": base_value,
                "rule_name": rule_name
            },
            trace=trace,
            input_context=input_context,
            rule_name=rule_name,
            rule_schema=config.get("schema", {})
        )
    
    async def _execute_generic_rule_default(self, rule_name: str, input_context: Dict[str, Any], config: Dict[str, Any]) -> DecisionResult:
        """기본 제네릭 규칙 실행"""
        # 단순히 입력을 그대로 반환하는 기본 구현
        return DecisionResult(
            result={
                "processed_input": input_context,
                "rule_name": rule_name,
                "message": "Generic rule executed"
            },
            trace=[{
                "step": 1,
                "rule": "generic",
                "condition": "default",
                "result": "processed"
            }],
            input_context=input_context,
            rule_name=rule_name,
            rule_schema=config.get("schema", {})
        )
    
    def _evaluate_condition(self, input_context: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """조건을 평가합니다 (제네릭)"""
        if not condition:
            return True
        
        for field, expected in condition.items():
            if field not in input_context:
                return False
            
            actual = input_context[field]
            
            # 간단한 비교 로직
            if isinstance(expected, dict):
                if "min" in expected and actual < expected["min"]:
                    return False
                if "max" in expected and actual > expected["max"]:
                    return False
                if "equals" in expected and actual != expected["equals"]:
                    return False
                if "in" in expected and actual not in expected["in"]:
                    return False
            else:
                if actual != expected:
                    return False
        
        return True
    
    def _determine_category(self, score: float, thresholds: Dict[str, Any]) -> str:
        """점수에 따라 카테고리를 결정합니다"""
        if not thresholds:
            return "unknown"
        
        # 임계값을 점수 순으로 정렬
        sorted_thresholds = sorted(thresholds.items(), key=lambda x: x[1], reverse=True)
        
        for category, threshold in sorted_thresholds:
            if score >= threshold:
                return category
        
        return "lowest"
    
    def _calculate_additional_field(self, input_context: Dict[str, Any], field_config: Dict[str, Any]) -> Any:
        """추가 필드를 계산합니다"""
        field_type = field_config.get("type", "value")
        
        if field_type == "value":
            return field_config.get("value")
        elif field_type == "lookup":
            lookup_table = field_config.get("lookup_table", {})
            key = input_context.get(field_config.get("key_field", ""))
            return lookup_table.get(key, field_config.get("default", 0))
        elif field_type == "calculation":
            formula = field_config.get("formula", "0")
            # 간단한 수식 계산 (실제로는 더 복잡한 파서가 필요)
            try:
                return eval(formula, {"input": input_context})
            except:
                return 0
        
        return None


class DMNModel:
    """DMN 모델을 관리하는 클래스 (제네릭)"""
    
    def __init__(self, rules_dir: str = "rules"):
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(exist_ok=True)
        self._models: Dict[str, Any] = {}
        self.rule_engine = GenericRuleEngine()
        
        # 기본 규칙들 등록
        self._register_default_rules()
    
    def _register_default_rules(self):
        """기본 규칙들을 등록합니다"""
        # 보험료 계산 규칙
        self.rule_engine.register_rule("insurance_premium", {
            "type": "scoring",
            "schema": {
                "description": "보험료 계산 규칙",
                "required_fields": ["age", "gender", "smoker"],
                "optional_fields": ["health_score", "income", "vehicle_age", "credit_score"],
                "field_types": {
                    "age": "integer",
                    "gender": "string (male/female)",
                    "smoker": "boolean",
                    "health_score": "float (0-100)",
                    "income": "float",
                    "vehicle_age": "integer",
                    "credit_score": "integer"
                }
            },
            "rules": [
                {
                    "description": "나이 위험도",
                    "condition": {"age": {"min": 60}},
                    "score": 30
                },
                {
                    "description": "나이 위험도 (중간)",
                    "condition": {"age": {"min": 40, "max": 59}},
                    "score": 15
                },
                {
                    "description": "흡연 위험도",
                    "condition": {"smoker": True},
                    "score": 40
                },
                {
                    "description": "건강 위험도",
                    "condition": {"health_score": {"max": 49}},
                    "score": 25
                }
            ],
            "thresholds": {
                "High": 70,
                "Medium": 40,
                "Low": 0
            },
            "additional_fields": {
                "premium": {
                    "type": "calculation",
                    "formula": "50000 + (input.get('total_score', 0) - 40) * 1000"
                }
            }
        })
        
        # 대출 승인 규칙
        self.rule_engine.register_rule("loan_approval", {
            "type": "scoring",
            "schema": {
                "description": "대출 승인 규칙",
                "required_fields": ["credit_score", "income", "age"],
                "optional_fields": ["employment_years", "debt_to_income_ratio"],
                "field_types": {
                    "credit_score": "integer (300-850)",
                    "income": "float (annual income)",
                    "age": "integer",
                    "employment_years": "integer",
                    "debt_to_income_ratio": "float (0-1)"
                }
            },
            "rules": [
                {
                    "description": "신용점수 우수",
                    "condition": {"credit_score": {"min": 700}},
                    "score": 40
                },
                {
                    "description": "신용점수 양호",
                    "condition": {"credit_score": {"min": 600, "max": 699}},
                    "score": 25
                },
                {
                    "description": "신용점수 보통",
                    "condition": {"credit_score": {"min": 500, "max": 599}},
                    "score": 10
                },
                {
                    "description": "소득 높음",
                    "condition": {"income": {"min": 50000}},
                    "score": 30
                },
                {
                    "description": "소득 중간",
                    "condition": {"income": {"min": 30000, "max": 49999}},
                    "score": 20
                },
                {
                    "description": "나이 최적",
                    "condition": {"age": {"min": 25, "max": 65}},
                    "score": 20
                }
            ],
            "thresholds": {
                "Approved": 60,
                "Rejected": 0
            },
            "additional_fields": {
                "max_amount": {
                    "type": "calculation",
                    "formula": "min(input.get('income', 0) * 5, 1000000)"
                },
                "interest_rate": {
                    "type": "calculation",
                    "formula": "3.5 + (100 - input.get('total_score', 0)) * 0.1"
                }
            }
        })
    
    async def load_rule(self, rule_name: str) -> str:
        """DMN 규칙을 로드합니다"""
        rule_file = self.rules_dir / f"{rule_name}.dmn.xml"
        
        if not rule_file.exists():
            raise FileNotFoundError(f"Rule '{rule_name}' not found")
        
        async with aiofiles.open(rule_file, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # XML 파싱 (간단한 검증)
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            self._models[rule_name] = root
            return f"Rule '{rule_name}' loaded successfully"
        except ET.ParseError as e:
            raise ValueError(f"Invalid DMN XML: {e}")
    
    async def save_rule(self, rule_name: str, xml_content: str) -> str:
        """DMN 규칙을 저장합니다"""
        rule_file = self.rules_dir / f"{rule_name}.dmn.xml"
        
        # XML 유효성 검사
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ValueError(f"Invalid DMN XML: {e}")
        
        async with aiofiles.open(rule_file, 'w', encoding='utf-8') as f:
            await f.write(xml_content)
        
        return f"Rule '{rule_name}' saved successfully"
    
    async def list_rules(self) -> List[str]:
        """저장된 규칙 목록을 반환합니다"""
        if not self.rules_dir.exists():
            return []
        
        rules = []
        for file_path in self.rules_dir.glob("*.dmn.xml"):
            rules.append(file_path.stem.replace(".dmn", ""))
        
        return sorted(rules)
    
    async def delete_rule(self, rule_name: str) -> str:
        """DMN 규칙을 삭제합니다"""
        rule_file = self.rules_dir / f"{rule_name}.dmn.xml"
        
        if not rule_file.exists():
            raise FileNotFoundError(f"Rule '{rule_name}' not found")
        
        rule_file.unlink()
        
        if rule_name in self._models:
            del self._models[rule_name]
        
        return f"Rule '{rule_name}' deleted successfully"
    
    async def get_rule_schema(self, rule_name: str) -> Dict[str, Any]:
        """규칙의 입력 스키마를 반환합니다"""
        if rule_name in self.rule_engine.rule_configs:
            return self.rule_engine.rule_configs[rule_name].get("schema", {})
        else:
            return {
                "description": f"Unknown rule: {rule_name}",
                "required_fields": [],
                "optional_fields": [],
                "field_types": {},
                "examples": {}
            }
    
    async def evaluate_decision(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """DMN 규칙을 실행하여 의사결정을 수행합니다"""
        return await self.rule_engine.execute_rule(rule_name, input_context)


# FastMCP 서버 초기화
mcp = FastMCP("cdmn-mcp-server")
dmn_model = DMNModel()


@mcp.tool()
async def load_rule(rule_name: str) -> str:
    """
    지정된 이름의 DMN XML 규칙을 로드합니다.
    
    Args:
        rule_name: 로드할 규칙의 이름 (확장자 제외)
    
    Returns:
        로드 결과 메시지
    """
    try:
        return await dmn_model.load_rule(rule_name)
    except Exception as e:
        return f"Error loading rule '{rule_name}': {str(e)}"


@mcp.tool()
async def save_rule(rule_name: str, xml_content: str) -> str:
    """
    새로운 DMN 규칙을 저장합니다.
    
    Args:
        rule_name: 저장할 규칙의 이름
        xml_content: DMN XML 내용
    
    Returns:
        저장 결과 메시지
    """
    try:
        return await dmn_model.save_rule(rule_name, xml_content)
    except Exception as e:
        return f"Error saving rule '{rule_name}': {str(e)}"


@mcp.tool()
async def list_rules() -> List[str]:
    """
    등록된 DMN 규칙 목록을 조회합니다.
    
    Returns:
        규칙 이름 목록
    """
    try:
        return await dmn_model.list_rules()
    except Exception as e:
        return [f"Error listing rules: {str(e)}"]


@mcp.tool()
async def delete_rule(rule_name: str) -> str:
    """
    DMN 규칙을 삭제합니다.
    
    Args:
        rule_name: 삭제할 규칙의 이름
    
    Returns:
        삭제 결과 메시지
    """
    try:
        return await dmn_model.delete_rule(rule_name)
    except Exception as e:
        return f"Error deleting rule '{rule_name}': {str(e)}"


@mcp.tool()
async def get_rule_schema(rule_name: str) -> Dict[str, Any]:
    """
    규칙의 입력 스키마를 조회합니다.
    
    Args:
        rule_name: 규칙 이름
    
    Returns:
        규칙의 입력 스키마 (필수/선택 필드, 타입, 예시 포함)
    """
    try:
        return await dmn_model.get_rule_schema(rule_name)
    except Exception as e:
        return {"error": f"Error getting schema for rule '{rule_name}': {str(e)}"}


@mcp.tool()
async def register_rule(rule_name: str, rule_config: Dict[str, Any]) -> str:
    """
    새로운 규칙을 등록합니다.
    
    Args:
        rule_name: 규칙 이름
        rule_config: 규칙 설정 (type, schema, rules, thresholds 등)
    
    Returns:
        등록 결과 메시지
    """
    try:
        dmn_model.rule_engine.register_rule(rule_name, rule_config)
        return f"Rule '{rule_name}' registered successfully"
    except Exception as e:
        return f"Error registering rule '{rule_name}': {str(e)}"


@mcp.tool()
async def infer_decision(rule_name: str, context_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    지정된 DMN 규칙을 기반으로 의사결정을 실행합니다.
    
    Args:
        rule_name: 사용할 DMN 규칙의 이름
        context_input: key-value 딕셔너리 형태의 입력 데이터
    
    Returns:
        의사결정 결과 (result, trace, input_context, rule_name, execution_time, rule_schema 포함)
    """
    try:
        # 의사결정 실행
        result = await dmn_model.evaluate_decision(rule_name, context_input)
        
        return {
            "result": result.result,
            "trace": result.trace,
            "input_context": result.input_context,
            "rule_name": result.rule_name,
            "execution_time": result.execution_time,
            "rule_schema": result.rule_schema
        }
    except Exception as e:
        return {
            "error": f"Error executing decision: {str(e)}",
            "result": {},
            "trace": [],
            "input_context": {},
            "rule_name": rule_name,
            "execution_time": 0,
            "rule_schema": None
        }


@mcp.prompt()
async def parse_natural_language(text: str, rule_name: str) -> str:
    """
    자연어 텍스트를 지정된 규칙의 스키마에 맞는 구조화된 컨텍스트로 변환하는 프롬프트입니다.
    호출측 LLM이 이 프롬프트를 사용하여 자연어를 해당 규칙의 key-value 딕셔너리로 변환합니다.
    
    Args:
        text: 자연어 입력 텍스트
        rule_name: 대상 규칙 이름 (스키마를 결정하기 위해 사용)
    
    Returns:
        자연어를 구조화된 데이터로 변환하는 프롬프트
    """
    try:
        # 규칙 스키마 조회
        schema = await dmn_model.get_rule_schema(rule_name)
        
        if not schema or 'input_schema' not in schema:
            return f"""
다음 자연어 텍스트를 구조화된 key-value 딕셔너리로 변환해주세요:

입력 텍스트: "{text}"

규칙 '{rule_name}'의 스키마 정보를 찾을 수 없습니다. 일반적인 필드들을 추출하여 JSON 형태로 반환해주세요.

JSON만 반환하고 다른 설명은 포함하지 마세요.
"""
        
        input_schema = schema['input_schema']
        
        # 스키마 기반 필드 설명 생성
        field_descriptions = []
        for field_name, field_info in input_schema.items():
            field_type = field_info.get('type', 'string')
            field_desc = field_info.get('description', f'{field_name} 필드')
            field_descriptions.append(f"- {field_name}: {field_desc} ({field_type})")
        
        fields_text = "\n".join(field_descriptions)
        
        return f"""
다음 자연어 텍스트를 구조화된 key-value 딕셔너리로 변환해주세요:

입력 텍스트: "{text}"

규칙 '{rule_name}'의 스키마에 맞춰 다음 필드들을 추출하여 JSON 형태로 반환해주세요:

{fields_text}

예시 출력:
{{
    "field1": "value1",
    "field2": 123,
    "field3": true
}}

JSON만 반환하고 다른 설명은 포함하지 마세요.
"""
        
    except Exception as e:
        return f"""
다음 자연어 텍스트를 구조화된 key-value 딕셔너리로 변환해주세요:

입력 텍스트: "{text}"

규칙 '{rule_name}' 처리 중 오류가 발생했습니다: {str(e)}

일반적인 필드들을 추출하여 JSON 형태로 반환해주세요.

JSON만 반환하고 다른 설명은 포함하지 마세요.
"""


def main():
    """메인 함수 - 서버 실행"""
    # stdio 모드로 실행
    mcp.run()


if __name__ == "__main__":
    main()