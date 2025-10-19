#!/usr/bin/env python3
"""
DcisionAI MCP Server - FastMCP Implementation (Secure)
=====================================================

This module provides a FastMCP server implementation following the official
MCP documentation patterns for optimal compatibility.

Provides comprehensive optimization capabilities:

TOOLS (7 core tools):
1. classify_intent_tool - Intent classification for optimization requests
2. analyze_data_tool - Data analysis and preprocessing
3. select_solver_tool - Intelligent solver selection based on problem type
4. build_model_tool - Mathematical model building with Qwen 30B
5. solve_optimization_tool - Optimization solving and results
6. explain_optimization_tool - Business-facing explainability and insights
7. simulate_scenarios_tool - Scenario simulation and risk assessment

RESOURCES (2 resources):
1. dcisionai://knowledge-base - Secure knowledge base metadata (proprietary data protected)
2. dcisionai://workflow-templates - Industry workflow templates

PROMPTS (2 prompts):
1. optimization_analysis_prompt - Template for problem analysis
2. model_building_guidance_prompt - Template for model building guidance
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




# Resources
@mcp.resource("dcisionai://knowledge-base")
async def knowledge_base_resource() -> str:
    """Optimization Knowledge Base - Secure access to optimization examples and patterns.
    
    This resource provides metadata about the knowledge base without exposing proprietary data.
    Use the search_knowledge_base tool to query for specific optimization examples.
    """
    try:
        from .tools import DcisionAITools
        tools_instance = DcisionAITools()
        
        # Only return metadata, not the actual proprietary data
        kb_metadata = {
            "name": "DcisionAI Optimization Knowledge Base",
            "description": "Comprehensive database of optimization examples and patterns",
            "total_examples": len(tools_instance.kb.knowledge_base_data.get('examples', [])),
            "categories": list(tools_instance.kb.knowledge_base_data.get('categories', {}).keys()),
            "last_updated": tools_instance.kb.knowledge_base_data.get('metadata', {}).get('created_at', 'Unknown'),
            "access_method": "Use search_knowledge_base tool to query for specific examples",
            "security_note": "Proprietary data protected - only search results are returned"
        }
        
        return json.dumps(kb_metadata, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to load knowledge base metadata: {e}"}, indent=2)

@mcp.resource("dcisionai://workflow-templates")
async def workflow_templates_resource() -> str:
    """Industry Workflow Templates - Predefined optimization workflows for different industries."""
    try:
        result = await get_workflow_templates()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to load workflow templates: {e}"}, indent=2)

# Prompts
@mcp.prompt()
async def optimization_analysis_prompt(
    problem_type: str,
    industry: Optional[str] = None
) -> str:
    """Template for optimization problem analysis.
    
    Args:
        problem_type: Type of optimization problem (e.g., portfolio, production, scheduling)
        industry: Industry context (e.g., finance, manufacturing, healthcare)
    """
    industry = industry or "general"
    return f"""You are an expert optimization analyst. Analyze this {problem_type} optimization problem in the {industry} industry.

**Analysis Framework:**
1. **Problem Classification**: Identify the optimization type (linear, integer, quadratic, etc.)
2. **Decision Variables**: Define what decisions need to be made
3. **Constraints**: Identify limitations and requirements
4. **Objective**: Determine the optimization goal
5. **Complexity Assessment**: Evaluate problem size and computational requirements
6. **Solution Approach**: Recommend appropriate solving methods

**Industry Context**: {industry}
**Problem Type**: {problem_type}

Provide a structured analysis following this framework."""

@mcp.prompt()
async def model_building_guidance_prompt(complexity: str) -> str:
    """Template for mathematical model building guidance.
    
    Args:
        complexity: Problem complexity level (simple, medium, complex)
    """
    return f"""You are a mathematical optimization expert. Provide guidance for building a {complexity} complexity optimization model.

**Model Building Process:**
1. **Variable Definition**: Create decision variables with proper bounds and types
2. **Constraint Formulation**: Express limitations as mathematical constraints
3. **Objective Function**: Define the optimization goal mathematically
4. **Model Validation**: Ensure mathematical correctness and feasibility
5. **Solver Selection**: Choose appropriate solving algorithm

**Complexity Level**: {complexity}

Provide detailed guidance for each step, including examples and best practices."""

def main():
    """Initialize and run the FastMCP server."""
    logger.info("Starting DcisionAI MCP Server with FastMCP")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
