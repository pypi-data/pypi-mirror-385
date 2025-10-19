#!/usr/bin/env python3
"""
cDMN 전용 MCP Server

cDMN 프레임워크만을 사용하여 DMN 규칙을 실행합니다.
XML 파싱 구현체는 제거하고 오직 cDMN API만 사용합니다.
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
    print("✓ cDMN API successfully imported")
except ImportError as e:
    CDMN_AVAILABLE = False
    print(f"✗ cDMN API import failed: {e}")
    raise ImportError("cDMN is required but not available. Please install cDMN.")


class DecisionResult(BaseModel):
    """의사결정 결과를 나타내는 모델"""
    result: Dict[str, Any] = Field(description="의사결정 결과")
    trace: List[Dict[str, Any]] = Field(description="의사결정 경로 추적")
    input_context: Dict[str, Any] = Field(description="입력 컨텍스트 (key-value)")
    rule_name: str = Field(description="사용된 규칙 이름")
    execution_time: Optional[float] = Field(None, description="실행 시간 (초)")
    rule_schema: Optional[Dict[str, Any]] = Field(None, description="규칙별 입력 스키마")
    engine_used: str = Field(default="cdmn", description="사용된 엔진 (항상 cdm)")


class CDMNEngine:
    """cDMN 전용 엔진"""
    
    def __init__(self):
        if not CDMN_AVAILABLE:
            raise RuntimeError("cDMN is not available")
        
        self.cdmn_models: Dict[str, DMN] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        
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
        """DMN XML을 cDMN으로 로드합니다"""
        
        try:
            # 임시 파일에 XML 저장
            temp_xml_path = os.path.join(self.temp_dir, f"{rule_name}.dmn")
            with open(temp_xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            # cDMN API로 DMN 모델 로드
            dmn_model = DMN(path=temp_xml_path, auto_propagate=False)
            
            # 모델 저장
            self.cdmn_models[rule_name] = dmn_model
            
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
            raise ValueError(f"Failed to load DMN XML with cDMN: {str(e)}")
    
    def execute_dmn_rule(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """cDMN을 사용하여 DMN 규칙을 실행합니다"""
        start_time = time.time()
        
        if rule_name not in self.cdmn_models:
            execution_time = time.time() - start_time
            return DecisionResult(
                result={"error": f"Rule '{rule_name}' not loaded"},
                trace=[{"step": 1, "rule": "error", "condition": "rule_not_loaded", "result": "error"}],
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema={"error": "Rule not loaded"},
                engine_used="cdmn"
            )
        
        try:
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
            
            execution_time = time.time() - start_time
            return DecisionResult(
                result=results,
                trace=trace,
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema=self._extract_schema_from_metadata(metadata),
                engine_used="cdmn"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return DecisionResult(
                result={"error": f"Rule execution failed: {str(e)}"},
                trace=[{"step": 1, "rule": "error", "condition": "execution_failed", "result": str(e)}],
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema=self.model_metadata.get(rule_name, {}).get("schema", {}),
                engine_used="cdmn"
            )
    
    def _extract_schema_from_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """메타데이터에서 스키마 정보를 추출합니다"""
        return {
            "description": "DMN Rule (cDMN API)",
            "engine_type": "cdmn",
            "inputs": metadata.get("inputs", []),
            "outputs": metadata.get("outputs", []),
            "intermediary": metadata.get("intermediary", []),
            "loaded_at": metadata.get("loaded_at", 0)
        }
    
    def cleanup(self):
        """리소스 정리"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class DMNModel:
    """DMN 모델을 관리하는 클래스 (cDMN 전용)"""
    
    def __init__(self, rules_dir: str = "rules"):
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(exist_ok=True)
        self.dmn_engine = CDMNEngine()
    
    async def load_rule(self, rule_name: str) -> str:
        """DMN 규칙을 로드합니다"""
        rule_file = self.rules_dir / f"{rule_name}.dmn.xml"
        
        if not rule_file.exists():
            raise FileNotFoundError(f"Rule '{rule_name}' not found")
        
        async with aiofiles.open(rule_file, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # cDMN 엔진으로 XML 로드
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
        if rule_name in self.dmn_engine.model_metadata:
            del self.dmn_engine.model_metadata[rule_name]
        
        return f"Rule '{rule_name}' deleted successfully"
    
    async def get_rule_schema(self, rule_name: str) -> Dict[str, Any]:
        """규칙의 입력 스키마를 반환합니다"""
        if rule_name in self.dmn_engine.model_metadata:
            return self.dmn_engine.model_metadata[rule_name]
        else:
            return {
                "description": f"Rule '{rule_name}' not loaded",
                "engine_type": "cdmn",
                "inputs": [],
                "outputs": []
            }
    
    async def evaluate_decision(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """cDMN을 사용하여 DMN 규칙을 실행합니다"""
        return self.dmn_engine.execute_dmn_rule(rule_name, input_context)
    
    def cleanup(self):
        """리소스 정리"""
        self.dmn_engine.cleanup()


# FastMCP 서버 초기화
mcp = FastMCP("cdmn-only-mcp-server")
dmn_model = DMNModel()


@mcp.tool()
async def load_rule(rule_name: str) -> str:
    """
    지정된 이름의 DMN XML 규칙을 cDMN으로 로드합니다.
    
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
        규칙의 입력 스키마 (cDMN 메타데이터 포함)
    """
    try:
        return await dmn_model.get_rule_schema(rule_name)
    except Exception as e:
        return {"error": f"Error getting schema for rule '{rule_name}': {str(e)}"}


@mcp.tool()
async def infer_decision(rule_name: str, context_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    지정된 DMN 규칙을 기반으로 의사결정을 실행합니다. cDMN만 사용합니다.
    
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
            "engine_used": "cdmn"
        }


@mcp.tool()
async def check_engine_status() -> Dict[str, Any]:
    """
    cDMN 엔진의 상태를 확인합니다.
    
    Returns:
        엔진 상태 정보
    """
    return {
        "cdmn_available": CDMN_AVAILABLE,
        "message": f"cDMN Engine - Available: {CDMN_AVAILABLE}",
        "loaded_models": list(dmn_model.dmn_engine.cdmn_models.keys()),
        "total_loaded_models": len(dmn_model.dmn_engine.model_metadata)
    }


def main():
    """메인 함수 - 서버 실행"""
    print(f"Starting cDMN-only MCP Server...")
    print(f"cDMN API available: {CDMN_AVAILABLE}")
    print("Using only cDMN framework - no XML parsing")
    
    try:
        # stdio 모드로 실행
        mcp.run()
    finally:
        # 서버 종료 시 리소스 정리
        dmn_model.cleanup()


if __name__ == "__main__":
    main()
