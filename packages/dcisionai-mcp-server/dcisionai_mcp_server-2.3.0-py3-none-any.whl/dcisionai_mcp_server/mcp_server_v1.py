#!/usr/bin/env python3
"""
DcisionAI MCP Server - Standard MCP Protocol Implementation
==========================================================

This module provides a standard MCP server implementation that communicates
via stdin/stdout, compatible with Cursor IDE and other MCP clients.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types

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

class DcisionAIMCPServer:
    """
    DcisionAI MCP Server using standard MCP protocol.
    
    Provides comprehensive optimization capabilities:
    
    TOOLS (8 core tools):
    1. classify_intent - Intent classification for optimization requests
    2. analyze_data - Data analysis and preprocessing
    3. build_model - Mathematical model building with Qwen 30B
    4. solve_optimization - Optimization solving and results
    5. select_solver - Intelligent solver selection based on problem type
    6. explain_optimization - Business-facing explainability and insights
    7. get_workflow_templates - Industry workflow templates
    8. execute_workflow - End-to-end workflow execution
    
    RESOURCES (2 resources):
    1. dcisionai://knowledge-base - Optimization examples and patterns
    2. dcisionai://workflow-templates - Industry workflow templates
    
    PROMPTS (2 prompts):
    1. optimization_analysis - Template for problem analysis
    2. model_building_guidance - Template for model building guidance
    
    NOTIFICATIONS:
    - tools/list_changed - When available tools change
    - progress - Progress updates during long operations
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the DcisionAI MCP Server."""
        self.config = config or Config()
        self.server = Server("dcisionai-optimization")
        self._register_handlers()
        logger.info("DcisionAI MCP Server initialized successfully")
    
    async def _send_progress_notification(self, progress: float, message: str):
        """Send progress notification to clients."""
        try:
            await self.server.send_notification(
                types.Notification(
                    method="notifications/progress",
                    params={
                        "progress_token": "dcisionai_optimization",
                        "progress": progress,
                        "total": 1.0,
                        "message": message
                    }
                )
            )
        except Exception as e:
            logger.debug(f"Failed to send progress notification: {e}")
    
    async def _send_tools_changed_notification(self):
        """Send tools changed notification to clients."""
        try:
            await self.server.send_notification(
                types.Notification(
                    method="notifications/tools/list_changed"
                )
            )
        except Exception as e:
            logger.debug(f"Failed to send tools changed notification: {e}")
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        # Register notification handlers
        @self.server.list_notifications()
        async def handle_list_notifications() -> List[types.Notification]:
            """List available notifications."""
            return [
                types.Notification(
                    method="notifications/tools/list_changed",
                    description="Notifies when the list of available tools changes"
                ),
                types.Notification(
                    method="notifications/progress", 
                    description="Notifies about progress during long-running operations"
                )
            ]
        
        # Register resource handlers
        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            """List available resources."""
            return [
                types.Resource(
                    uri="dcisionai://knowledge-base",
                    name="Optimization Knowledge Base",
                    description="Database of optimization examples and patterns",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="dcisionai://workflow-templates",
                    name="Industry Workflow Templates",
                    description="Predefined optimization workflows for different industries",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content."""
            if uri == "dcisionai://knowledge-base":
                # Return knowledge base content
                try:
                    from .tools import DcisionAITools
                    tools_instance = DcisionAITools()
                    kb_data = tools_instance.kb.knowledge_base_data
                    return json.dumps(kb_data, indent=2)
                except Exception as e:
                    return json.dumps({"error": f"Failed to load knowledge base: {e}"})
            elif uri == "dcisionai://workflow-templates":
                # Return workflow templates
                try:
                    from .tools import get_workflow_templates
                    result = await get_workflow_templates()
                    return json.dumps(result, indent=2)
                except Exception as e:
                    return json.dumps({"error": f"Failed to load workflow templates: {e}"})
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        # Register prompt handlers
        @self.server.list_prompts()
        async def handle_list_prompts() -> List[types.Prompt]:
            """List available prompts."""
            return [
                types.Prompt(
                    name="optimization_analysis",
                    description="Template for optimization problem analysis",
                    arguments=[
                        types.PromptArgument(
                            name="problem_type",
                            description="Type of optimization problem (e.g., portfolio, production, scheduling)",
                            required=True
                        ),
                        types.PromptArgument(
                            name="industry",
                            description="Industry context (e.g., finance, manufacturing, healthcare)",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="model_building_guidance",
                    description="Template for mathematical model building guidance",
                    arguments=[
                        types.PromptArgument(
                            name="complexity",
                            description="Problem complexity level (simple, medium, complex)",
                            required=True
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: Dict[str, str]) -> List[types.TextContent]:
            """Get prompt content."""
            if name == "optimization_analysis":
                problem_type = arguments.get("problem_type", "generic")
                industry = arguments.get("industry", "general")
                prompt_text = f"""You are an expert optimization analyst. Analyze this {problem_type} optimization problem in the {industry} industry.

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
                return [types.TextContent(type="text", text=prompt_text)]
            elif name == "model_building_guidance":
                complexity = arguments.get("complexity", "medium")
                prompt_text = f"""You are a mathematical optimization expert. Provide guidance for building a {complexity} complexity optimization model.

**Model Building Process:**
1. **Variable Definition**: Create decision variables with proper bounds and types
2. **Constraint Formulation**: Express limitations as mathematical constraints
3. **Objective Function**: Define the optimization goal mathematically
4. **Model Validation**: Ensure mathematical correctness and feasibility
5. **Solver Selection**: Choose appropriate solving algorithm

**Complexity Level**: {complexity}

Provide detailed guidance for each step, including examples and best practices."""
                return [types.TextContent(type="text", text=prompt_text)]
            else:
                raise ValueError(f"Unknown prompt: {name}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name="classify_intent",
                    description="Classify user intent for optimization requests",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "The user's optimization request or problem description"
                            },
                            "context": {
                                "type": "string",
                                "description": "Optional context about the business domain",
                                "default": None
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="analyze_data",
                    description="Analyze and preprocess data for optimization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Description of the optimization problem"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Intent classification results from classify_intent",
                                "default": {}
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="build_model",
                    description="Build mathematical optimization model using Qwen 30B",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Detailed problem description"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Intent classification results",
                                "default": {}
                            },
                            "data_analysis": {
                                "type": "object",
                                "description": "Results from data analysis step",
                                "default": {}
                            },
                            "solver_selection": {
                                "type": "object",
                                "description": "Results from solver selection step",
                                "default": {}
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="solve_optimization",
                    description="Solve the optimization problem and generate results",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Problem description"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Intent classification results",
                                "default": {}
                            },
                            "data_analysis": {
                                "type": "object",
                                "description": "Data analysis results",
                                "default": {}
                            },
                            "model_building": {
                                "type": "object",
                                "description": "Model building results",
                                "default": {}
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="get_workflow_templates",
                    description="Get available industry workflow templates",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="select_solver",
                    description="Select the best available solver for optimization problems",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "optimization_type": {
                                "type": "string",
                                "description": "Type of optimization problem (linear_programming, quadratic_programming, mixed_integer_linear_programming, etc.)"
                            },
                            "problem_size": {
                                "type": "object",
                                "description": "Problem size information (num_variables, num_constraints, etc.)",
                                "default": {}
                            },
                            "performance_requirement": {
                                "type": "string",
                                "description": "Performance requirement: speed, accuracy, or balanced",
                                "default": "balanced"
                            }
                        },
                        "required": ["optimization_type"]
                    }
                ),
                Tool(
                    name="explain_optimization",
                    description="Provide business-facing explainability for optimization results",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Original problem description"
                            },
                            "intent_data": {
                                "type": "object",
                                "description": "Results from intent classification",
                                "default": {}
                            },
                            "data_analysis": {
                                "type": "object",
                                "description": "Results from data analysis",
                                "default": {}
                            },
                            "model_building": {
                                "type": "object",
                                "description": "Results from model building",
                                "default": {}
                            },
                            "optimization_solution": {
                                "type": "object",
                                "description": "Results from optimization solving",
                                "default": {}
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="simulate_scenarios",
                    description="Simulate different scenarios for optimization analysis and risk assessment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "problem_description": {
                                "type": "string",
                                "description": "Description of the optimization problem"
                            },
                            "optimization_solution": {
                                "type": "object",
                                "description": "Results from optimization solving",
                                "default": {}
                            },
                            "scenario_parameters": {
                                "type": "object",
                                "description": "Parameters for scenario simulation",
                                "default": {}
                            },
                            "simulation_type": {
                                "type": "string",
                                "description": "Type of simulation (monte_carlo, discrete_event, agent_based, system_dynamics, stochastic_optimization)",
                                "default": "monte_carlo"
                            },
                            "num_trials": {
                                "type": "integer",
                                "description": "Number of simulation trials",
                                "default": 10000
                            }
                        },
                        "required": ["problem_description"]
                    }
                ),
                Tool(
                    name="execute_workflow",
                    description="Execute a complete optimization workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "industry": {
                                "type": "string",
                                "description": "Target industry (manufacturing, healthcare, retail, marketing, financial, logistics, energy)"
                            },
                            "workflow_id": {
                                "type": "string",
                                "description": "Specific workflow to execute"
                            },
                            "user_input": {
                                "type": "object",
                                "description": "User input parameters",
                                "default": {}
                            }
                        },
                        "required": ["industry", "workflow_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "classify_intent":
                    result = await classify_intent(
                        arguments.get("problem_description", ""),
                        arguments.get("context")
                    )
                elif name == "analyze_data":
                    result = await analyze_data(
                        arguments.get("problem_description", ""),
                        arguments.get("intent_data", {})
                    )
                elif name == "build_model":
                    await self._send_progress_notification(0.1, "Starting model building...")
                    result = await build_model(
                        arguments.get("problem_description", ""),
                        arguments.get("intent_data", {}),
                        arguments.get("data_analysis", {}),
                        arguments.get("solver_selection", {})
                    )
                    await self._send_progress_notification(1.0, "Model building completed")
                elif name == "solve_optimization":
                    result = await solve_optimization(
                        arguments.get("problem_description", ""),
                        arguments.get("intent_data", {}),
                        arguments.get("data_analysis", {}),
                        arguments.get("model_building", {})
                    )
                elif name == "select_solver":
                    result = await select_solver(
                        arguments.get("optimization_type", ""),
                        arguments.get("problem_size", {}),
                        arguments.get("performance_requirement", "balanced")
                    )
                elif name == "explain_optimization":
                    result = await explain_optimization(
                        arguments.get("problem_description", ""),
                        arguments.get("intent_data", {}),
                        arguments.get("data_analysis", {}),
                        arguments.get("model_building", {}),
                        arguments.get("optimization_solution", {})
                    )
                elif name == "simulate_scenarios":
                    result = await simulate_scenarios(
                        arguments.get("problem_description", ""),
                        arguments.get("optimization_solution", {}),
                        arguments.get("scenario_parameters", {}),
                        arguments.get("simulation_type", "monte_carlo"),
                        arguments.get("num_trials", 10000)
                    )
                elif name == "get_workflow_templates":
                    result = await get_workflow_templates()
                elif name == "execute_workflow":
                    result = await execute_workflow(
                        arguments.get("industry", ""),
                        arguments.get("workflow_id", ""),
                        arguments.get("user_input", {})
                    )
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                # Convert result to JSON string
                if isinstance(result, dict):
                    result_text = json.dumps(result, indent=2)
                else:
                    result_text = str(result)
                
                return [TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                error_result = {
                    "error": f"Tool execution failed: {str(e)}",
                    "tool": name,
                    "arguments": arguments
                }
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    async def run(self):
        """Run the MCP server using stdio transport."""
        logger.info("Starting DcisionAI MCP Server with stdio transport")
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="dcisionai-optimization",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=types.NotificationOptions(
                                tools_changed=True,
                                prompts_changed=True,
                                resources_changed=True
                            ),
                            experimental_capabilities={}
                        )
                    ),
                    raise_exceptions=True
                )
        except Exception as e:
            logger.error(f"Error in MCP server run: {e}")
            import traceback
            traceback.print_exc()
            raise

def main():
    """Main entry point for the MCP server."""
    try:
        # Load configuration
        config = Config()
        
        # Create and run server
        server = DcisionAIMCPServer(config)
        asyncio.run(server.run())
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
