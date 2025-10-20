#!/usr/bin/env python3
"""
Workflow Validator - Smart validation for optimization workflows
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .validation_tool import ValidationTool

logger = logging.getLogger(__name__)


class WorkflowValidator:
    """Smart workflow validation with conditional gating"""
    
    def __init__(self, validation_tool: ValidationTool):
        self.validation_tool = validation_tool
        
        # Define which tools should be validated and their thresholds
        self.validation_config = {
            "build_model_tool": {
                "required": True,
                "trust_threshold": 0.6,
                "validation_type": "comprehensive",
                "critical": True
            },
            "solve_optimization_tool": {
                "required": True,
                "trust_threshold": 0.7,
                "validation_type": "comprehensive",
                "critical": True
            },
            "explain_optimization_tool": {
                "required": False,
                "trust_threshold": 0.5,
                "validation_type": "business",
                "critical": False
            },
            "simulate_scenarios_tool": {
                "required": False,
                "trust_threshold": 0.5,
                "validation_type": "business",
                "critical": False
            }
        }
    
    async def validate_workflow_step(
        self,
        problem_description: str,
        tool_name: str,
        tool_output: Dict[str, Any],
        model_spec: Optional[Dict] = None,
        force_validation: bool = False
    ) -> Dict[str, Any]:
        """
        Validate a workflow step with smart gating logic
        
        Args:
            problem_description: Original problem description
            tool_name: Name of the tool that generated the output
            tool_output: The tool's output to validate
            model_spec: Model specification (if available)
            force_validation: Force validation even if not configured
        
        Returns:
            Enhanced tool output with validation results
        """
        try:
            # Check if this tool should be validated
            config = self.validation_config.get(tool_name, {})
            should_validate = force_validation or config.get("required", False)
            
            if not should_validate:
                logger.info(f"Skipping validation for {tool_name} (not required)")
                return {
                    "original_output": tool_output,
                    "validation_skipped": True,
                    "reason": "Tool not configured for validation"
                }
            
            # Perform validation
            validation_type = config.get("validation_type", "comprehensive")
            validation_result = await self.validation_tool.validate_tool_output(
                problem_description, tool_name, tool_output, model_spec, validation_type
            )
            
            # Check trust threshold
            trust_score = validation_result.get("result", {}).get("overall_trust_score", 0.0)
            trust_threshold = config.get("trust_threshold", 0.5)
            is_critical = config.get("critical", False)
            
            # Determine if we should block the workflow
            should_block = is_critical and trust_score < trust_threshold
            
            result = {
                "original_output": tool_output,
                "validation": validation_result,
                "trust_score": trust_score,
                "trust_threshold": trust_threshold,
                "validation_passed": trust_score >= trust_threshold,
                "should_block_workflow": should_block,
                "is_critical_tool": is_critical
            }
            
            if should_block:
                logger.warning(f"Critical tool {tool_name} failed validation (score: {trust_score:.2f} < {trust_threshold:.2f})")
                result["status"] = "validation_failed"
                result["error"] = f"Critical tool validation failed: trust score {trust_score:.2f} below threshold {trust_threshold:.2f}"
            else:
                logger.info(f"Tool {tool_name} validation passed (score: {trust_score:.2f})")
                result["status"] = "validation_passed"
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow validation error for {tool_name}: {e}")
            return {
                "original_output": tool_output,
                "validation_error": str(e),
                "status": "validation_error"
            }
    
    async def validate_complete_workflow(
        self,
        problem_description: str,
        workflow_results: Dict[str, Any],
        model_spec: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Validate a complete optimization workflow
        
        Args:
            problem_description: Original problem description
            workflow_results: Dictionary of tool_name -> tool_output
            model_spec: Model specification (if available)
        
        Returns:
            Complete workflow validation results
        """
        try:
            validation_results = {}
            overall_trust_score = 0.0
            critical_failures = []
            warnings = []
            
            # Validate each tool output
            for tool_name, tool_output in workflow_results.items():
                if tool_name in self.validation_config:
                    result = await self.validate_workflow_step(
                        problem_description, tool_name, tool_output, model_spec
                    )
                    validation_results[tool_name] = result
                    
                    # Track critical failures
                    if result.get("should_block_workflow", False):
                        critical_failures.append(tool_name)
                    
                    # Accumulate trust scores
                    trust_score = result.get("trust_score", 0.0)
                    overall_trust_score += trust_score
                    
                    # Collect warnings
                    validation = result.get("validation", {})
                    if validation.get("result", {}).get("summary", {}).get("total_warnings", 0) > 0:
                        warnings.append(f"{tool_name}: {validation.get('result', {}).get('summary', {}).get('total_warnings', 0)} warnings")
            
            # Calculate overall metrics
            num_validated = len(validation_results)
            if num_validated > 0:
                overall_trust_score /= num_validated
            
            # Determine workflow status
            if critical_failures:
                status = "critical_validation_failed"
                status_text = f"Critical tools failed validation: {', '.join(critical_failures)}"
            elif overall_trust_score >= 0.7:
                status = "high_confidence"
                status_text = "Workflow validation passed with high confidence"
            elif overall_trust_score >= 0.5:
                status = "medium_confidence"
                status_text = "Workflow validation passed with medium confidence"
            else:
                status = "low_confidence"
                status_text = "Workflow validation passed with low confidence"
            
            return {
                "status": status,
                "status_text": status_text,
                "overall_trust_score": overall_trust_score,
                "critical_failures": critical_failures,
                "warnings": warnings,
                "validation_results": validation_results,
                "workflow_recommendation": self._get_workflow_recommendation(
                    status, overall_trust_score, critical_failures, warnings
                ),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Complete workflow validation error: {e}")
            return {
                "status": "validation_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_workflow_recommendation(
        self, status: str, trust_score: float, critical_failures: List[str], warnings: List[str]
    ) -> str:
        """Get recommendation based on workflow validation results"""
        if status == "critical_validation_failed":
            return f"Workflow should not proceed - critical tools failed: {', '.join(critical_failures)}"
        elif status == "high_confidence":
            return "Workflow results are reliable and can be used with confidence"
        elif status == "medium_confidence":
            return "Workflow results are generally reliable, but review warnings and consider manual validation"
        elif status == "low_confidence":
            return "Workflow results have significant issues - manual review strongly recommended"
        else:
            return "Workflow validation failed - manual review required"
    
    def configure_validation(
        self, tool_name: str, required: bool = None, trust_threshold: float = None,
        validation_type: str = None, critical: bool = None
    ) -> None:
        """Configure validation settings for a specific tool"""
        if tool_name not in self.validation_config:
            self.validation_config[tool_name] = {}
        
        config = self.validation_config[tool_name]
        if required is not None:
            config["required"] = required
        if trust_threshold is not None:
            config["trust_threshold"] = trust_threshold
        if validation_type is not None:
            config["validation_type"] = validation_type
        if critical is not None:
            config["critical"] = critical
        
        logger.info(f"Updated validation config for {tool_name}: {config}")
    
    def get_validation_config(self) -> Dict[str, Any]:
        """Get current validation configuration"""
        return self.validation_config.copy()
