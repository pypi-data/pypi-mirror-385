#!/usr/bin/env python3
"""
Test cases for CDMN Decision MCP Server
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from server import DMNModel, DecisionContext, NaturalLanguageProcessor


class TestDecisionContext:
    """Test DecisionContext model"""
    
    def test_decision_context_creation(self):
        """Test creating DecisionContext with valid data"""
        context = DecisionContext(
            age=30,
            gender="male",
            smoker=True,
            income=50000.0,
            health_score=75.0
        )
        
        assert context.age == 30
        assert context.gender == "male"
        assert context.smoker is True
        assert context.income == 50000.0
        assert context.health_score == 75.0
    
    def test_decision_context_optional_fields(self):
        """Test creating DecisionContext with optional fields"""
        context = DecisionContext()
        
        assert context.age is None
        assert context.gender is None
        assert context.smoker is None
        assert context.custom_fields == {}


class TestNaturalLanguageProcessor:
    """Test NaturalLanguageProcessor class"""
    
    def setup_method(self):
        """Setup test method"""
        self.nlp = NaturalLanguageProcessor()
    
    def test_parse_age_korean(self):
        """Test parsing age in Korean"""
        text = "30세 남자"
        context = self.nlp.parse_natural_language(text)
        assert context.age == 30
    
    def test_parse_age_english(self):
        """Test parsing age in English"""
        text = "age: 25"
        context = self.nlp.parse_natural_language(text)
        assert context.age == 25
    
    def test_parse_gender_male(self):
        """Test parsing male gender"""
        text = "30세 남자"
        context = self.nlp.parse_natural_language(text)
        assert context.gender == "male"
    
    def test_parse_gender_female(self):
        """Test parsing female gender"""
        text = "25세 여자"
        context = self.nlp.parse_natural_language(text)
        assert context.gender == "female"
    
    def test_parse_smoker_true(self):
        """Test parsing smoker status as true"""
        text = "30세 남자이고 흡연자야"
        context = self.nlp.parse_natural_language(text)
        assert context.smoker is True
    
    def test_parse_smoker_false(self):
        """Test parsing smoker status as false"""
        text = "30세 남자이고 비흡연자야"
        context = self.nlp.parse_natural_language(text)
        assert context.smoker is False
    
    def test_parse_income(self):
        """Test parsing income"""
        text = "소득: 50000"
        context = self.nlp.parse_natural_language(text)
        assert context.income == 50000.0
    
    def test_parse_health_score(self):
        """Test parsing health score"""
        text = "건강 점수: 75"
        context = self.nlp.parse_natural_language(text)
        assert context.health_score == 75.0
    
    def test_parse_credit_score(self):
        """Test parsing credit score"""
        text = "신용 점수: 750"
        context = self.nlp.parse_natural_language(text)
        assert context.credit_score == 750
    
    def test_parse_complex_text(self):
        """Test parsing complex natural language text"""
        text = "30세 남자이고 흡연자야. 소득은 50000이고 건강 점수는 75야."
        context = self.nlp.parse_natural_language(text)
        
        assert context.age == 30
        assert context.gender == "male"
        assert context.smoker is True
        assert context.income == 50000.0
        assert context.health_score == 75.0


class TestDMNModel:
    """Test DMNModel class"""
    
    def setup_method(self):
        """Setup test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.model = DMNModel(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test method"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_save_and_load_rule(self):
        """Test saving and loading a rule"""
        rule_name = "test_rule"
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/">
  <decision id="test" name="Test Decision">
    <decisionTable id="testTable" hitPolicy="FIRST">
      <output id="testOutput" label="Test Output" typeRef="string"/>
    </decisionTable>
  </decision>
</definitions>"""
        
        # Save rule
        result = await self.model.save_rule(rule_name, xml_content)
        assert "saved successfully" in result
        
        # Load rule
        result = await self.model.load_rule(rule_name)
        assert "loaded successfully" in result
    
    @pytest.mark.asyncio
    async def test_save_invalid_xml(self):
        """Test saving invalid XML"""
        rule_name = "invalid_rule"
        xml_content = "invalid xml content"
        
        with pytest.raises(ValueError, match="Invalid DMN XML"):
            await self.model.save_rule(rule_name, xml_content)
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_rule(self):
        """Test loading a non-existent rule"""
        with pytest.raises(FileNotFoundError):
            await self.model.load_rule("nonexistent_rule")
    
    @pytest.mark.asyncio
    async def test_list_rules_empty(self):
        """Test listing rules when directory is empty"""
        rules = await self.model.list_rules()
        assert rules == []
    
    @pytest.mark.asyncio
    async def test_list_rules_with_files(self):
        """Test listing rules with existing files"""
        # Create test files
        rule1_file = Path(self.temp_dir) / "rule1.dmn.xml"
        rule2_file = Path(self.temp_dir) / "rule2.dmn.xml"
        
        rule1_file.write_text("<?xml version='1.0'?><definitions></definitions>")
        rule2_file.write_text("<?xml version='1.0'?><definitions></definitions>")
        
        rules = await self.model.list_rules()
        assert len(rules) == 2
        assert "rule1" in rules
        assert "rule2" in rules
    
    @pytest.mark.asyncio
    async def test_delete_rule(self):
        """Test deleting a rule"""
        rule_name = "test_rule"
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/">
  <decision id="test" name="Test Decision">
    <decisionTable id="testTable" hitPolicy="FIRST">
      <output id="testOutput" label="Test Output" typeRef="string"/>
    </decisionTable>
  </decision>
</definitions>"""
        
        # Save rule first
        await self.model.save_rule(rule_name, xml_content)
        
        # Delete rule
        result = await self.model.delete_rule(rule_name)
        assert "deleted successfully" in result
        
        # Verify rule is deleted
        with pytest.raises(FileNotFoundError):
            await self.model.load_rule(rule_name)
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_rule(self):
        """Test deleting a non-existent rule"""
        with pytest.raises(FileNotFoundError):
            await self.model.delete_rule("nonexistent_rule")
    
    @pytest.mark.asyncio
    async def test_evaluate_insurance_premium(self):
        """Test evaluating insurance premium decision"""
        # Create insurance premium rule
        rule_name = "insurance_premium"
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/">
  <decision id="test" name="Test Decision">
    <decisionTable id="testTable" hitPolicy="FIRST">
      <output id="testOutput" label="Test Output" typeRef="string"/>
    </decisionTable>
  </decision>
</definitions>"""
        
        await self.model.save_rule(rule_name, xml_content)
        
        # Test context
        context = DecisionContext(age=30, smoker=True, health_score=40)
        
        # Evaluate decision
        result = await self.model.evaluate_decision(rule_name, context)
        
        assert isinstance(result.result, dict)
        assert "risk_category" in result.result
        assert "premium" in result.result
        assert isinstance(result.trace, list)
        assert isinstance(result.markdown_output, str)
        assert "Decision Path" in result.markdown_output
    
    @pytest.mark.asyncio
    async def test_evaluate_loan_approval(self):
        """Test evaluating loan approval decision"""
        # Create loan approval rule
        rule_name = "loan_approval"
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/">
  <decision id="test" name="Test Decision">
    <decisionTable id="testTable" hitPolicy="FIRST">
      <output id="testOutput" label="Test Output" typeRef="string"/>
    </decisionTable>
  </decision>
</definitions>"""
        
        await self.model.save_rule(rule_name, xml_content)
        
        # Test context
        context = DecisionContext(credit_score=750, income=60000, age=35)
        
        # Evaluate decision
        result = await self.model.evaluate_decision(rule_name, context)
        
        assert isinstance(result.result, dict)
        assert "approved" in result.result
        assert isinstance(result.trace, list)
        assert isinstance(result.markdown_output, str)
        assert "Decision Path" in result.markdown_output


class TestInsurancePremiumCalculation:
    """Test insurance premium calculation logic"""
    
    def setup_method(self):
        """Setup test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.model = DMNModel(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test method"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_high_risk_smoker(self):
        """Test high risk calculation for smoker"""
        context = DecisionContext(age=65, smoker=True, health_score=30)
        result = await self.model._calculate_insurance_premium(context)
        
        assert result.result["risk_category"] == "High"
        assert result.result["premium"] > 100000  # High risk premium
        assert "흡연" in result.markdown_output
    
    @pytest.mark.asyncio
    async def test_low_risk_non_smoker(self):
        """Test low risk calculation for non-smoker"""
        context = DecisionContext(age=30, smoker=False, health_score=80)
        result = await self.model._calculate_insurance_premium(context)
        
        assert result.result["risk_category"] == "Low"
        assert result.result["premium"] <= 100000  # Low risk premium
        assert "비흡연" in result.markdown_output or "아니오" in result.markdown_output
    
    @pytest.mark.asyncio
    async def test_medium_risk_elderly(self):
        """Test medium risk calculation for elderly"""
        context = DecisionContext(age=45, smoker=False, health_score=60)
        result = await self.model._calculate_insurance_premium(context)
        
        assert result.result["risk_category"] in ["Low", "Medium"]
        assert isinstance(result.result["premium"], int)


class TestLoanApprovalCalculation:
    """Test loan approval calculation logic"""
    
    def setup_method(self):
        """Setup test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.model = DMNModel(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test method"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_high_score_approval(self):
        """Test approval for high score applicant"""
        context = DecisionContext(credit_score=750, income=60000, age=35)
        result = await self.model._calculate_loan_approval(context)
        
        assert result.result["approved"] is True
        assert result.result["approval_score"] >= 60
        assert result.result["max_amount"] > 0
        assert result.result["interest_rate"] > 0
    
    @pytest.mark.asyncio
    async def test_low_score_rejection(self):
        """Test rejection for low score applicant"""
        context = DecisionContext(credit_score=400, income=20000, age=20)
        result = await self.model._calculate_loan_approval(context)
        
        assert result.result["approved"] is False
        assert result.result["approval_score"] < 60
        assert "Insufficient approval score" in result.result["reason"]


if __name__ == "__main__":
    pytest.main([__file__])



