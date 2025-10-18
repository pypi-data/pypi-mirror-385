"""
보험료 계산 비즈니스 로직
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class InsuranceContext:
    """보험료 계산 컨텍스트"""
    age: int
    gender: str
    smoker: bool
    health_score: float
    income: float = None
    vehicle_age: int = None
    credit_score: int = None


@dataclass
class InsuranceResult:
    """보험료 계산 결과"""
    risk_category: str
    risk_score: int
    premium: int
    trace: List[Dict[str, Any]]


class InsuranceCalculator:
    """보험료 계산기"""
    
    @staticmethod
    def calculate_premium(context: InsuranceContext) -> InsuranceResult:
        """보험료를 계산합니다"""
        trace = []
        risk_score = 0
        
        # 나이 기반 위험도 계산
        if context.age > 60:
            risk_score += 30
            trace.append({
                "step": 1,
                "rule": "age_risk",
                "condition": f"age > 60 ({context.age})",
                "result": "+30"
            })
        elif context.age > 40:
            risk_score += 15
            trace.append({
                "step": 1,
                "rule": "age_risk", 
                "condition": f"age > 40 ({context.age})",
                "result": "+15"
            })
        
        # 흡연 여부 기반 위험도 계산
        if context.smoker:
            risk_score += 40
            trace.append({
                "step": 2,
                "rule": "smoker_risk",
                "condition": "smoker = true",
                "result": "+40"
            })
        
        # 건강 점수 기반 위험도 계산
        if context.health_score and context.health_score < 50:
            risk_score += 25
            trace.append({
                "step": 3,
                "rule": "health_risk",
                "condition": f"health_score < 50 ({context.health_score})",
                "result": "+25"
            })
        
        # 위험도 분류
        if risk_score >= 70:
            risk_category = "High"
        elif risk_score >= 40:
            risk_category = "Medium"
        else:
            risk_category = "Low"
        
        # 보험료 계산
        base_premium = 50000
        if risk_category == "High":
            premium = int(base_premium * 2.5)
        elif risk_category == "Medium":
            premium = int(base_premium * 1.5)
        else:
            premium = base_premium
        
        return InsuranceResult(
            risk_category=risk_category,
            risk_score=risk_score,
            premium=premium,
            trace=trace
        )
