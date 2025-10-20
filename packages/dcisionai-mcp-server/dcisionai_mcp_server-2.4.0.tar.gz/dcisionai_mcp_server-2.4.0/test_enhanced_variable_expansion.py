#!/usr/bin/env python3
"""
Test Enhanced Variable Expansion Prompts
"""

import sys
import os
sys.path.append('.')

from dcisionai_mcp_server.tools import DcisionAITools
import asyncio
import json
import logging
from datetime import datetime

# Enable debug logging
logging.basicConfig(level=logging.INFO)

async def test_enhanced_variable_expansion():
    """Test the enhanced variable expansion prompts"""
    print('🧪 Testing Enhanced Variable Expansion Prompts')
    print('=' * 60)
    
    tools = DcisionAITools()
    
    # Test with a complex multi-dimensional problem
    problem = '''
    A hospital needs to schedule nurses for a 7-day week with 3 shifts per day.
    Nurses: 10 available nurses (N1-N10)
    Shifts: Morning (6 AM - 2 PM), Afternoon (2 PM - 10 PM), Night (10 PM - 6 AM)
    Requirements: Each shift needs exactly 3 nurses, each nurse can work max 5 shifts per week, each nurse needs at least 1 day off
    Preferences: Some nurses prefer certain shifts, some have availability restrictions
    Objective: Maximize nurse satisfaction while meeting all coverage requirements
    '''
    
    print('📊 Problem: Nurse scheduling with 10 nurses × 7 days × 3 shifts')
    print('Expected: 210 individual variables (10 × 7 × 3)')
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
    solver = await tools.select_solver('mixed_integer_linear_programming', {'num_variables': 210, 'num_constraints': 31})
    print(f'✅ Solver: {solver.get("result", {}).get("selected_solver", "unknown")}')
    print()
    
    # Step 4: Enhanced Model Building with Variable Expansion
    print('Step 4: Enhanced Model Building with Variable Expansion')
    print('-' * 50)
    model = await tools.build_model(problem, intent.get('result'), data.get('result'), solver.get('result'))
    
    print(f'Status: {model["status"]}')
    if model['status'] == 'success':
        result = model.get('result', {})
        variables = result.get('variables', [])
        constraints = result.get('constraints', [])
        reasoning = result.get('reasoning_steps', {})
        
        print(f'✅ Model built successfully!')
        print(f'Variables: {len(variables)}')
        print(f'Constraints: {len(constraints)}')
        print(f'Model Type: {result.get("model_type", "unknown")}')
        
        # Show reasoning steps
        if reasoning:
            print('\n📋 7-Step Reasoning Process:')
            for i, (step, content) in enumerate(reasoning.items(), 1):
                print(f'  {i}. {step}: {content[:100]}...')
        
        # Show variables
        if variables:
            print(f'\n📊 Variables ({len(variables)}):')
            for i, var in enumerate(variables[:10]):  # Show first 10
                if isinstance(var, dict):
                    print(f'  {i+1}. {var.get("name", "unknown")}: {var.get("description", "no description")}')
            if len(variables) > 10:
                print(f'  ... and {len(variables) - 10} more variables')
        
        # Show constraints
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
            print(f'\n🎯 Objective: {objective.get("type", "unknown")} {objective.get("expression", "unknown")[:100]}...')
        
        # Show MathOpt integration
        mathopt_model = result.get('mathopt_model')
        if mathopt_model and mathopt_model.get('status') == 'success':
            print(f'\n🔧 MathOpt Integration: ✅ Success')
        else:
            print(f'\n🔧 MathOpt Integration: ❌ Failed or not available')
        
        # Validation
        validation = result.get('validation_summary', {})
        if validation:
            print(f'\n✅ Validation:')
            print(f'  All Variables Used: {"✅ Yes" if validation.get("all_variables_used", False) else "❌ No"}')
            print(f'  Model Feasible: {"✅ Yes" if validation.get("model_is_feasible", False) else "❌ No"}')
        
        # Check against expectations
        expected_variables = 210  # 10 nurses × 7 days × 3 shifts
        if len(variables) != expected_variables:
            print(f'\n⚠️  Variable Count Mismatch: Expected {expected_variables}, Got {len(variables)}')
            if len(variables) < expected_variables:
                print(f'   ❌ Still oversimplified - need to expand multi-dimensional structure')
            else:
                print(f'   ✅ More variables than expected - good expansion')
        else:
            print(f'\n✅ Variable Count Match: Got {len(variables)} variables as expected')
        
    else:
        print(f'❌ Model building failed: {model.get("error", "Unknown error")}')
    
    print()
    print('🎉 Enhanced Variable Expansion Test Complete!')

if __name__ == "__main__":
    asyncio.run(test_enhanced_variable_expansion())
