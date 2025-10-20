#!/usr/bin/env python3
"""
Test MathOpt Integration with 7-Step Reasoning Process
"""

import sys
import os
sys.path.append('.')

from dcisionai_mcp_server.tools import DcisionAITools
from dcisionai_mcp_server.mathopt_model_builder import MathOptModelBuilder, HAS_MATHOPT
import asyncio
import json
import logging

# Enable debug logging
logging.basicConfig(level=logging.INFO)

async def test_mathopt_integration():
    print('🚀 Testing MathOpt Integration with 7-Step Reasoning')
    print('=' * 60)
    
    print(f'MathOpt Available: {"✅ Yes" if HAS_MATHOPT else "❌ No"}')
    if not HAS_MATHOPT:
        print('Install with: pip install ortools')
        return
    
    tools = DcisionAITools()
    
    # Portfolio optimization problem with individual stocks
    problem = '''
    Portfolio optimization for \$10M across individual stocks:
    - Technology: AAPL (12%), MSFT (12%), GOOGL (12%), AMZN (12%), META (12%)
    - Financial: JPM (8%), BAC (8%), WFC (8%), GS (8%), MS (8%)
    - Healthcare: JNJ (10%), PFE (10%), UNH (10%), ABBV (10%), MRK (10%)
    - Energy: XOM (6%), CVX (6%), COP (6%), EOG (6%), SLB (6%)
    
    Constraints:
    - Maximum 10% allocation to any single stock
    - Maximum 30% allocation to any single sector
    - Minimum 5% allocation to each sector for diversification
    - Total portfolio must equal 100%
    
    Objective: Maximize expected return
    '''
    
    print('📊 Problem: Portfolio optimization with individual stock constraints')
    print('Expected: 20 individual stock variables (5 stocks × 4 sectors)')
    print()
    
    # Step 1: Intent Classification
    print('Step 1: Intent Classification')
    intent = await tools.classify_intent(problem)
    print(f'✅ Intent: {intent.get("result", {}).get("intent", "unknown")}')
    print()
    
    # Step 2: Data Analysis
    print('Step 2: Data Analysis')
    data = await tools.analyze_data(problem, intent.get('result'))
    print(f'✅ Readiness: {data.get("result", {}).get("readiness_score", 0):.1%}')
    print()
    
    # Step 3: Solver Selection
    print('Step 3: Solver Selection')
    solver = await tools.select_solver('linear_programming', {'num_variables': 20, 'num_constraints': 10})
    print(f'✅ Solver: {solver.get("result", {}).get("selected_solver", "unknown")}')
    print()
    
    # Step 4: Enhanced Model Building with MathOpt
    print('Step 4: Enhanced Model Building (7-Step + MathOpt)')
    print('-' * 50)
    model = await tools.build_model(problem, intent.get('result'), data.get('result'), solver.get('result'))
    
    print(f'Status: {model["status"]}')
    if model['status'] == 'success':
        result = model.get('result', {})
        print(f'✅ Model built successfully!')
        print(f'Variables: {len(result.get("variables", []))}')
        print(f'Constraints: {len(result.get("constraints", []))}')
        print(f'Model Type: {result.get("model_type", "unknown")}')
        
        # Show reasoning steps
        reasoning = result.get('reasoning_steps', {})
        if reasoning:
            print('\n📋 7-Step Reasoning Process:')
            for i, (step, content) in enumerate(reasoning.items(), 1):
                print(f'  {i}. {step}: {content[:100]}...')
        
        # Show variables
        variables = result.get('variables', [])
        if variables:
            print(f'\n📊 Variables ({len(variables)}):')
            for i, var in enumerate(variables[:10]):  # Show first 10
                if isinstance(var, dict):
                    print(f'  {i+1}. {var.get("name", "unknown")}: {var.get("description", "no description")}')
            if len(variables) > 10:
                print(f'  ... and {len(variables) - 10} more variables')
        
        # Show constraints
        constraints = result.get('constraints', [])
        if constraints:
            print(f'\n🔒 Constraints ({len(constraints)}):')
            for i, constraint in enumerate(constraints[:5]):  # Show first 5
                if isinstance(constraint, dict):
                    print(f'  {i+1}. {constraint.get("expression", "unknown")}')
                    print(f'     {constraint.get("description", "no description")}')
            if len(constraints) > 5:
                print(f'  ... and {len(constraints) - 5} more constraints')
        
        # Show objective
        objective = result.get('objective', {})
        if isinstance(objective, dict):
            print(f'\n🎯 Objective: {objective.get("type", "unknown")} {objective.get("expression", "unknown")}')
            print(f'Description: {objective.get("description", "no description")}')
        
        # Show MathOpt integration
        mathopt_model = result.get('mathopt_model')
        if mathopt_model and mathopt_model.get('status') == 'success':
            print(f'\n🔧 MathOpt Integration: ✅ Success')
            print(f'  Model Name: {mathopt_model.get("model_name", "unknown")}')
            print(f'  Variables in MathOpt: {mathopt_model.get("validation", {}).get("variables_count", 0)}')
            print(f'  Constraints in MathOpt: {mathopt_model.get("validation", {}).get("constraints_count", 0)}')
            print(f'  Has Objective: {"✅ Yes" if mathopt_model.get("validation", {}).get("has_objective", False) else "❌ No"}')
        else:
            print(f'\n🔧 MathOpt Integration: ❌ Failed or not available')
        
        # Show validation summary
        validation = result.get('validation_summary', {})
        if validation:
            print(f'\n✅ Validation Summary:')
            print(f'  Variables Defined: {validation.get("variables_defined", 0)}')
            print(f'  Constraints Defined: {validation.get("constraints_defined", 0)}')
            print(f'  All Variables Used: {"✅ Yes" if validation.get("all_variables_used", False) else "❌ No"}')
            print(f'  Model Feasible: {"✅ Yes" if validation.get("model_is_feasible", False) else "❌ No"}')
        
    else:
        print(f'❌ Model building failed: {model.get("error", "Unknown error")}')
    
    print()
    print('🎉 MathOpt Integration Test Complete!')

