#!/usr/bin/env python3
"""
Integration tests for CDMN Decision MCP Server
"""

import asyncio
import json
import tempfile
from pathlib import Path

import pytest
from server import DMNModel, DecisionContext, NaturalLanguageProcessor


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def setup_method(self):
        """Setup test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.model = DMNModel(self.temp_dir)
        self.nlp = NaturalLanguageProcessor()
    
    def teardown_method(self):
        """Cleanup test method"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_complete_insurance_workflow(self):
        """Test complete insurance premium calculation workflow"""
        # 1. Create and save insurance rule
        rule_name = "insurance_premium"
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/">
  <decision id="test" name="Test Decision">
    <decisionTable id="testTable" hitPolicy="FIRST">
      <output id="testOutput" label="Test Output" typeRef="string"/>
    </decisionTable>
  </decision>
</definitions>"""
        
        save_result = await self.model.save_rule(rule_name, xml_content)
        assert "saved successfully" in save_result
        
        # 2. Load the rule
        load_result = await self.model.load_rule(rule_name)
        assert "loaded successfully" in load_result
        
        # 3. Parse natural language input
        natural_text = "30세 남자이고 흡연자야. 건강 점수는 40이야."
        context = self.nlp.parse_natural_language(natural_text)
        
        assert context.age == 30
        assert context.gender == "male"
        assert context.smoker is True
        assert context.health_score == 40.0
        
        # 4. Evaluate decision
        result = await self.model.evaluate_decision(rule_name, context)
        
        # 5. Verify result structure
        assert isinstance(result.result, dict)
        assert "risk_category" in result.result
        assert "premium" in result.result
        assert isinstance(result.trace, list)
        assert len(result.trace) > 0
        assert isinstance(result.markdown_output, str)
        assert "Decision Path" in result.markdown_output
        
        # 6. Verify markdown contains expected information
        markdown = result.markdown_output
        assert "30세" in markdown
        assert "남자" in markdown or "male" in markdown
        assert "흡연" in markdown
        assert "40" in markdown
    
    @pytest.mark.asyncio
    async def test_complete_loan_workflow(self):
        """Test complete loan approval workflow"""
        # 1. Create and save loan rule
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
        
        # 2. Parse natural language input
        natural_text = "신용 점수는 750이고 소득은 60000달러야. 나이는 35세야."
        context = self.nlp.parse_natural_language(natural_text)
        
        assert context.credit_score == 750
        assert context.income == 60000.0
        assert context.age == 35
        
        # 3. Evaluate decision
        result = await self.model.evaluate_decision(rule_name, context)
        
        # 4. Verify result structure
        assert isinstance(result.result, dict)
        assert "approved" in result.result
        assert "approval_score" in result.result
        assert isinstance(result.trace, list)
        assert isinstance(result.markdown_output, str)
        
        # 5. Verify markdown contains expected information
        markdown = result.markdown_output
        assert "750" in markdown
        assert "60000" in markdown
        assert "35세" in markdown
    
    @pytest.mark.asyncio
    async def test_rule_management_workflow(self):
        """Test complete rule management workflow"""
        # 1. List initial rules (should be empty)
        initial_rules = await self.model.list_rules()
        assert initial_rules == []
        
        # 2. Create multiple rules
        rules_data = [
            ("rule1", "<?xml version='1.0'?><definitions></definitions>"),
            ("rule2", "<?xml version='1.0'?><definitions></definitions>"),
            ("rule3", "<?xml version='1.0'?><definitions></definitions>")
        ]
        
        for rule_name, xml_content in rules_data:
            result = await self.model.save_rule(rule_name, xml_content)
            assert "saved successfully" in result
        
        # 3. List rules after creation
        rules_after_creation = await self.model.list_rules()
        assert len(rules_after_creation) == 3
        assert "rule1" in rules_after_creation
        assert "rule2" in rules_after_creation
        assert "rule3" in rules_after_creation
        
        # 4. Load one rule
        load_result = await self.model.load_rule("rule1")
        assert "loaded successfully" in load_result
        
        # 5. Delete one rule
        delete_result = await self.model.delete_rule("rule2")
        assert "deleted successfully" in delete_result
        
        # 6. List rules after deletion
        rules_after_deletion = await self.model.list_rules()
        assert len(rules_after_deletion) == 2
        assert "rule1" in rules_after_deletion
        assert "rule2" not in rules_after_deletion
        assert "rule3" in rules_after_deletion
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test error handling in various scenarios"""
        # 1. Test loading non-existent rule
        with pytest.raises(FileNotFoundError):
            await self.model.load_rule("nonexistent_rule")
        
        # 2. Test deleting non-existent rule
        with pytest.raises(FileNotFoundError):
            await self.model.delete_rule("nonexistent_rule")
        
        # 3. Test saving invalid XML
        with pytest.raises(ValueError, match="Invalid DMN XML"):
            await self.model.save_rule("invalid_rule", "invalid xml content")
        
        # 4. Test evaluating with non-existent rule
        context = DecisionContext(age=30, smoker=True)
        result = await self.model.evaluate_decision("nonexistent_rule", context)
        
        # Should return a default result for unknown rules
        assert isinstance(result.result, dict)
        assert "decision" in result.result
        assert result.result["decision"] == "unknown"
    
    @pytest.mark.asyncio
    async def test_natural_language_parsing_edge_cases(self):
        """Test natural language parsing with edge cases"""
        # 1. Empty string
        context = self.nlp.parse_natural_language("")
        assert context.age is None
        assert context.gender is None
        assert context.smoker is None
        
        # 2. Mixed language input
        text = "30세 male이고 smoker야. income은 50000이야."
        context = self.nlp.parse_natural_language(text)
        assert context.age == 30
        assert context.gender == "male"
        assert context.smoker is True
        assert context.income == 50000.0
        
        # 3. Complex sentence with multiple attributes
        text = "25세 여자이고 비흡연자야. 소득은 40000이고 건강 점수는 85야. 신용 점수는 720이야."
        context = self.nlp.parse_natural_language(text)
        assert context.age == 25
        assert context.gender == "female"
        assert context.smoker is False
        assert context.income == 40000.0
        assert context.health_score == 85.0
        assert context.credit_score == 720
        
        # 4. Text with no recognizable patterns
        text = "안녕하세요. 오늘 날씨가 좋네요."
        context = self.nlp.parse_natural_language(text)
        assert context.age is None
        assert context.gender is None
        assert context.smoker is None
    
    @pytest.mark.asyncio
    async def test_markdown_output_formatting(self):
        """Test markdown output formatting"""
        # Test insurance premium markdown
        context = DecisionContext(age=30, gender="male", smoker=True, health_score=40)
        result = await self.model._calculate_insurance_premium(context)
        
        markdown = result.markdown_output
        
        # Check for required sections
        assert "## 🧠 Decision Path" in markdown
        assert "### 입력 정보" in markdown
        assert "### 의사결정 과정" in markdown
        assert "### 최종 결과" in markdown
        assert "✅ **Final Decision**" in markdown
        assert "💰 **Calculated Premium**" in markdown
        
        # Check for input information
        assert "30세" in markdown
        assert "남자" in markdown or "male" in markdown
        assert "예" in markdown or "true" in markdown
        assert "40" in markdown
        
        # Test loan approval markdown
        context = DecisionContext(credit_score=750, income=60000, age=35)
        result = await self.model._calculate_loan_approval(context)
        
        markdown = result.markdown_output
        
        # Check for required sections
        assert "## 🧠 Decision Path" in markdown
        assert "### 입력 정보" in markdown
        assert "### 의사결정 과정" in markdown
        assert "### 최종 결과" in markdown
        
        # Check for input information
        assert "750" in markdown
        assert "60000" in markdown
        assert "35세" in markdown


if __name__ == "__main__":
    pytest.main([__file__])

