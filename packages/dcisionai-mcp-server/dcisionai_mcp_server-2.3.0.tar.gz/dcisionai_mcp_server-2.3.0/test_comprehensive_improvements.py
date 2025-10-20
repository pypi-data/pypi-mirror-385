#!/usr/bin/env python3
"""
Comprehensive test of all improvements made to the DcisionAI MCP server:
1. Enhanced JSON parsing robustness
2. MathOpt constraint parsing with MathOptFormat structure
3. Enhanced variable expansion for multi-dimensional problems
4. Truth Guardian validation
5. Knowledge Base integration
"""

import asyncio
import json
from dcisionai_mcp_server.tools import DcisionAITools

async def test_comprehensive_improvements():
    print("🧪 Comprehensive Test of All Improvements")
    print("=" * 60)
    
    tools = DcisionAITools()
    
    # Test 1: Enhanced JSON Parsing
    print("\n📋 Test 1: Enhanced JSON Parsing")
    print("-" * 40)
    
    test_cases = [
        '{"intent": "optimization", "type": "linear_programming"}',
        '```json\n{"intent": "optimization", "type": "linear_programming"}\n```',
        'Here is the result: {"intent": "optimization", "type": "linear_programming"}',
        '{"intent": "optimization", "type": "linear_programming", "extra": "data"}',
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = tools._parse_json(test_case)
        if isinstance(result, dict) and 'intent' in result:
            print(f"✅ Test case {i}: JSON parsed successfully")
        else:
            print(f"❌ Test case {i}: JSON parsing failed")
    
    # Test 2: MathOpt Constraint Parsing
    print("\n🔧 Test 2: MathOpt Constraint Parsing")
    print("-" * 40)
    
    try:
        from dcisionai_mcp_server.mathopt_model_builder import MathOptModelBuilder
        builder = MathOptModelBuilder()
        
        # Test constraint parsing
        test_constraints = [
            "x1 + x2 <= 1",
            "x1 >= 0.1", 
            "x1 + x2 = 1",
            "0.12*x1 + 0.08*x2 <= 0.5"
        ]
        
        for constraint in test_constraints:
            result = builder._parse_constraint_to_mathopt_format(constraint)
            if result and 'function' in result and 'set' in result:
                print(f"✅ Constraint '{constraint}' parsed successfully")
            else:
                print(f"❌ Constraint '{constraint}' parsing failed")
                
    except Exception as e:
        print(f"❌ MathOpt constraint parsing test failed: {e}")
    
    # Test 3: Enhanced Variable Expansion
    print("\n📊 Test 3: Enhanced Variable Expansion")
    print("-" * 40)
    
    test_problems = [
        {
            "description": "Nurse scheduling with 3 nurses × 2 days × 2 shifts",
            "expected_variables": 12,
            "expected_type": "scheduling"
        },
        {
            "description": "Portfolio optimization with 5 individual stocks: AAPL, MSFT, GOOGL, TSLA, AMZN",
            "expected_variables": 5,
            "expected_type": "portfolio_optimization"
        },
        {
            "description": "Vehicle routing with 3 vehicles × 10 customers",
            "expected_variables": 30,
            "expected_type": "routing"
        }
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n🔍 Problem {i}: {problem['description']}")
        
        # Test intent classification
        intent_result = await tools.classify_intent(problem['description'])
        if intent_result.get('status') == 'success':
            intent_type = intent_result.get('result', {}).get('intent', '')
            print(f"✅ Intent classification: {intent_type}")
        else:
            print(f"❌ Intent classification failed")
            continue
        
        # Test data analysis
        data_result = await tools.analyze_data(problem['description'], intent_result.get('result'))
        if data_result.get('status') == 'success':
            readiness = data_result.get('result', {}).get('readiness_score', 0)
            print(f"✅ Data analysis: {readiness*100:.1f}% readiness")
        else:
            print(f"❌ Data analysis failed")
            continue
        
        # Test solver selection
        solver_result = await tools.select_solver(
            intent_result.get('result', {}).get('optimization_type', 'linear_programming'),
            {'variables': problem['expected_variables'], 'constraints': 5}
        )
        if solver_result.get('status') == 'success':
            solver = solver_result.get('result', {}).get('selected_solver', '')
            print(f"✅ Solver selection: {solver}")
        else:
            print(f"❌ Solver selection failed")
            continue
        
        # Test model building
        model_result = await tools.build_model(
            problem['description'],
            intent_result.get('result'),
            data_result.get('result'),
            solver_result.get('result')
        )
        
        if model_result.get('status') == 'success':
            variables = model_result.get('result', {}).get('variables', [])
            actual_count = len(variables) if isinstance(variables, list) else 0
            expected_count = problem['expected_variables']
            
            print(f"✅ Model building: {actual_count} variables created")
            if actual_count == expected_count:
                print(f"✅ Variable count matches expected: {expected_count}")
            else:
                print(f"⚠️  Variable count mismatch: expected {expected_count}, got {actual_count}")
            
            # Show first few variables
            if isinstance(variables, list) and len(variables) > 0:
                print(f"📋 Sample variables:")
                for j, var in enumerate(variables[:3]):
                    if isinstance(var, dict):
                        print(f"   {j+1}. {var.get('name', 'unknown')}")
                if len(variables) > 3:
                    print(f"   ... and {len(variables) - 3} more")
        else:
            print(f"❌ Model building failed: {model_result.get('error', 'Unknown error')}")
    
    # Test 4: Truth Guardian Validation
    print("\n🛡️  Test 4: Truth Guardian Validation")
    print("-" * 40)
    
    # Test with failed optimization
    fake_failed_optimization = {
        "status": "error",
        "result": {"status": "infeasible"}
    }
    
    explain_result = await tools.explain_optimization(
        "Test problem",
        optimization_solution=fake_failed_optimization
    )
    
    if explain_result.get('status') == 'error':
        print("✅ Truth Guardian correctly rejected explanation for failed optimization")
    else:
        print("❌ Truth Guardian failed to reject explanation for failed optimization")
    
    simulate_result = await tools.simulate_scenarios(
        "Test problem",
        optimization_solution=fake_failed_optimization
    )
    
    if simulate_result.get('status') == 'error':
        print("✅ Truth Guardian correctly rejected simulation for failed optimization")
    else:
        print("❌ Truth Guardian failed to reject simulation for failed optimization")
    
    # Test 5: Knowledge Base Integration
    print("\n📚 Test 5: Knowledge Base Integration")
    print("-" * 40)
    
    try:
        kb_context = tools.kb.search("production planning optimization")
        if kb_context and "Similar:" in kb_context:
            print("✅ Knowledge Base search working")
        else:
            print("⚠️  Knowledge Base search returned limited results")
        
        guidance = tools.kb.get_problem_type_guidance("portfolio optimization")
        if guidance and "Portfolio Optimization" in guidance:
            print("✅ Knowledge Base guidance working")
        else:
            print("⚠️  Knowledge Base guidance returned limited results")
            
    except Exception as e:
        print(f"❌ Knowledge Base integration test failed: {e}")
    
    print("\n🎉 Comprehensive Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_comprehensive_improvements())
