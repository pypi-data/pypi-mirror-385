"""
Mock LLM Client for testing purposes
"""

import re
from typing import Dict, Any


class MockLLMClient:
    """Mock LLM Client for testing without OpenAI API key"""
    
    def __init__(self):
        self.api_key = "mock_key"
    
    async def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """
        자연어 텍스트를 구조화된 컨텍스트로 변환합니다 (Mock 구현)
        
        Args:
            text: 자연어 입력 텍스트
        
        Returns:
            파싱된 컨텍스트 딕셔너리
        """
        result = {}
        
        # 나이 파싱
        age_patterns = [
            r'(\d+)세',
            r'나이는?\s*(\d+)',
            r'age\s*:?\s*(\d+)',
            r'(\d+)\s*years?\s*old'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['age'] = int(match.group(1))
                break
        
        # 성별 파싱
        if re.search(r'남자|남성|male|남', text, re.IGNORECASE):
            result['gender'] = 'male'
        elif re.search(r'여자|여성|female|여', text, re.IGNORECASE):
            result['gender'] = 'female'
        
        # 흡연 여부 파싱
        if re.search(r'흡연|담배|smoker|smoking', text, re.IGNORECASE):
            result['smoker'] = True
        elif re.search(r'비흡연|금연|non.?smoker', text, re.IGNORECASE):
            result['smoker'] = False
        
        # 건강 점수 파싱
        health_patterns = [
            r'건강\s*점수는?\s*(\d+(?:\.\d+)?)',
            r'health\s*score\s*:?\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*점'
        ]
        
        for pattern in health_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['health_score'] = float(match.group(1))
                break
        
        # 소득 파싱
        income_patterns = [
            r'소득은?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'income\s*:?\s*\$?(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*달러',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*원'
        ]
        
        for pattern in income_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                income_str = match.group(1).replace(',', '')
                result['income'] = float(income_str)
                break
        
        # 신용 점수 파싱
        credit_patterns = [
            r'신용\s*점수는?\s*(\d+)',
            r'credit\s*score\s*:?\s*(\d+)',
            r'(\d+)\s*점'
        ]
        
        for pattern in credit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['credit_score'] = int(match.group(1))
                break
        
        # 차량 연식 파싱
        vehicle_patterns = [
            r'차량\s*연식은?\s*(\d+)',
            r'vehicle\s*age\s*:?\s*(\d+)',
            r'(\d+)\s*년\s*차'
        ]
        
        for pattern in vehicle_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['vehicle_age'] = int(match.group(1))
                break
        
        # 고용 연수 파싱
        employment_patterns = [
            r'고용\s*연수는?\s*(\d+)',
            r'employment\s*years?\s*:?\s*(\d+)',
            r'(\d+)\s*년\s*근무'
        ]
        
        for pattern in employment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['employment_years'] = int(match.group(1))
                break
        
        return result