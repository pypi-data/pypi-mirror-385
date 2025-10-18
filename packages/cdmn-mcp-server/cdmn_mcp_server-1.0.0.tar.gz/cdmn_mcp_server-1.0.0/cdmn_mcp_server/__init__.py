"""
CDMN Decision MCP Server

FastMCP 기반 DMN 서버로 자연어 입력을 받아 DMN 규칙을 실행하고 결과를 반환하는 MCP 서버입니다.
"""

__version__ = "1.0.0"
__author__ = "rickjang"
__email__ = "rickjang@example.com"
__description__ = "FastMCP 기반 DMN 서버로 자연어 입력을 받아 DMN 규칙을 실행하고 결과를 반환하는 MCP 서버"

from .server_fully_generic import DMNModel, DecisionResult, GenericRuleEngine

__all__ = [
    "DMNModel",
    "DecisionResult", 
    "GenericRuleEngine",
]
