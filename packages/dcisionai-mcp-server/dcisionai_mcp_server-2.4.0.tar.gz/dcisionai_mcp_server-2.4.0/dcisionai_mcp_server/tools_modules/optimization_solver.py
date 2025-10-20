#!/usr/bin/env python3
"""
Optimization Solver Tool
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..models.model_spec import ModelSpec
from ..optimization_engine import solve_real_optimization
from ..core.validators import Validator

logger = logging.getLogger(__name__)


class OptimizationSolver:
    """Optimization solver for mathematical models"""
    
    def __init__(self):
        self.validator = Validator()
    
    async def solve_optimization(
        self,
        problem_description: str,
        intent_data: Optional[Dict] = None,
        data_analysis: Optional[Dict] = None,
        model_building: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Solve optimization problem using real solver"""
        try:
            # REQUIRE a real model from build_model_tool - no fallbacks!
            if not model_building or 'result' not in model_building:
                logger.error("No model provided - solve_optimization requires a real model from build_model_tool")
                return {
                    "status": "error",
                    "step": "optimization_solution",
                    "error": "No model provided - solve_optimization requires a real model from build_model_tool",
                    "message": "Please run build_model_tool first to create a mathematical model"
                }
            
            # Validate that we have a proper model structure
            model_result = model_building['result']
            if not model_result.get('variables') or not model_result.get('constraints') or not model_result.get('objective'):
                logger.error("Invalid model structure - missing required components")
                return {
                    "status": "error",
                    "step": "optimization_solution",
                    "error": "Invalid model structure - missing variables, constraints, or objective",
                    "message": "Model must contain variables, constraints, and objective"
                }
            
            logger.info("Using real model from build_model_tool for optimization")
            logger.info(f"Model has {len(model_result.get('variables', []))} variables and {len(model_result.get('constraints', []))} constraints")
            
            # Convert to ModelSpec and solve with real OR-Tools solver
            model_spec = ModelSpec.from_dict(model_result)
            solver_result = solve_real_optimization(model_spec.to_dict())
            
            # Validate the optimization results
            validation = self.validator.validate(solver_result, model_spec)
            
            if not validation['is_valid'] and solver_result.get('status') == 'optimal':
                logger.warning(f"Validation errors: {validation['errors']}")
            
            solver_result['validation'] = validation
            
            return {
                "status": "success" if validation['is_valid'] else "error",
                "step": "optimization_solution",
                "timestamp": datetime.now().isoformat(),
                "result": solver_result,
                "message": f"Solved with real OR-Tools solver: {solver_result.get('status')}"
            }
            
        except Exception as e:
            logger.error(f"Solve error: {e}")
            return {"status": "error", "step": "optimization_solution", "error": str(e)}


async def solve_optimization_tool(
    problem_description: str,
    intent_data: Optional[Dict] = None,
    data_analysis: Optional[Dict] = None,
    model_building: Optional[Dict] = None
) -> Dict[str, Any]:
    """Tool wrapper for optimization solving"""
    # This would be called from the main tools orchestrator
    # For now, return a placeholder
    return {"status": "error", "error": "Tool not initialized"}
