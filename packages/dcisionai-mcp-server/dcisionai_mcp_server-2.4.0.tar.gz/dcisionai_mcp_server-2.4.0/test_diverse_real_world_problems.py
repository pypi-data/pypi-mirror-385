#!/usr/bin/env python3
"""
Test Enhanced Model Builder with Diverse Real-World Optimization Problems
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

class DiverseProblemTester:
    def __init__(self):
        self.tools = DcisionAITools()
        self.results = {}
        
    async def test_problem(self, problem_name: str, problem_description: str, expected_variables: int = None, expected_constraints: int = None):
        """Test a single optimization problem"""
        print(f'\n{"="*80}')
        print(f'🧪 TESTING: {problem_name}')
        print(f'{"="*80}')
        print(f'Problem: {problem_description[:200]}...')
        if expected_variables:
            print(f'Expected Variables: {expected_variables}')
        if expected_constraints:
            print(f'Expected Constraints: {expected_constraints}')
        print()
        
        try:
            # Step 1: Intent Classification
            print('Step 1: Intent Classification')
            intent = await self.tools.classify_intent(problem_description)
            print(f'✅ Intent: {intent.get("result", {}).get("intent", "unknown")}')
            print(f'   Industry: {intent.get("result", {}).get("industry", "unknown")}')
            print(f'   Type: {intent.get("result", {}).get("optimization_type", "unknown")}')
            print(f'   Complexity: {intent.get("result", {}).get("complexity", "unknown")}')
            print()
            
            # Step 2: Data Analysis
            print('Step 2: Data Analysis')
            data = await self.tools.analyze_data(problem_description, intent.get('result'))
            print(f'✅ Readiness: {data.get("result", {}).get("readiness_score", 0):.1%}')
            print(f'   Variables Identified: {data.get("result", {}).get("variables_identified", [])}')
            print()
            
            # Step 3: Solver Selection
            print('Step 3: Solver Selection')
            opt_type = intent.get('result', {}).get('optimization_type', 'linear_programming')
            problem_size = {
                'num_variables': expected_variables or 5,
                'num_constraints': expected_constraints or 3
            }
            solver = await self.tools.select_solver(opt_type, problem_size)
            print(f'✅ Solver: {solver.get("result", {}).get("selected_solver", "unknown")}')
            print()
            
            # Step 4: Model Building
            print('Step 4: Enhanced Model Building (7-Step + MathOpt)')
            print('-' * 50)
            model = await self.tools.build_model(problem_description, intent.get('result'), data.get('result'), solver.get('result'))
            
            result = {
                'problem_name': problem_name,
                'problem_description': problem_description,
                'intent_classification': intent,
                'data_analysis': data,
                'solver_selection': solver,
                'model_building': model,
                'expected_variables': expected_variables,
                'expected_constraints': expected_constraints,
                'timestamp': datetime.now().isoformat()
            }
            
            if model['status'] == 'success':
                model_result = model.get('result', {})
                variables = model_result.get('variables', [])
                constraints = model_result.get('constraints', [])
                reasoning = model_result.get('reasoning_steps', {})
                
                print(f'✅ Model built successfully!')
                print(f'   Variables: {len(variables)}')
                print(f'   Constraints: {len(constraints)}')
                print(f'   Model Type: {model_result.get("model_type", "unknown")}')
                
                # Show key variables
                if variables:
                    print(f'\n📊 Key Variables:')
                    for i, var in enumerate(variables[:5]):
                        if isinstance(var, dict):
                            print(f'   {i+1}. {var.get("name", "unknown")}: {var.get("description", "no description")}')
                    if len(variables) > 5:
                        print(f'   ... and {len(variables) - 5} more variables')
                
                # Show key constraints
                if constraints:
                    print(f'\n🔒 Key Constraints:')
                    for i, constraint in enumerate(constraints[:3]):
                        if isinstance(constraint, dict):
                            print(f'   {i+1}. {constraint.get("expression", "unknown")}')
                    if len(constraints) > 3:
                        print(f'   ... and {len(constraints) - 3} more constraints')
                
                # Show objective
                objective = model_result.get('objective', {})
                if isinstance(objective, dict):
                    print(f'\n🎯 Objective: {objective.get("type", "unknown")} {objective.get("expression", "unknown")[:100]}...')
                
                # Show MathOpt integration
                mathopt_model = model_result.get('mathopt_model')
                if mathopt_model and mathopt_model.get('status') == 'success':
                    print(f'\n🔧 MathOpt Integration: ✅ Success')
                else:
                    print(f'\n🔧 MathOpt Integration: ❌ Failed or not available')
                
                # Validation
                validation = model_result.get('validation_summary', {})
                if validation:
                    print(f'\n✅ Validation:')
                    print(f'   All Variables Used: {"✅ Yes" if validation.get("all_variables_used", False) else "❌ No"}')
                    print(f'   Model Feasible: {"✅ Yes" if validation.get("model_is_feasible", False) else "❌ No"}')
                
                # Check against expectations
                if expected_variables and len(variables) != expected_variables:
                    print(f'\n⚠️  Variable Count Mismatch: Expected {expected_variables}, Got {len(variables)}')
                if expected_constraints and len(constraints) != expected_constraints:
                    print(f'\n⚠️  Constraint Count Mismatch: Expected {expected_constraints}, Got {len(constraints)}')
                
                result['success'] = True
                result['actual_variables'] = len(variables)
                result['actual_constraints'] = len(constraints)
                
            else:
                print(f'❌ Model building failed: {model.get("error", "Unknown error")}')
                result['success'] = False
                result['error'] = model.get('error', 'Unknown error')
            
            self.results[problem_name] = result
            return result
            
        except Exception as e:
            print(f'❌ Test failed with exception: {e}')
            result = {
                'problem_name': problem_name,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.results[problem_name] = result
            return result
    
    async def run_all_tests(self):
        """Run all diverse problem tests"""
        print('🚀 TESTING ENHANCED MODEL BUILDER WITH DIVERSE REAL-WORLD PROBLEMS')
        print('=' * 80)
        print(f'Timestamp: {datetime.now().isoformat()}')
        print(f'Version: Enhanced with MathOpt + 7-Step Reasoning')
        print()
        
        # Define diverse test problems
        test_problems = [
            {
                'name': 'Supply Chain Optimization',
                'description': '''
                A manufacturing company needs to optimize its supply chain for 3 products across 4 warehouses.
                Products: Widget A (demand: 1000 units), Widget B (demand: 800 units), Widget C (demand: 600 units)
                Warehouses: North (capacity: 500 units), South (capacity: 400 units), East (capacity: 300 units), West (capacity: 200 units)
                Shipping costs: North->A: $5, North->B: $4, North->C: $3, South->A: $6, South->B: $5, South->C: $4, East->A: $7, East->B: $6, East->C: $5, West->A: $8, West->B: $7, West->C: $6
                Constraints: Each warehouse has capacity limits, each product has demand requirements
                Objective: Minimize total shipping costs while meeting all demand
                ''',
                'expected_variables': 12,  # 3 products × 4 warehouses
                'expected_constraints': 7   # 4 capacity + 3 demand
            },
            {
                'name': 'Employee Scheduling',
                'description': '''
                A hospital needs to schedule nurses for a 7-day week with 3 shifts per day.
                Nurses: 10 available nurses (N1-N10)
                Shifts: Morning (6 AM - 2 PM), Afternoon (2 PM - 10 PM), Night (10 PM - 6 AM)
                Requirements: Each shift needs exactly 3 nurses, each nurse can work max 5 shifts per week, each nurse needs at least 1 day off
                Preferences: Some nurses prefer certain shifts, some have availability restrictions
                Objective: Maximize nurse satisfaction while meeting all coverage requirements
                ''',
                'expected_variables': 210,  # 10 nurses × 7 days × 3 shifts
                'expected_constraints': 31   # 21 shift requirements + 10 max shifts + other constraints
            },
            {
                'name': 'Investment Portfolio (Risk-Adjusted)',
                'description': '''
                An investment firm needs to allocate $50M across 8 asset classes with risk constraints.
                Assets: Stocks (expected return: 12%, risk: 20%), Bonds (8%, 5%), REITs (10%, 15%), Commodities (6%, 25%), International (11%, 18%), Emerging Markets (15%, 30%), Cash (2%, 1%), Alternatives (9%, 12%)
                Constraints: Max 30% in any single asset, min 5% in each asset, max 40% in high-risk assets (risk > 15%), total allocation = 100%
                Risk Budget: Portfolio risk (weighted average) must not exceed 15%
                Objective: Maximize expected return while staying within risk constraints
                ''',
                'expected_variables': 8,   # 8 asset classes
                'expected_constraints': 12  # 8 max allocation + 8 min allocation + 1 risk + 1 total
            },
            {
                'name': 'Production Planning (Multi-Period)',
                'description': '''
                A factory produces 4 products over 6 months with seasonal demand and capacity constraints.
                Products: Product A (profit: $50/unit), Product B ($40/unit), Product C ($60/unit), Product D ($35/unit)
                Monthly Capacity: 1000 units total production capacity
                Demand (units/month): A: [200,250,300,280,220,180], B: [150,180,200,190,160,140], C: [100,120,150,140,110,90], D: [80,100,120,110,90,70]
                Inventory: Can store up to 200 units of each product, holding cost $2/unit/month
                Setup Costs: $500 per product per month if produced
                Objective: Maximize profit over 6 months
                ''',
                'expected_variables': 48,   # 4 products × 6 months × 2 (production + inventory)
                'expected_constraints': 30  # 6 capacity + 24 demand + other constraints
            },
            {
                'name': 'Vehicle Routing (VRP)',
                'description': '''
                A delivery company has 5 vehicles and needs to deliver to 20 customers.
                Vehicles: V1-V5 (capacities: 100, 120, 80, 90, 110 units respectively)
                Customers: C1-C20 (demands: 5-25 units each, locations with distances)
                Depot: Central warehouse where all vehicles start and end
                Constraints: Each customer visited exactly once, vehicle capacity limits, maximum route length of 200 miles
                Distances: Symmetric distance matrix between all locations (depot + 20 customers)
                Objective: Minimize total distance traveled while serving all customers
                ''',
                'expected_variables': 105,  # 5 vehicles × 21 locations (depot + 20 customers)
                'expected_constraints': 25  # 20 customer visits + 5 capacity + other constraints
            },
            {
                'name': 'Resource Allocation (Project Management)',
                'description': '''
                A software company has 3 projects with 5 developers and needs to allocate resources optimally.
                Projects: Web App (priority: High, effort: 40 person-days), Mobile App (Medium, 30 person-days), API (Low, 20 person-days)
                Developers: D1-D5 (skills: [Web, Mobile, API], availability: [8,7,6,8,7] days)
                Skills Matrix: D1: [Web, API], D2: [Web, Mobile], D3: [Mobile, API], D4: [Web, Mobile, API], D5: [Web, API]
                Constraints: Each developer can work on max 2 projects, each project needs at least 1 developer, skill requirements must be met
                Deadlines: Web App (10 days), Mobile App (15 days), API (8 days)
                Objective: Maximize project completion while meeting deadlines and skill requirements
                ''',
                'expected_variables': 15,   # 3 projects × 5 developers
                'expected_constraints': 18  # 3 project requirements + 5 developer limits + 10 skill constraints
            },
            {
                'name': 'Facility Location',
                'description': '''
                A retail chain wants to open stores in 6 potential locations to serve 12 customer zones.
                Locations: L1-L6 (opening costs: $100K, $120K, $80K, $90K, $110K, $95K)
                Customer Zones: Z1-Z12 (demands: 50-200 customers each)
                Distances: Matrix of distances from each location to each customer zone
                Service Constraints: Each customer zone must be within 30 miles of at least one store
                Budget: Maximum $500K for opening stores
                Revenue: $50 per customer served per month
                Objective: Maximize net profit (revenue - opening costs) while serving all customers
                ''',
                'expected_variables': 18,   # 6 locations + 12 customer assignments
                'expected_constraints': 19  # 6 budget + 12 service + 1 total budget
            },
            {
                'name': 'Diet Optimization (Nutrition)',
                'description': '''
                A nutritionist needs to create a meal plan for a patient with specific dietary requirements.
                Foods: Chicken (protein: 25g, carbs: 0g, fat: 3g, calories: 120, cost: $2), Rice (2g, 28g, 0g, 130, $0.5), Vegetables (3g, 5g, 0g, 25, $1), Fish (22g, 0g, 1g, 100, $3), Bread (3g, 15g, 1g, 80, $0.3)
                Requirements: Protein: 50-80g, Carbs: 100-200g, Fat: 20-40g, Calories: 1500-2000, Max cost: $15/day
                Preferences: At least 2 servings of vegetables, no more than 3 servings of any single food
                Serving sizes: 100g portions
                Objective: Minimize cost while meeting all nutritional requirements
                ''',
                'expected_variables': 5,    # 5 food types
                'expected_constraints': 12  # 5 nutritional requirements + 5 max servings + 2 preferences
            }
        ]
        
        # Run all tests
        for problem in test_problems:
            await self.test_problem(
                problem['name'],
                problem['description'],
                problem['expected_variables'],
                problem['expected_constraints']
            )
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate a summary report of all tests"""
        print(f'\n{"="*80}')
        print('📊 SUMMARY REPORT')
        print(f'{"="*80}')
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results.values() if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        print(f'Total Tests: {total_tests}')
        print(f'Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)')
        print(f'Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)')
        print()
        
        # Detailed results
        for name, result in self.results.items():
            status = "✅ SUCCESS" if result.get('success', False) else "❌ FAILED"
            print(f'{status}: {name}')
            
            if result.get('success', False):
                actual_vars = result.get('actual_variables', 0)
                actual_constraints = result.get('actual_constraints', 0)
                expected_vars = result.get('expected_variables', 'N/A')
                expected_constraints = result.get('expected_constraints', 'N/A')
                
                print(f'   Variables: {actual_vars} (expected: {expected_vars})')
                print(f'   Constraints: {actual_constraints} (expected: {expected_constraints})')
                
                # Check if expectations were met
                var_match = expected_vars == 'N/A' or actual_vars == expected_vars
                constraint_match = expected_constraints == 'N/A' or actual_constraints == expected_constraints
                
                if var_match and constraint_match:
                    print(f'   ✅ Expectations met')
                else:
                    print(f'   ⚠️  Expectations not met')
            else:
                print(f'   Error: {result.get("error", "Unknown error")}')
            print()
        
        # Save detailed results
        with open('../DIVERSE_PROBLEMS_TEST_RESULTS.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f'📄 Detailed results saved to: DIVERSE_PROBLEMS_TEST_RESULTS.json')
        print(f'🎉 Diverse Problems Testing Complete!')

async def main():
    tester = DiverseProblemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
