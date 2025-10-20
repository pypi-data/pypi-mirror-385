#!/usr/bin/env python3
"""
Validation Tool - Truth Guardian for Optimization Results
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..core.bedrock_client import BedrockClient
from ..core.validators import Validator
from ..models.model_spec import ModelSpec
from ..utils.json_parser import parse_json

logger = logging.getLogger(__name__)


class ValidationTool:
    """Truth Guardian - Validates optimization tool outputs for correctness and business logic"""
    
    def __init__(self, bedrock_client: BedrockClient):
        self.bedrock = bedrock_client
        self.validator = Validator()
    
    async def validate_tool_output(
        self,
        problem_description: str,
        tool_name: str,
        tool_output: Dict[str, Any],
        model_spec: Optional[Dict[str, Any]] = None,
        validation_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Validate any tool's output for correctness and business logic
        
        Args:
            problem_description: Original problem description
            tool_name: Name of the tool that generated the output
            tool_output: The tool's output to validate
            model_spec: Model specification (if available)
            validation_type: Type of validation ("mathematical", "business", "comprehensive")
        """
        try:
            logger.info(f"Starting validation for {tool_name} output")
            
            validation_results = {
                "tool_name": tool_name,
                "validation_type": validation_type,
                "timestamp": datetime.now().isoformat(),
                "overall_trust_score": 0.0,
                "validation_details": {}
            }
            
            # Mathematical validation (if model spec available)
            if model_spec and validation_type in ["mathematical", "comprehensive"]:
                math_validation = await self._validate_mathematical_correctness(
                    tool_output, model_spec
                )
                validation_results["validation_details"]["mathematical"] = math_validation
            
            # Business logic validation
            if validation_type in ["business", "comprehensive"]:
                business_validation = await self._validate_business_logic(
                    problem_description, tool_name, tool_output, model_spec
                )
                validation_results["validation_details"]["business"] = business_validation
            
            # Output structure validation
            structure_validation = self._validate_output_structure(tool_name, tool_output)
            validation_results["validation_details"]["structure"] = structure_validation
            
            # Calculate overall trust score
            trust_score = self._calculate_trust_score(validation_results["validation_details"])
            validation_results["overall_trust_score"] = trust_score
            
            # Generate validation summary
            validation_results["summary"] = self._generate_validation_summary(
                validation_results["validation_details"], trust_score
            )
            
            return {
                "status": "success",
                "step": "validation",
                "timestamp": datetime.now().isoformat(),
                "result": validation_results,
                "message": f"Validation completed for {tool_name} with trust score {trust_score:.2f}"
            }
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                "status": "error",
                "step": "validation",
                "error": str(e),
                "message": f"Validation failed for {tool_name}"
            }
    
    async def _validate_mathematical_correctness(
        self, tool_output: Dict[str, Any], model_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate mathematical correctness of optimization results"""
        try:
            # Convert model spec to ModelSpec object
            model = ModelSpec.from_dict(model_spec)
            
            # Extract optimization results
            result_data = tool_output.get('result', {})
            if not result_data:
                return {
                    "is_valid": False,
                    "errors": ["No result data found in tool output"],
                    "warnings": [],
                    "trust_score": 0.0
                }
            
            # Use the existing validator
            validation = self.validator.validate(result_data, model)
            
            # Calculate trust score based on validation results
            trust_score = 1.0 if validation['is_valid'] else 0.5
            if validation['warnings']:
                trust_score -= 0.1 * len(validation['warnings'])
            
            return {
                "is_valid": validation['is_valid'],
                "errors": validation['errors'],
                "warnings": validation['warnings'],
                "trust_score": max(0.0, trust_score),
                "validation_type": "mathematical_correctness"
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Mathematical validation error: {str(e)}"],
                "warnings": [],
                "trust_score": 0.0,
                "validation_type": "mathematical_correctness"
            }
    
    async def _validate_business_logic(
        self,
        problem_description: str,
        tool_name: str,
        tool_output: Dict[str, Any],
        model_spec: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate business logic using AI reasoning"""
        try:
            # Extract relevant data from tool output
            result_data = tool_output.get('result', {})
            optimal_values = result_data.get('optimal_values', {})
            objective_value = result_data.get('objective_value', 0)
            status = result_data.get('status', 'unknown')
            
            # Create validation prompt
            prompt = f"""You are a business validation expert. Validate this optimization result for business correctness.

PROBLEM: {problem_description}

TOOL: {tool_name}

TOOL OUTPUT:
{result_data}

MODEL SPECIFICATION:
{model_spec if model_spec else 'Not provided'}

VALIDATION TASKS:
1. Does this solution make business sense for the stated problem?
2. Are the optimal values realistic and achievable?
3. Are there any logical inconsistencies?
4. Does the objective value align with business expectations?
5. Are there any red flags or unrealistic assumptions?

BUSINESS VALIDATION CRITERIA:
- Values should be within reasonable business ranges
- Solution should be implementable in practice
- No contradictory or impossible results
- Objective should align with stated business goals
- Constraints should be properly respected

Respond with JSON:
{{
  "is_valid": true/false,
  "business_errors": ["List of business logic errors"],
  "business_warnings": ["List of business warnings"],
  "realism_check": {{
    "values_realistic": true/false,
    "implementation_feasible": true/false,
    "objective_reasonable": true/false
  }},
  "trust_score": 0.0-1.0,
  "validation_reasoning": "Detailed explanation of validation decision"
}}

Be specific about WHY something is wrong, not just that it's wrong."""
            
            resp = await self.bedrock.invoke("anthropic.claude-3-haiku-20240307-v1:0", prompt, 3000)
            result = parse_json(resp)
            
            # Ensure required fields exist
            result.setdefault('is_valid', True)
            result.setdefault('business_errors', [])
            result.setdefault('business_warnings', [])
            result.setdefault('trust_score', 0.8)
            result.setdefault('validation_reasoning', 'Business logic validation completed')
            
            return {
                "is_valid": result['is_valid'],
                "errors": result['business_errors'],
                "warnings": result['business_warnings'],
                "trust_score": result['trust_score'],
                "validation_type": "business_logic",
                "reasoning": result['validation_reasoning'],
                "realism_check": result.get('realism_check', {})
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Business validation error: {str(e)}"],
                "warnings": [],
                "trust_score": 0.0,
                "validation_type": "business_logic"
            }
    
    def _validate_output_structure(self, tool_name: str, tool_output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the structure and completeness of tool output"""
        try:
            errors = []
            warnings = []
            
            # Check required fields
            required_fields = ['status', 'step', 'timestamp', 'result']
            for field in required_fields:
                if field not in tool_output:
                    errors.append(f"Missing required field: {field}")
            
            # Check status field
            status = tool_output.get('status', 'unknown')
            if status not in ['success', 'error', 'warning']:
                warnings.append(f"Unusual status value: {status}")
            
            # Check result field
            result = tool_output.get('result', {})
            if not result:
                errors.append("Empty result field")
            
            # Tool-specific validation
            if tool_name == 'build_model_tool':
                if 'variables' not in result or 'constraints' not in result or 'objective' not in result:
                    errors.append("Model building result missing core components")
                if 'reasoning_steps' not in result:
                    warnings.append("Model building result missing reasoning steps")
            
            elif tool_name == 'solve_optimization_tool':
                if 'optimal_values' not in result:
                    errors.append("Optimization result missing optimal values")
                if 'objective_value' not in result:
                    errors.append("Optimization result missing objective value")
            
            # Calculate trust score
            trust_score = 1.0
            if errors:
                trust_score -= 0.3 * len(errors)
            if warnings:
                trust_score -= 0.1 * len(warnings)
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "trust_score": max(0.0, trust_score),
                "validation_type": "output_structure"
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Structure validation error: {str(e)}"],
                "warnings": [],
                "trust_score": 0.0,
                "validation_type": "output_structure"
            }
    
    def _calculate_trust_score(self, validation_details: Dict[str, Any]) -> float:
        """Calculate overall trust score from all validation results"""
        try:
            scores = []
            weights = {
                'mathematical': 0.4,
                'business': 0.4,
                'structure': 0.2
            }
            
            for validation_type, details in validation_details.items():
                if isinstance(details, dict) and 'trust_score' in details:
                    weight = weights.get(validation_type, 0.33)
                    scores.append(details['trust_score'] * weight)
            
            if not scores:
                return 0.5  # Default score if no validations
            
            return sum(scores) / sum(weights.values())
            
        except Exception as e:
            logger.error(f"Trust score calculation error: {e}")
            return 0.5
    
    def _generate_validation_summary(
        self, validation_details: Dict[str, Any], trust_score: float
    ) -> Dict[str, Any]:
        """Generate a summary of validation results"""
        try:
            total_errors = 0
            total_warnings = 0
            validation_types = []
            
            for validation_type, details in validation_details.items():
                if isinstance(details, dict):
                    validation_types.append(validation_type)
                    total_errors += len(details.get('errors', []))
                    total_warnings += len(details.get('warnings', []))
            
            # Determine overall status
            if trust_score >= 0.8:
                status = "high_confidence"
                status_text = "High confidence - results appear valid"
            elif trust_score >= 0.6:
                status = "medium_confidence"
                status_text = "Medium confidence - some concerns noted"
            elif trust_score >= 0.4:
                status = "low_confidence"
                status_text = "Low confidence - significant issues found"
            else:
                status = "unreliable"
                status_text = "Unreliable - major validation failures"
            
            return {
                "overall_status": status,
                "status_text": status_text,
                "trust_score": trust_score,
                "validation_types_completed": validation_types,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "recommendation": self._get_recommendation(trust_score, total_errors, total_warnings)
            }
            
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return {
                "overall_status": "error",
                "status_text": "Validation summary generation failed",
                "trust_score": 0.0,
                "recommendation": "Manual review required"
            }
    
    def _get_recommendation(self, trust_score: float, total_errors: int, total_warnings: int) -> str:
        """Get recommendation based on validation results"""
        if trust_score >= 0.8 and total_errors == 0:
            return "Results are reliable and can be used with confidence"
        elif trust_score >= 0.6 and total_errors == 0:
            return "Results are generally reliable, but review warnings"
        elif trust_score >= 0.4:
            return "Results have significant issues - manual review recommended"
        else:
            return "Results are unreliable - do not use without thorough review"
