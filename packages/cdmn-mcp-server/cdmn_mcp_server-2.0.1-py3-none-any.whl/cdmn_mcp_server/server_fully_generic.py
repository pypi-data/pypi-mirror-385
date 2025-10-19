#!/usr/bin/env python3
"""
Hybrid DMN MCP Server - cDMN + Standard XML Support

cDMN 공식 API와 표준 XML 파싱을 모두 지원하는 하이브리드 MCP 서버입니다.
DMN XML 파일을 자동으로 감지하고 적절한 실행 엔진을 선택합니다.
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# cDMN 공식 API import
try:
    from cdmn.API import DMN
    CDMN_AVAILABLE = True
except ImportError:
    CDMN_AVAILABLE = False
    print("Warning: cDMN API not available. Using XML-only mode.")


class DecisionResult(BaseModel):
    """의사결정 결과를 나타내는 모델"""
    result: Dict[str, Any] = Field(description="의사결정 결과")
    trace: List[Dict[str, Any]] = Field(description="의사결정 경로 추적")
    input_context: Dict[str, Any] = Field(description="입력 컨텍스트 (key-value)")
    rule_name: str = Field(description="사용된 규칙 이름")
    execution_time: Optional[float] = Field(None, description="실행 시간 (초)")
    rule_schema: Optional[Dict[str, Any]] = Field(None, description="규칙별 입력 스키마")
    engine_used: Optional[str] = Field(None, description="사용된 엔진 (cdmn/xml)")


class HybridDMNEngine:
    """하이브리드 DMN 엔진 - cDMN과 표준 XML 파싱 지원"""
    
    def __init__(self):
        self.cdmn_models: Dict[str, DMN] = {}
        self.xml_models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        self.engine_types: Dict[str, str] = {}  # 모델별 사용된 엔진 타입
        
        # 임시 파일 디렉토리 설정
        self.temp_dir = tempfile.mkdtemp()
        self._setup_temp_files()
    
    def _setup_temp_files(self):
        """임시 파일들을 미리 생성하여 API 버그를 해결합니다"""
        temp_files = [
            'idp_temp.txt',
            'idp_input.txt',
            'idp_output.txt'
        ]
        
        for temp_file in temp_files:
            temp_path = os.path.join(self.temp_dir, temp_file)
            with open(temp_path, 'w') as f:
                f.write('')
    
    def load_dmn_xml(self, rule_name: str, xml_content: str) -> Dict[str, Any]:
        """DMN XML을 로드하고 적절한 엔진을 선택합니다"""
        
        # 먼저 cDMN API로 시도
        if CDMN_AVAILABLE:
            try:
                # 임시 파일에 XML 저장
                temp_xml_path = os.path.join(self.temp_dir, f"{rule_name}.dmn")
                with open(temp_xml_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                
                # cDMN API로 DMN 모델 로드
                dmn_model = DMN(path=temp_xml_path, auto_propagate=False)
                
                # 모델 저장
                self.cdmn_models[rule_name] = dmn_model
                self.engine_types[rule_name] = "cdmn"
                
                # 메타데이터 추출
                metadata = {
                    "inputs": dmn_model.get_inputs(),
                    "outputs": dmn_model.get_outputs(),
                    "intermediary": dmn_model.get_intermediary(),
                    "loaded_at": time.time(),
                    "engine_type": "cdmn"
                }
                
                self.model_metadata[rule_name] = metadata
                
                return {
                    "status": "success",
                    "message": f"Rule '{rule_name}' loaded successfully with cDMN API",
                    "engine_type": "cdmn",
                    "inputs": metadata["inputs"],
                    "outputs": metadata["outputs"],
                    "intermediary": metadata["intermediary"]
                }
                
            except Exception as e:
                print(f"cDMN loading failed for {rule_name}: {e}")
        
        # cDMN 실패 시 표준 XML 파싱 사용
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)
            
            # DMN XML 구조 분석
            metadata = self._analyze_dmn_xml(root)
            metadata["loaded_at"] = time.time()
            metadata["engine_type"] = "xml"
            
            self.xml_models[rule_name] = root
            self.engine_types[rule_name] = "xml"
            self.model_metadata[rule_name] = metadata
            
            return {
                "status": "success", 
                "message": f"Rule '{rule_name}' loaded successfully with XML parser",
                "engine_type": "xml",
                "decisions": metadata.get("decisions", []),
                "inputs": metadata.get("inputs", [])
            }
            
        except Exception as e:
            raise ValueError(f"Failed to load DMN XML with any engine: {str(e)}")
    
    def _analyze_dmn_xml(self, root) -> Dict[str, Any]:
        """DMN XML 구조를 분석하여 메타데이터를 추출합니다"""
        metadata = {
            "decisions": [],
            "inputs": [],
            "decision_tables": [],
            "rules": []
        }
        
        # 네임스페이스 처리
        ns = {'dmn': 'https://www.omg.org/spec/DMN/20191111/MODEL/'}
        
        # Decision 요소들 찾기
        decisions = root.findall('.//dmn:decision', ns)
        for decision in decisions:
            decision_info = {
                "id": decision.get("id"),
                "name": decision.get("name"),
                "tables": []
            }
            
            # Decision Table 찾기
            tables = decision.findall('.//dmn:decisionTable', ns)
            for table in tables:
                table_info = {
                    "id": table.get("id"),
                    "hitPolicy": table.get("hitPolicy", "UNIQUE"),
                    "inputs": [],
                    "outputs": [],
                    "rules": []
                }
                
                # Input 요소들
                inputs = table.findall('.//dmn:input', ns)
                for input_elem in inputs:
                    input_info = {
                        "id": input_elem.get("id"),
                        "label": input_elem.get("label", ""),
                        "expression": ""
                    }
                    
                    # Input Expression 찾기
                    expr = input_elem.find('.//dmn:text', ns)
                    if expr is not None:
                        input_info["expression"] = expr.text or ""
                    
                    table_info["inputs"].append(input_info)
                    metadata["inputs"].append(input_info)
                
                # Output 요소들
                outputs = table.findall('.//dmn:output', ns)
                for output in outputs:
                    output_info = {
                        "id": output.get("id"),
                        "label": output.get("label", ""),
                        "typeRef": output.get("typeRef", "")
                    }
                    table_info["outputs"].append(output_info)
                
                # Rule 요소들
                rules = table.findall('.//dmn:rule', ns)
                for rule in rules:
                    rule_info = {
                        "id": rule.get("id"),
                        "inputEntries": [],
                        "outputEntries": []
                    }
                    
                    # Input Entry들
                    input_entries = rule.findall('.//dmn:inputEntry', ns)
                    for entry in input_entries:
                        text_elem = entry.find('.//dmn:text', ns)
                        rule_info["inputEntries"].append(text_elem.text if text_elem is not None else "")
                    
                    # Output Entry들
                    output_entries = rule.findall('.//dmn:outputEntry', ns)
                    for entry in output_entries:
                        text_elem = entry.find('.//dmn:text', ns)
                        rule_info["outputEntries"].append(text_elem.text if text_elem is not None else "")
                    
                    table_info["rules"].append(rule_info)
                    metadata["rules"].append(rule_info)
                
                decision_info["tables"].append(table_info)
                metadata["decision_tables"].append(table_info)
            
            metadata["decisions"].append(decision_info)
        
        return metadata
    
    def execute_dmn_rule(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """DMN 규칙을 실행합니다"""
        start_time = time.time()
        
        if rule_name not in self.engine_types:
            execution_time = time.time() - start_time
            return DecisionResult(
                result={"error": f"Rule '{rule_name}' not loaded"},
                trace=[{"step": 1, "rule": "error", "condition": "rule_not_loaded", "result": "error"}],
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema={"error": "Rule not loaded"},
                engine_used="none"
            )
        
        try:
            engine_type = self.engine_types[rule_name]
            
            if engine_type == "cdmn":
                result = self._execute_with_cdmn(rule_name, input_context)
            else:
                result = self._execute_with_xml(rule_name, input_context)
            
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.engine_used = engine_type
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return DecisionResult(
                result={"error": f"Rule execution failed: {str(e)}"},
                trace=[{"step": 1, "rule": "error", "condition": "execution_failed", "result": str(e)}],
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema=self.model_metadata.get(rule_name, {}).get("schema", {}),
                engine_used=self.engine_types.get(rule_name, "unknown")
            )
    
    def _execute_with_cdmn(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """cDMN API를 사용하여 규칙을 실행합니다"""
        dmn_model = self.cdmn_models[rule_name]
        trace = []
        results = {}
        
        # 입력값 설정
        for key, value in input_context.items():
            try:
                dmn_model.set_value(key, value)
                trace.append({
                    "step": len(trace) + 1,
                    "action": "set_input",
                    "variable": key,
                    "value": value,
                    "result": "success"
                })
            except Exception as e:
                trace.append({
                    "step": len(trace) + 1,
                    "action": "set_input",
                    "variable": key,
                    "value": value,
                    "result": f"error: {str(e)}"
                })
        
        # 추론 실행 (propagation)
        try:
            dmn_model.propagate()
            trace.append({
                "step": len(trace) + 1,
                "action": "propagate",
                "result": "success"
            })
        except Exception as e:
            trace.append({
                "step": len(trace) + 1,
                "action": "propagate",
                "result": f"error: {str(e)}"
            })
        
        # 결과 추출
        metadata = self.model_metadata[rule_name]
        outputs = metadata.get("outputs", [])
        intermediary = metadata.get("intermediary", [])
        
        # 출력 변수들 확인
        for output_var in outputs:
            try:
                if dmn_model.is_certain(output_var):
                    value = dmn_model.value_of(output_var)
                    results[output_var] = value
                    trace.append({
                        "step": len(trace) + 1,
                        "action": "get_output",
                        "variable": output_var,
                        "result": f"certain: {value}"
                    })
                else:
                    results[output_var] = "uncertain"
                    trace.append({
                        "step": len(trace) + 1,
                        "action": "get_output",
                        "variable": output_var,
                        "result": "uncertain"
                    })
            except Exception as e:
                results[output_var] = f"error: {str(e)}"
                trace.append({
                    "step": len(trace) + 1,
                    "action": "get_output",
                    "variable": output_var,
                    "result": f"error: {str(e)}"
                })
        
        # 중간 변수들도 확인
        for inter_var in intermediary:
            try:
                if dmn_model.is_certain(inter_var):
                    value = dmn_model.value_of(inter_var)
                    results[f"intermediary_{inter_var}"] = value
                    trace.append({
                        "step": len(trace) + 1,
                        "action": "get_intermediary",
                        "variable": inter_var,
                        "result": f"certain: {value}"
                    })
            except Exception as e:
                # 중간 변수는 선택적이므로 오류를 무시
                pass
        
        # 모델 확장 시도 (모든 해 구하기)
        try:
            model_expansion = dmn_model.model_expand()
            if model_expansion:
                results["model_expansion"] = model_expansion.getvalue()
                trace.append({
                    "step": len(trace) + 1,
                    "action": "model_expand",
                    "result": "success"
                })
        except Exception as e:
            trace.append({
                "step": len(trace) + 1,
                "action": "model_expand",
                "result": f"error: {str(e)}"
            })
        
        return DecisionResult(
            result=results,
            trace=trace,
            input_context=input_context,
            rule_name=rule_name,
            rule_schema=self._extract_schema_from_metadata(metadata)
        )
    
    def _execute_with_xml(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """표준 XML 파서를 사용하여 규칙을 실행합니다"""
        metadata = self.model_metadata[rule_name]
        decisions = metadata.get("decisions", [])
        
        trace = []
        results = {}
        
        # 각 Decision Table을 순서대로 실행
        for decision in decisions:
            decision_name = decision.get("name", "unknown")
            tables = decision.get("tables", [])
            
            for table in tables:
                table_id = table.get("id", "unknown")
                rules = table.get("rules", [])
                inputs = table.get("inputs", [])
                outputs = table.get("outputs", [])
                
                # 입력값 매칭 및 규칙 평가
                matched_rule = None
                for rule in rules:
                    if self._evaluate_rule_conditions(rule, inputs, input_context):
                        matched_rule = rule
                        break
                
                if matched_rule:
                    # 출력값 추출
                    output_values = matched_rule.get("outputEntries", [])
                    for i, output in enumerate(outputs):
                        if i < len(output_values):
                            output_name = output.get("label", f"output_{i}")
                            output_value = output_values[i]
                            results[output_name] = self._parse_output_value(output_value)
                    
                    trace.append({
                        "step": len(trace) + 1,
                        "decision": decision_name,
                        "table": table_id,
                        "rule": matched_rule.get("id", "unknown"),
                        "condition": "rule_matched",
                        "result": output_values
                    })
                else:
                    trace.append({
                        "step": len(trace) + 1,
                        "decision": decision_name,
                        "table": table_id,
                        "rule": "none",
                        "condition": "no_match",
                        "result": "no_matching_rule"
                    })
        
        return DecisionResult(
            result=results,
            trace=trace,
            input_context=input_context,
            rule_name=rule_name,
            rule_schema=self._extract_schema_from_metadata(metadata)
        )
    
    def _evaluate_rule_conditions(self, rule: Dict[str, Any], inputs: List[Dict[str, Any]], input_context: Dict[str, Any]) -> bool:
        """규칙의 입력 조건을 평가합니다"""
        input_entries = rule.get("inputEntries", [])
        
        for i, input_def in enumerate(inputs):
            if i >= len(input_entries):
                continue
            
            input_expression = input_def.get("expression", "")
            condition_text = input_entries[i]
            
            # 입력값 가져오기
            input_value = input_context.get(input_expression, None)
            if input_value is None:
                return False
            
            # 조건 평가
            if not self._evaluate_condition(input_value, condition_text):
                return False
        
        return True
    
    def _evaluate_condition(self, value: Any, condition: str) -> bool:
        """단일 조건을 평가합니다"""
        if not condition or condition.strip() == "":
            return True
        
        condition = condition.strip()
        
        try:
            # 숫자 비교
            if condition.startswith(">="):
                threshold = float(condition[2:])
                return float(value) >= threshold
            elif condition.startswith("<="):
                threshold = float(condition[2:])
                return float(value) <= threshold
            elif condition.startswith(">"):
                threshold = float(condition[1:])
                return float(value) > threshold
            elif condition.startswith("<"):
                threshold = float(condition[1:])
                return float(value) < threshold
            elif condition.startswith("="):
                threshold = condition[1:].strip()
                return str(value) == threshold
            else:
                # 문자열 비교
                return str(value).lower() == condition.lower()
        except (ValueError, TypeError):
            # 타입 변환 실패 시 문자열 비교
            return str(value).lower() == condition.lower()
    
    def _parse_output_value(self, value: str) -> Any:
        """출력값을 적절한 타입으로 파싱합니다"""
        if not value:
            return None
        
        value = value.strip()
        
        # 문자열인 경우 따옴표 제거
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        
        # 불린값
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # 숫자값
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 문자열
        return value
    
    def _extract_schema_from_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """메타데이터에서 스키마 정보를 추출합니다"""
        engine_type = metadata.get("engine_type", "unknown")
        
        if engine_type == "cdmn":
            return {
                "description": "DMN Rule (cDMN API)",
                "engine_type": "cdmn",
                "inputs": metadata.get("inputs", []),
                "outputs": metadata.get("outputs", []),
                "intermediary": metadata.get("intermediary", []),
                "loaded_at": metadata.get("loaded_at", 0)
            }
        else:
            return {
                "description": "DMN Rule (XML Parser)",
                "engine_type": "xml",
                "decisions": metadata.get("decisions", []),
                "inputs": [inp.get("expression", "") for inp in metadata.get("inputs", [])],
                "outputs": [out.get("label", "") for out in metadata.get("decision_tables", [])],
                "loaded_at": metadata.get("loaded_at", 0)
            }
    
    def cleanup(self):
        """리소스 정리"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class DMNModel:
    """DMN 모델을 관리하는 클래스 (하이브리드)"""
    
    def __init__(self, rules_dir: str = "rules"):
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(exist_ok=True)
        self.dmn_engine = HybridDMNEngine()
    
    async def load_rule(self, rule_name: str) -> str:
        """DMN 규칙을 로드합니다"""
        rule_file = self.rules_dir / f"{rule_name}.dmn.xml"
        
        if not rule_file.exists():
            raise FileNotFoundError(f"Rule '{rule_name}' not found")
        
        async with aiofiles.open(rule_file, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # 하이브리드 엔진으로 XML 로드
        result = self.dmn_engine.load_dmn_xml(rule_name, content)
        return result["message"]
    
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
        
        # 저장 후 즉시 로드 시도
        try:
            self.dmn_engine.load_dmn_xml(rule_name, xml_content)
        except Exception as e:
            print(f"Warning: Failed to load saved XML: {e}")
        
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
        
        # 엔진에서도 제거
        if rule_name in self.dmn_engine.cdmn_models:
            del self.dmn_engine.cdmn_models[rule_name]
        if rule_name in self.dmn_engine.xml_models:
            del self.dmn_engine.xml_models[rule_name]
        if rule_name in self.dmn_engine.model_metadata:
            del self.dmn_engine.model_metadata[rule_name]
        if rule_name in self.dmn_engine.engine_types:
            del self.dmn_engine.engine_types[rule_name]
        
        return f"Rule '{rule_name}' deleted successfully"
    
    async def get_rule_schema(self, rule_name: str) -> Dict[str, Any]:
        """규칙의 입력 스키마를 반환합니다"""
        if rule_name in self.dmn_engine.model_metadata:
            return self.dmn_engine.model_metadata[rule_name]
        else:
            return {
                "description": f"Rule '{rule_name}' not loaded",
                "engine_type": "none",
                "inputs": [],
                "outputs": []
            }
    
    async def evaluate_decision(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """DMN 규칙을 실행하여 의사결정을 수행합니다"""
        return self.dmn_engine.execute_dmn_rule(rule_name, input_context)
    
    def cleanup(self):
        """리소스 정리"""
        self.dmn_engine.cleanup()


# FastMCP 서버 초기화
mcp = FastMCP("hybrid-dmn-mcp-server")
dmn_model = DMNModel()


@mcp.tool()
async def load_rule(rule_name: str) -> str:
    """
    지정된 이름의 DMN XML 규칙을 로드합니다. cDMN API와 표준 XML 파싱을 모두 지원합니다.
    
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
        규칙의 입력 스키마 (엔진별 메타데이터 포함)
    """
    try:
        return await dmn_model.get_rule_schema(rule_name)
    except Exception as e:
        return {"error": f"Error getting schema for rule '{rule_name}': {str(e)}"}


@mcp.tool()
async def infer_decision(rule_name: str, context_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    지정된 DMN 규칙을 기반으로 의사결정을 실행합니다. 하이브리드 엔진을 사용합니다.
    
    Args:
        rule_name: 사용할 DMN 규칙의 이름
        context_input: key-value 딕셔너리 형태의 입력 데이터
    
    Returns:
        의사결정 결과 (result, trace, input_context, rule_name, execution_time, rule_schema, engine_used 포함)
    """
    try:
        # 입력 컨텍스트 생성
        if isinstance(context_input, str):
            input_context = {"raw_input": context_input}
        else:
            input_context = context_input
        
        # 의사결정 실행
        result = await dmn_model.evaluate_decision(rule_name, input_context)
        
        return {
            "result": result.result,
            "trace": result.trace,
            "input_context": result.input_context,
            "rule_name": result.rule_name,
            "execution_time": result.execution_time,
            "rule_schema": result.rule_schema,
            "engine_used": result.engine_used
        }
    except Exception as e:
        return {
            "error": f"Error executing decision: {str(e)}",
            "result": {},
            "trace": [],
            "input_context": {},
            "rule_name": rule_name,
            "execution_time": 0,
            "rule_schema": None,
            "engine_used": "error"
        }


@mcp.tool()
async def check_engine_status() -> Dict[str, Any]:
    """
    하이브리드 엔진의 상태를 확인합니다.
    
    Returns:
        엔진 상태 정보
    """
    return {
        "cdmn_available": CDMN_AVAILABLE,
        "message": f"Hybrid DMN Engine - cDMN: {CDMN_AVAILABLE}, XML: True",
        "loaded_cdmn_models": list(dmn_model.dmn_engine.cdmn_models.keys()),
        "loaded_xml_models": list(dmn_model.dmn_engine.xml_models.keys()),
        "engine_types": dmn_model.dmn_engine.engine_types,
        "total_loaded_models": len(dmn_model.dmn_engine.model_metadata)
    }


def main():
    """메인 함수 - 서버 실행"""
    print(f"Starting Hybrid DMN MCP Server...")
    print(f"cDMN API available: {CDMN_AVAILABLE}")
    print("Supports both cDMN API and standard XML parsing")
    
    try:
        # stdio 모드로 실행
        mcp.run()
    finally:
        # 서버 종료 시 리소스 정리
        dmn_model.cleanup()


if __name__ == "__main__":
    main()