def test_mathopt_builder_directly():
    """Test MathOpt model builder directly"""
    print('\n🔧 Testing MathOpt Model Builder Directly')
    print('=' * 50)
    
    if not HAS_MATHOPT:
        print('❌ MathOpt not available')
        return
    
    # Create a simple portfolio model
    reasoning_data = {
        "reasoning_steps": {
            "step1_decision_analysis": "Allocate to 3 stocks: AAPL, MSFT, GOOGL",
            "step2_constraint_analysis": "Max 50% per stock, total 100%",
            "step3_objective_analysis": "Maximize expected return",
            "step4_variable_design": "x1, x2, x3 for AAPL, MSFT, GOOGL",
            "step5_constraint_formulation": "x1 <= 0.5, x2 <= 0.5, x3 <= 0.5, x1+x2+x3=1",
            "step6_objective_formulation": "0.12*x1 + 0.10*x2 + 0.08*x3",
            "step7_validation": "All variables used"
        },
        "variables": [
            {"name": "x1", "type": "continuous", "bounds": "0 to 0.5", "description": "AAPL allocation"},
            {"name": "x2", "type": "continuous", "bounds": "0 to 0.5", "description": "MSFT allocation"},
            {"name": "x3", "type": "continuous", "bounds": "0 to 0.5", "description": "GOOGL allocation"}
        ],
        "constraints": [
            {"expression": "x1 <= 0.5", "description": "Max 50% in AAPL"},
            {"expression": "x2 <= 0.5", "description": "Max 50% in MSFT"},
            {"expression": "x3 <= 0.5", "description": "Max 50% in GOOGL"},
            {"expression": "x1 + x2 + x3 = 1", "description": "Total allocation 100%"}
        ],
        "objective": {
            "type": "maximize",
            "expression": "0.12*x1 + 0.10*x2 + 0.08*x3",
            "description": "Expected portfolio return"
        }
    }
    
    builder = MathOptModelBuilder()
    result = builder.build_model_from_reasoning(reasoning_data)
    
    print(f'MathOpt Builder Result: {result.get("status", "unknown")}')
    if result.get('status') == 'success':
        validation = result.get('validation', {})
        print(f'✅ Variables: {validation.get("variables_count", 0)}')
        print(f'✅ Constraints: {validation.get("constraints_count", 0)}')
        print(f'✅ Has Objective: {validation.get("has_objective", False)}')
        print(f'✅ Model Created: {validation.get("model_created", False)}')
    else:
        print(f'❌ Error: {result.get("error", "Unknown error")}')

if __name__ == "__main__":
    # Test MathOpt integration
    asyncio.run(test_mathopt_integration())
    
    # Test MathOpt builder directly
    test_mathopt_builder_directly()
