#!/usr/bin/env python3
"""
pyDMNrules MCP Server - DMN Decision Engine with FastMCP

pyDMNrules 엔진을 사용하여 DMN XML 파일을 로드하고 의사결정을 실행하는 MCP 서버입니다.
DMN XML 파일을 관리하고, 규칙별 입력 스키마를 제공하며, LLM이 적절한 형태로 추론을 호출할 수 있도록 합니다.
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# pyDMNrules import
try:
    from pyDMNrules import DMN
    PYDMNRULES_AVAILABLE = True
except ImportError:
    PYDMNRULES_AVAILABLE = False
    print("Error: pyDMNrules not available. Please install it: pip install pydmnrules-enhanced")


class DecisionResult(BaseModel):
    """의사결정 결과를 나타내는 모델"""
    result: Dict[str, Any] = Field(description="의사결정 결과")
    trace: List[Dict[str, Any]] = Field(description="의사결정 경로 추적")
    input_context: Dict[str, Any] = Field(description="입력 컨텍스트 (key-value)")
    rule_name: str = Field(description="사용된 규칙 이름")
    execution_time: Optional[float] = Field(None, description="실행 시간 (초)")
    rule_schema: Optional[Dict[str, Any]] = Field(None, description="규칙별 입력 스키마")
    engine_used: Optional[str] = Field(None, description="사용된 엔진 (pyDMNrules)")


class PyDMNrulesEngine:
    """pyDMNrules 엔진 - DMN XML 파싱 및 실행"""
    
    def __init__(self):
        self.dmn_models: Dict[str, DMN] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        
    def load_dmn_xml(self, rule_name: str, xml_content: str) -> Dict[str, Any]:
        """DMN XML을 로드하고 규칙 엔진을 구축합니다"""
        
        if not PYDMNRULES_AVAILABLE:
            raise RuntimeError("pyDMNrules is not available. Please install it.")
        
        try:
            # DMN 모델 인스턴스 생성
            dmn_model = DMN()
            
            # XML 문자열로부터 모델 로드
            status = dmn_model.useXML(xml_content)
            
            # 에러 체크
            if 'errors' in status and len(status['errors']) > 0:
                return {
                    "status": "error",
                    "message": f"Failed to load rule '{rule_name}'",
                    "errors": status['errors']
                }
            
            # 모델 저장
            self.dmn_models[rule_name] = dmn_model
            
            # 메타데이터 추출 - Glossary로부터 입력/출력 변수 정보 추출
            metadata = self._extract_metadata(dmn_model, rule_name)
            self.model_metadata[rule_name] = metadata
            
            return {
                "status": "success",
                "message": f"Rule '{rule_name}' loaded successfully with pyDMNrules",
                "engine_type": "pyDMNrules",
                "inputs": metadata.get("inputs", {}),
                "outputs": metadata.get("outputs", {}),
                "decision_tables": metadata.get("decision_tables", [])
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load DMN XML: {str(e)}",
                "errors": [str(e)]
            }
    
    def _extract_metadata(self, dmn_model: DMN, rule_name: str) -> Dict[str, Any]:
        """DMN 모델로부터 메타데이터를 추출합니다"""
        metadata = {
            "loaded_at": time.time(),
            "engine_type": "pyDMNrules",
            "rule_name": rule_name,
            "inputs": {},
            "outputs": {},
            "decision_tables": [],
            "glossary": {},
            "variable_names": []  # LLM이 사용해야 할 정확한 변수 이름 목록
        }
        
        # Glossary 정보 추출
        if hasattr(dmn_model, 'glossary') and dmn_model.glossary:
            for variable, info in dmn_model.glossary.items():
                item = info.get('item', '')
                concept = info.get('concept', '')
                
                glossary_entry = {
                    "variable": variable,
                    "item": item,
                    "concept": concept,
                    "type": "string",  # 기본 타입 (pyDMNrules에서 타입 정보가 제한적임)
                    "feel_name": item  # FEEL 표현식에서 사용되는 이름
                }
                
                metadata["glossary"][variable] = glossary_entry
                metadata["variable_names"].append(variable)
                
                # 입력/출력 구분은 decision tables를 분석해야 정확하지만,
                # 일단 모든 glossary 항목을 입력으로 간주
                metadata["inputs"][variable] = glossary_entry
        
        # Decision Tables 정보 추출
        if hasattr(dmn_model, 'decisionTables') and dmn_model.decisionTables:
            for table_name, table_info in dmn_model.decisionTables.items():
                decision_table = {
                    "name": table_name,
                    "hit_policy": table_info.get('hitPolicy', 'U'),
                    "description": table_info.get('name', table_name)
                }
                metadata["decision_tables"].append(decision_table)
        
        # Decisions 정보 추출
        if hasattr(dmn_model, 'decisions') and dmn_model.decisions:
            metadata["decisions"] = []
            for decision in dmn_model.decisions:
                if isinstance(decision, (list, tuple)) and len(decision) > 2:
                    metadata["decisions"].append({
                        "description": decision[1] if len(decision) > 1 else "",
                        "table": decision[2] if len(decision) > 2 else ""
                    })
        
        return metadata
    
    def execute_dmn_rule(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """DMN 규칙을 실행합니다"""
        start_time = time.time()
        
        if rule_name not in self.dmn_models:
            execution_time = time.time() - start_time
            return DecisionResult(
                result={"error": f"Rule '{rule_name}' not loaded"},
                trace=[{"step": 1, "rule": "error", "condition": "rule_not_loaded", "result": "error"}],
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema={"error": "Rule not loaded"},
                engine_used="pyDMNrules"
            )
        
        try:
            dmn_model = self.dmn_models[rule_name]
            
            # pyDMNrules의 decide() 함수 호출
            (status, result_data) = dmn_model.decide(input_context)
            
            # 에러 체크
            if 'errors' in status and len(status['errors']) > 0:
                execution_time = time.time() - start_time
                return DecisionResult(
                    result={"error": "Decision execution failed", "details": status['errors']},
                    trace=[{"step": 1, "error": str(status['errors'])}],
                    input_context=input_context,
                    rule_name=rule_name,
                    execution_time=execution_time,
                    rule_schema=self.model_metadata.get(rule_name, {}),
                    engine_used="pyDMNrules"
                )
            
            # 결과 파싱 및 trace 생성
            trace = self._build_trace(result_data, input_context)
            parsed_result = self._parse_result(result_data)
            
            execution_time = time.time() - start_time
            
            return DecisionResult(
                result=parsed_result,
                trace=trace,
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema=self.model_metadata.get(rule_name, {}),
                engine_used="pyDMNrules"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return DecisionResult(
                result={"error": f"Rule execution failed: {str(e)}"},
                trace=[{"step": 1, "rule": "error", "condition": "execution_failed", "result": str(e)}],
                input_context=input_context,
                rule_name=rule_name,
                execution_time=execution_time,
                rule_schema=self.model_metadata.get(rule_name, {}),
                engine_used="pyDMNrules"
            )
    
    def _parse_result(self, result_data: Any) -> Dict[str, Any]:
        """pyDMNrules 결과를 파싱합니다"""
        
        # result_data는 단일 decision dict이거나 decision dict의 list일 수 있음
        if isinstance(result_data, list):
            # 여러 decision tables가 실행된 경우
            # 마지막 결과를 primary result로, 전체를 all_results로 저장
            all_results = []
            for item in result_data:
                if isinstance(item, dict) and 'Result' in item:
                    all_results.append(item['Result'])
            
            return {
                "final_result": all_results[-1] if all_results else {},
                "all_results": all_results,
                "decision_count": len(all_results)
            }
        
        elif isinstance(result_data, dict):
            # 단일 decision table 결과
            if 'Result' in result_data:
                return result_data['Result']
            else:
                return result_data
        
        else:
            return {"raw_result": str(result_data)}
    
    def _build_trace(self, result_data: Any, input_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """의사결정 경로 추적 정보를 생성합니다"""
        trace = []
        
        # 입력 정보 추가
        trace.append({
            "step": 1,
            "action": "input",
            "data": input_context,
            "description": "Input context provided"
        })
        
        # result_data 분석
        if isinstance(result_data, list):
            # 여러 decision tables가 실행된 경우
            for idx, item in enumerate(result_data):
                step_info = {
                    "step": idx + 2,
                    "action": "decision_table",
                    "index": idx
                }
                
                if isinstance(item, dict):
                    if 'Executed Rule' in item:
                        executed_rule = item['Executed Rule']
                        if isinstance(executed_rule, tuple) and len(executed_rule) >= 3:
                            step_info["description"] = executed_rule[0]
                            step_info["table"] = executed_rule[1]
                            step_info["rule_id"] = executed_rule[2]
                    
                    if 'Result' in item:
                        step_info["result"] = item['Result']
                    
                    if 'RuleAnnotations' in item:
                        step_info["annotations"] = item['RuleAnnotations']
                
                trace.append(step_info)
        
        elif isinstance(result_data, dict):
            # 단일 decision table 결과
            step_info = {
                "step": 2,
                "action": "decision_table"
            }
            
            if 'Executed Rule' in result_data:
                executed_rule = result_data['Executed Rule']
                if isinstance(executed_rule, tuple) and len(executed_rule) >= 3:
                    step_info["description"] = executed_rule[0]
                    step_info["table"] = executed_rule[1]
                    step_info["rule_id"] = executed_rule[2]
            
            if 'Result' in result_data:
                step_info["result"] = result_data['Result']
            
            if 'RuleAnnotations' in result_data:
                step_info["annotations"] = result_data['RuleAnnotations']
            
            trace.append(step_info)
        
        return trace
    
    def get_rule_schema(self, rule_name: str) -> Dict[str, Any]:
        """규칙의 스키마 정보를 반환합니다"""
        if rule_name in self.model_metadata:
            metadata = self.model_metadata[rule_name]
            
            # LLM이 이해하기 쉬운 형태로 스키마 구성
            schema = {
                "rule_name": rule_name,
                "engine_type": "pyDMNrules",
                "loaded_at": metadata.get("loaded_at", 0),
                "inputs": {},
                "outputs": {},
                "decision_tables": metadata.get("decision_tables", []),
                "example_input": {},
                "variable_names": metadata.get("variable_names", []),
                "important_note": "⚠️ Use EXACT variable names from 'variable_names' list as dictionary keys in context_input"
            }
            
            # 입력 필드 정보
            for var_name, var_info in metadata.get("inputs", {}).items():
                schema["inputs"][var_name] = {
                    "variable_name": var_name,  # 정확한 변수 이름 (공백 포함 가능)
                    "feel_name": var_info.get('feel_name', ''),  # FEEL 표현식 이름
                    "description": f"{var_info.get('concept', '')}.{var_info.get('item', '')}",
                    "type": var_info.get("type", "string"),
                    "required": True
                }
                schema["example_input"][var_name] = None
            
            # 출력 필드 정보
            for var_name, var_info in metadata.get("outputs", {}).items():
                schema["outputs"][var_name] = {
                    "variable_name": var_name,
                    "feel_name": var_info.get('feel_name', ''),
                    "description": f"{var_info.get('concept', '')}.{var_info.get('item', '')}",
                    "type": var_info.get("type", "string")
                }
            
            return schema
        else:
            return {
                "error": f"Rule '{rule_name}' not loaded",
                "inputs": {},
                "outputs": {}
            }


class DMNModel:
    """DMN 모델을 관리하는 클래스 (pyDMNrules)"""
    
    def __init__(self, rules_dir: str = "rules"):
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(exist_ok=True)
        self.dmn_engine = PyDMNrulesEngine()
    
    async def load_rule(self, rule_name: str) -> str:
        """DMN 규칙을 로드합니다"""
        rule_file = self.rules_dir / f"{rule_name}.dmn"
        
        if not rule_file.exists():
            # .dmn.xml 확장자도 시도
            rule_file = self.rules_dir / f"{rule_name}.dmn.xml"
            if not rule_file.exists():
                raise FileNotFoundError(f"Rule '{rule_name}' not found (tried .dmn and .dmn.xml)")
        
        async with aiofiles.open(rule_file, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # pyDMNrules 엔진으로 XML 로드
        result = self.dmn_engine.load_dmn_xml(rule_name, content)
        
        if result.get("status") == "error":
            error_msg = result.get("message", "Unknown error")
            errors = result.get("errors", [])
            raise ValueError(f"{error_msg}: {errors}")
        
        return result["message"]
    
    async def save_rule(self, rule_name: str, xml_content: str) -> str:
        """DMN 규칙을 저장합니다"""
        rule_file = self.rules_dir / f"{rule_name}.dmn"
        
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
        
        rules = set()
        
        # .dmn 파일 찾기
        for file_path in self.rules_dir.glob("*.dmn"):
            if not file_path.name.endswith('.xml'):
                rules.add(file_path.stem)
        
        # .dmn.xml 파일 찾기
        for file_path in self.rules_dir.glob("*.dmn.xml"):
            rule_name = file_path.name.replace('.dmn.xml', '')
            rules.add(rule_name)
        
        return sorted(list(rules))
    
    async def delete_rule(self, rule_name: str) -> str:
        """DMN 규칙을 삭제합니다"""
        deleted = False
        
        # .dmn 파일 삭제 시도
        rule_file = self.rules_dir / f"{rule_name}.dmn"
        if rule_file.exists():
            rule_file.unlink()
            deleted = True
        
        # .dmn.xml 파일 삭제 시도
        rule_file_xml = self.rules_dir / f"{rule_name}.dmn.xml"
        if rule_file_xml.exists():
            rule_file_xml.unlink()
            deleted = True
        
        if not deleted:
            raise FileNotFoundError(f"Rule '{rule_name}' not found")
        
        # 엔진에서도 제거
        if rule_name in self.dmn_engine.dmn_models:
            del self.dmn_engine.dmn_models[rule_name]
        if rule_name in self.dmn_engine.model_metadata:
            del self.dmn_engine.model_metadata[rule_name]
        
        return f"Rule '{rule_name}' deleted successfully"
    
    async def get_rule_schema(self, rule_name: str) -> Dict[str, Any]:
        """규칙의 입력 스키마를 반환합니다"""
        return self.dmn_engine.get_rule_schema(rule_name)
    
    async def evaluate_decision(self, rule_name: str, input_context: Dict[str, Any]) -> DecisionResult:
        """DMN 규칙을 실행하여 의사결정을 수행합니다"""
        return self.dmn_engine.execute_dmn_rule(rule_name, input_context)


# FastMCP 서버 초기화
mcp = FastMCP("pydmnrules-mcp-server")
dmn_model = DMNModel()


@mcp.tool()
async def load_rule(rule_name: str) -> str:
    """
    지정된 이름의 DMN XML 규칙을 로드합니다. pyDMNrules 엔진을 사용합니다.
    
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
    지정된 DMN 규칙을 기반으로 의사결정을 실행합니다. pyDMNrules 엔진을 사용합니다.
    
    Args:
        rule_name: 사용할 DMN 규칙의 이름
        context_input: key-value 딕셔너리 형태의 입력 데이터
    
    Returns:
        의사결정 결과 (result, trace, input_context, rule_name, execution_time, rule_schema, engine_used 포함)
    """
    try:
        # 입력 컨텍스트 생성
        if isinstance(context_input, str):
            try:
                input_context = json.loads(context_input)
            except json.JSONDecodeError:
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
    pyDMNrules 엔진의 상태를 확인합니다.
    
    Returns:
        엔진 상태 정보
    """
    return {
        "pydmnrules_available": PYDMNRULES_AVAILABLE,
        "message": f"pyDMNrules Engine - Available: {PYDMNRULES_AVAILABLE}",
        "loaded_models": list(dmn_model.dmn_engine.dmn_models.keys()),
        "total_loaded_models": len(dmn_model.dmn_engine.dmn_models),
        "rules_directory": str(dmn_model.rules_dir.absolute())
    }


def main():
    """메인 함수 - 서버 실행"""
    __version__ = "1.0.0"
    
    print(f"Starting pyDMNrules MCP Server v{__version__}")
    print(f"pyDMNrules available: {PYDMNRULES_AVAILABLE}")
    print("Supports DMN XML files (.dmn, .dmn.xml)")
    print(f"Rules directory: {dmn_model.rules_dir.absolute()}")
    
    if not PYDMNRULES_AVAILABLE:
        print("\n⚠️  WARNING: pyDMNrules is not installed!")
        print("Install with: pip install pydmnrules-enhanced")
        return
    
    try:
        # stdio 모드로 실행
        mcp.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nServer error: {e}")


if __name__ == "__main__":
    main()

