#!/usr/bin/env python3
"""
DcisionAI MCP Server - FastMCP Implementation
============================================

This module provides a FastMCP server implementation following the official
MCP documentation patterns for optimal compatibility.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

from .tools import (
    classify_intent,
    analyze_data,
    build_model,
    solve_optimization,
    select_solver,
    explain_optimization,
    simulate_scenarios,
    get_workflow_templates,
    execute_workflow,
)
from .config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("dcisionai-optimization")

@mcp.tool()
async def classify_intent_tool(problem_description: str, context: Optional[str] = None) -> str:
    """Classify user intent for optimization requests.
    
    Args:
        problem_description: The user's optimization request or problem description
        context: Optional context about the business domain
    """
    try:
        result = await classify_intent(problem_description, context)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in classify_intent: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def analyze_data_tool(problem_description: str, intent_data: Optional[Dict[str, Any]] = None) -> str:
    """Analyze and preprocess data for optimization.
    
    Args:
        problem_description: Description of the optimization problem
        intent_data: Intent classification results
    """
    try:
        result = await analyze_data(problem_description, intent_data or {})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in analyze_data: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def select_solver_tool(
    optimization_type: str = "linear_programming",
    problem_size: Optional[Dict[str, Any]] = None,
    performance_requirement: str = "balanced"
) -> str:
    """Select the best available solver for optimization problems.
    
    Args:
        optimization_type: Type of optimization problem (linear_programming, quadratic_programming, etc.)
        problem_size: Problem size information (num_variables, num_constraints, etc.)
        performance_requirement: Performance requirement (speed, accuracy, or balanced)
    """
    try:
        result = await select_solver(optimization_type, problem_size or {}, performance_requirement)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in select_solver: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def build_model_tool(
    problem_description: str,
    intent_data: Optional[Dict[str, Any]] = None,
    data_analysis: Optional[Dict[str, Any]] = None,
    solver_selection: Optional[Dict[str, Any]] = None
) -> str:
    """Build mathematical optimization model using Qwen 30B.
    
    Args:
        problem_description: Detailed problem description
        intent_data: Intent classification results
        data_analysis: Results from data analysis step
        solver_selection: Results from solver selection step
    """
    try:
        result = await build_model(
            problem_description,
            intent_data or {},
            data_analysis or {},
            solver_selection or {}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in build_model: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def solve_optimization_tool(
    problem_description: str,
    intent_data: Optional[Dict[str, Any]] = None,
    data_analysis: Optional[Dict[str, Any]] = None,
    model_building: Optional[Dict[str, Any]] = None
) -> str:
    """Solve the optimization problem and generate results.
    
    Args:
        problem_description: Problem description
        intent_data: Intent classification results
        data_analysis: Data analysis results
        model_building: Model building results
    """
    try:
        result = await solve_optimization(
            problem_description,
            intent_data or {},
            data_analysis or {},
            model_building or {}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in solve_optimization: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def explain_optimization_tool(
    problem_description: str,
    intent_data: Optional[Dict[str, Any]] = None,
    data_analysis: Optional[Dict[str, Any]] = None,
    model_building: Optional[Dict[str, Any]] = None,
    optimization_solution: Optional[Dict[str, Any]] = None
) -> str:
    """Provide business-facing explainability for optimization results.
    
    Args:
        problem_description: Original problem description
        intent_data: Intent classification results
        data_analysis: Data analysis results
        model_building: Model building results
        optimization_solution: Optimization solution results
    """
    try:
        result = await explain_optimization(
            problem_description,
            intent_data or {},
            data_analysis or {},
            model_building or {},
            optimization_solution or {}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in explain_optimization: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def simulate_scenarios_tool(
    problem_description: str,
    optimization_solution: Optional[Dict[str, Any]] = None,
    scenario_parameters: Optional[Dict[str, Any]] = None,
    simulation_type: str = "monte_carlo",
    num_trials: int = 10000
) -> str:
    """Simulate different scenarios for optimization analysis and risk assessment.
    
    Args:
        problem_description: Description of the optimization problem
        optimization_solution: Results from optimization solving
        scenario_parameters: Parameters for scenario simulation
        simulation_type: Type of simulation (monte_carlo, discrete_event, agent_based, etc.)
        num_trials: Number of simulation trials
    """
    try:
        result = await simulate_scenarios(
            problem_description,
            optimization_solution or {},
            scenario_parameters or {},
            simulation_type,
            num_trials
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in simulate_scenarios: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_workflow_templates_tool() -> str:
    """Get available industry workflow templates.
    
    Returns:
        JSON string containing available workflow templates
    """
    try:
        result = await get_workflow_templates()
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in get_workflow_templates: {e}")
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def execute_workflow_tool(
    industry: str,
    workflow_id: str,
    user_input: Optional[Dict[str, Any]] = None
) -> str:
    """Execute a complete optimization workflow.
    
    Args:
        industry: Target industry (manufacturing, healthcare, retail, etc.)
        workflow_id: Specific workflow to execute
        user_input: User input parameters
    """
    try:
        result = await execute_workflow(industry, workflow_id, user_input or {})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in execute_workflow: {e}")
        return json.dumps({"error": str(e)}, indent=2)

def main():
    """Initialize and run the FastMCP server."""
    logger.info("Starting DcisionAI MCP Server with FastMCP")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
