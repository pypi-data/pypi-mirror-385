#!/usr/bin/env python3
"""
Test MathOpt Constraint Parsing Fix
"""

import sys
import os
sys.path.append('.')

from dcisionai_mcp_server.mathopt_model_builder import MathOptModelBuilder
import json

def test_mathopt_constraint_parsing():
    """Test the fixed MathOpt constraint parsing"""
    print('🧪 Testing MathOpt Constraint Parsing Fix')
    print('=' * 60)
    
    # Test data with simple portfolio optimization
    test_data = {
        "reasoning_steps": {
            "step1_decision_analysis": "Allocate to individual stocks: AAPL, MSFT, GOOGL",
            "step2_constraint_analysis": "Max 10% per stock, total 100%",
            "step3_objective_analysis": "Maximize expected portfolio return",
            "step4_variable_design": "Individual stock allocation variables",
            "step5_constraint_formulation": "Stock limits, total allocation",
            "step6_objective_formulation": "Weighted sum of expected returns",
            "step7_validation": "All variables used in constraints and objective"
        },
        "variables": [
            {"name": "x_AAPL", "type": "continuous", "bounds": "0 to 0.1", "description": "AAPL allocation"},
            {"name": "x_MSFT", "type": "continuous", "bounds": "0 to 0.1", "description": "MSFT allocation"},
            {"name": "x_GOOGL", "type": "continuous", "bounds": "0 to 0.1", "description": "GOOGL allocation"}
        ],
        "constraints": [
            {"expression": "x_AAPL + x_MSFT + x_GOOGL = 1", "description": "Total allocation 100%"},
            {"expression": "x_AAPL <= 0.1", "description": "Max 10% in AAPL"},
            {"expression": "x_MSFT <= 0.1", "description": "Max 10% in MSFT"},
            {"expression": "x_GOOGL <= 0.1", "description": "Max 10% in GOOGL"}
        ],
        "objective": {
            "type": "maximize",
            "expression": "0.12*x_AAPL + 0.10*x_MSFT + 0.08*x_GOOGL",
            "description": "Expected portfolio return"
        }
    }
    
    # Test the MathOpt model builder
    builder = MathOptModelBuilder()
    result = builder.build_model_from_reasoning(test_data)
    
    print(f'Status: {result.get("status", "unknown")}')
    
    if result.get('status') == 'success':
        print('✅ MathOpt model built successfully!')
        
        validation = result.get('validation', {})
        print(f'Variables: {validation.get("variables_count", 0)}')
        print(f'Constraints: {validation.get("constraints_count", 0)}')
        print(f'Has Objective: {validation.get("has_objective", False)}')
        print(f'Model Created: {validation.get("model_created", False)}')
        
        # Test individual parsing functions
        print('\n🔍 Testing Individual Parsing Functions:')
        
        # Test linear expression parsing
        test_expressions = [
            "0.12*x_AAPL + 0.10*x_MSFT",
            "x_AAPL + x_MSFT + x_GOOGL",
            "0.1",
            "x_AAPL"
        ]
        
        for expr in test_expressions:
            try:
                parsed = builder._parse_linear_expression(expr)
                print(f'  Expression "{expr}" -> {type(parsed).__name__}: {parsed}')
            except Exception as e:
                print(f'  Expression "{expr}" -> ERROR: {e}')
        
        # Test constraint parsing
        test_constraints = [
            "x_AAPL + x_MSFT + x_GOOGL = 1",
            "x_AAPL <= 0.1",
            "x_MSFT >= 0.05"
        ]
        
        print('\n🔍 Testing Constraint Parsing:')
        for constraint in test_constraints:
            try:
                parsed = builder._parse_constraint(constraint)
                if parsed:
                    print(f'  Constraint "{constraint}" -> {parsed}')
                else:
                    print(f'  Constraint "{constraint}" -> Failed to parse')
            except Exception as e:
                print(f'  Constraint "{constraint}" -> ERROR: {e}')
        
    else:
        print(f'❌ MathOpt model building failed: {result.get("error", "Unknown error")}')
    
    return result

if __name__ == "__main__":
    test_mathopt_constraint_parsing()
