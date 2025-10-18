"""
대출 승인 비즈니스 로직
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class LoanContext:
    """대출 승인 컨텍스트"""
    credit_score: int
    income: float
    age: int
    employment_years: int = None
    debt_to_income_ratio: float = None


@dataclass
class LoanResult:
    """대출 승인 결과"""
    approved: bool
    approval_score: int
    max_amount: float
    interest_rate: float
    trace: List[Dict[str, Any]]
    reason: str = None


class LoanApprovalCalculator:
    """대출 승인 계산기"""
    
    @staticmethod
    def calculate_approval(context: LoanContext) -> LoanResult:
        """대출 승인을 계산합니다"""
        trace = []
        approval_score = 0
        
        # 신용 점수 기반 점수 계산
        if context.credit_score >= 700:
            approval_score += 40
            trace.append({
                "step": 1,
                "rule": "credit_excellent",
                "condition": f"credit_score >= 700 ({context.credit_score})",
                "result": "+40"
            })
        elif context.credit_score >= 600:
            approval_score += 25
            trace.append({
                "step": 1,
                "rule": "credit_good",
                "condition": f"credit_score >= 600 ({context.credit_score})",
                "result": "+25"
            })
        elif context.credit_score >= 500:
            approval_score += 10
            trace.append({
                "step": 1,
                "rule": "credit_fair",
                "condition": f"credit_score >= 500 ({context.credit_score})",
                "result": "+10"
            })
        
        # 소득 기반 점수 계산
        if context.income >= 50000:
            approval_score += 30
            trace.append({
                "step": 2,
                "rule": "income_high",
                "condition": f"income >= 50000 ({context.income})",
                "result": "+30"
            })
        elif context.income >= 30000:
            approval_score += 20
            trace.append({
                "step": 2,
                "rule": "income_medium",
                "condition": f"income >= 30000 ({context.income})",
                "result": "+20"
            })
        
        # 나이 기반 점수 계산
        if 25 <= context.age <= 65:
            approval_score += 20
            trace.append({
                "step": 3,
                "rule": "age_optimal",
                "condition": f"25 <= age <= 65 ({context.age})",
                "result": "+20"
            })
        
        # 승인 결정
        approved = approval_score >= 60
        
        if approved:
            max_amount = min(context.income * 5, 1000000)
            interest_rate = 3.5 + (100 - approval_score) * 0.1
            reason = None
        else:
            max_amount = 0
            interest_rate = 0
            reason = "Insufficient approval score"
        
        return LoanResult(
            approved=approved,
            approval_score=approval_score,
            max_amount=max_amount,
            interest_rate=interest_rate,
            reason=reason,
            trace=trace
        )
