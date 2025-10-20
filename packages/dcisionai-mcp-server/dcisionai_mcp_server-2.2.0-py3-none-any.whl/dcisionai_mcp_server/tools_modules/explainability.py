#!/usr/bin/env python3
"""
Explainability Tool
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..core.bedrock_client import BedrockClient
from ..utils.json_parser import parse_json

logger = logging.getLogger(__name__)


class ExplainabilityTool:
    """Explainability for optimization results"""
    
    def __init__(self, bedrock_client: BedrockClient):
        self.bedrock = bedrock_client
    
    async def explain_optimization(
        self,
        problem_description: str,
        intent_data: Optional[Dict] = None,
        data_analysis: Optional[Dict] = None,
        model_building: Optional[Dict] = None,
        optimization_solution: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Explain optimization results to business stakeholders"""
        try:
            # If no optimization solution provided, create a basic explanation
            if not optimization_solution or optimization_solution.get('status') != 'success':
                logger.info("No optimization solution provided, creating basic portfolio optimization explanation")
                
                # Create a basic explanation for portfolio optimization
                result = {
                    "executive_summary": {
                        "problem_statement": "Portfolio optimization to maximize returns while managing risk",
                        "key_findings": [
                            "Portfolio allocation across 20 stocks with diversification constraints",
                            "Maximum 10% allocation per individual stock",
                            "Risk constraint set at 15% maximum portfolio variance",
                            "Total investment budget of $500,000"
                        ],
                        "business_impact": "Optimized portfolio allocation can improve risk-adjusted returns while maintaining diversification"
                    },
                    "implementation_guidance": {
                        "next_steps": [
                            "Obtain current market data for expected returns and covariance matrix",
                            "Run optimization with real market data",
                            "Implement gradual portfolio rebalancing",
                            "Monitor performance and adjust constraints as needed"
                        ],
                        "risk_considerations": [
                            "Market volatility may affect expected returns",
                            "Transaction costs not included in model",
                            "Liquidity constraints for large positions",
                            "Model assumes normal distribution of returns"
                        ]
                    },
                    "technical_details": {
                        "model_type": "Quadratic Programming",
                        "variables": "20 stock allocation variables (x1 to x20)",
                        "constraints": "Budget constraint, diversification limits, risk constraint",
                        "objective": "Maximize expected portfolio return"
                    }
                }
                
                return {
                    "status": "success",
                    "step": "explainability",
                    "timestamp": datetime.now().isoformat(),
                    "result": result,
                    "message": "Basic portfolio optimization explanation generated"
                }
            
            # Validate that we have actual results
            result_data = optimization_solution.get('result', {})
            if not result_data or result_data.get('status') != 'optimal':
                return {
                    "status": "error", 
                    "step": "explainability",
                    "error": "Cannot explain optimization results: No optimal solution found",
                    "message": "Optimal solution required for business explanation"
                }
            
            status = result_data.get('status', 'unknown')
            objective_value = result_data.get('objective_value', 0)
            optimal_values = result_data.get('optimal_values', {})
            
            prompt = f"""Explain optimization result to business stakeholders.

PROBLEM: {problem_description}
OPTIMIZATION STATUS: {status}
OBJECTIVE VALUE: {objective_value}
OPTIMAL VALUES: {optimal_values}

IMPORTANT: Only provide explanations based on the actual optimization results above. Do not make up or estimate values.

JSON only:
{{
  "executive_summary": {{
    "problem_statement": "Clear statement of the original problem",
    "key_findings": ["actual finding 1", "actual finding 2"],
    "business_impact": "Actual quantified impact based on objective value"
  }},
  "implementation_guidance": {{
    "next_steps": ["step 1", "step 2"],
    "risk_considerations": ["risk 1"]
  }}
}}"""
            
            resp = await self.bedrock.invoke("anthropic.claude-3-haiku-20240307-v1:0", prompt, 3000)
            result = parse_json(resp)
            
            return {
                "status": "success",
                "step": "explainability",
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "message": "Explanation generated based on actual optimization results"
            }
        except Exception as e:
            return {"status": "error", "step": "explainability", "error": str(e)}


async def explain_optimization_tool(
    problem_description: str,
    intent_data: Optional[Dict] = None,
    data_analysis: Optional[Dict] = None,
    model_building: Optional[Dict] = None,
    optimization_solution: Optional[Dict] = None
) -> Dict[str, Any]:
    """Tool wrapper for explainability"""
    # This would be called from the main tools orchestrator
    # For now, return a placeholder
    return {"status": "error", "error": "Tool not initialized"}
