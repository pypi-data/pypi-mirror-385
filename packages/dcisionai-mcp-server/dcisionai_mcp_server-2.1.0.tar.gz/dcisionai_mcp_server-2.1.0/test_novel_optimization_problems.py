#!/usr/bin/env python3
"""
Test Enhanced Model Builder with Novel Optimization Problems
Avoiding training bias and hallucination patterns
"""

import sys
import os
sys.path.append('.')

from dcisionai_mcp_server.tools import DcisionAITools
import asyncio
import json
import logging
from datetime import datetime
import random

# Enable debug logging
logging.basicConfig(level=logging.INFO)

class NovelProblemTester:
    def __init__(self):
        self.tools = DcisionAITools()
        self.results = {}
        
    async def test_novel_problem(self, problem_name: str, problem_description: str, expected_variables: int = None, expected_constraints: int = None):
        """Test a novel optimization problem"""
        print(f'\n{"="*80}')
        print(f'🧪 TESTING NOVEL PROBLEM: {problem_name}')
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
    
    async def run_novel_tests(self):
        """Run tests with completely novel optimization problems"""
        print('🚀 TESTING ENHANCED MODEL BUILDER WITH NOVEL OPTIMIZATION PROBLEMS')
        print('=' * 80)
        print(f'Timestamp: {datetime.now().isoformat()}')
        print(f'Version: Enhanced with MathOpt + 7-Step Reasoning')
        print('🎯 Goal: Test with completely novel problems to avoid training bias')
        print()
        
        # Define completely novel test problems (not in training data)
        novel_problems = [
            {
                'name': 'Archaeological Site Excavation',
                'description': '''
                An archaeological team needs to optimize excavation of 7 ancient sites over 4 seasons.
                Sites: Site A (artifacts: 150, difficulty: 3), Site B (200, 2), Site C (100, 4), Site D (300, 1), Site E (80, 5), Site F (250, 2), Site G (120, 3)
                Seasons: Spring (weather: good, time: 90 days), Summer (excellent, 120 days), Fall (good, 80 days), Winter (poor, 60 days)
                Team: 12 archaeologists with different specializations
                Constraints: Each site can only be excavated in one season, each archaeologist can work on max 2 sites per season, weather affects excavation efficiency
                Budget: $500K total, excavation costs vary by site difficulty and season
                Objective: Maximize total artifacts discovered while staying within budget and respecting weather constraints
                ''',
                'expected_variables': 28,  # 7 sites × 4 seasons
                'expected_constraints': 15  # 7 site assignments + 4 season capacity + 4 budget
            },
            {
                'name': 'Space Mission Resource Allocation',
                'description': '''
                NASA needs to allocate resources for 5 space missions to different planets.
                Missions: Mars (priority: High, fuel: 1000L, crew: 6), Venus (Medium, 800L, 4), Jupiter (Low, 2000L, 8), Saturn (Medium, 1800L, 7), Pluto (Low, 3000L, 5)
                Resources: Fuel (5000L available), Crew (20 astronauts), Equipment (15 units), Budget ($2B)
                Launch Windows: Mars (every 26 months), Venus (every 19 months), Jupiter (every 13 months), Saturn (every 29 months), Pluto (every 248 years)
                Constraints: Each mission needs minimum crew size, fuel requirements must be met, equipment allocation per mission, budget limits
                Risk Factors: Mission success probability varies by planet and crew experience
                Objective: Maximize expected scientific return while minimizing risk and staying within resource constraints
                ''',
                'expected_variables': 5,   # 5 missions
                'expected_constraints': 8  # 5 resource constraints + 3 global limits
            },
            {
                'name': 'Underwater Cable Network',
                'description': '''
                A telecommunications company needs to lay underwater cables connecting 8 coastal cities.
                Cities: A, B, C, D, E, F, G, H (populations: 2M, 1.5M, 3M, 800K, 1.2M, 2.5M, 900K, 1.8M)
                Cable Routes: 12 possible routes with different distances and depths
                Cable Types: Standard (cost: $100K/km, capacity: 10Gbps), Premium ($150K/km, 50Gbps), Ultra ($200K/km, 100Gbps)
                Constraints: Each city must be connected, maximum 2 cable types per route, depth affects cable type selection, capacity must meet demand
                Environmental: Some routes pass through protected marine areas (restrictions apply)
                Objective: Minimize total cost while ensuring all cities are connected and capacity requirements are met
                ''',
                'expected_variables': 36,  # 12 routes × 3 cable types
                'expected_constraints': 20  # 8 city connections + 12 route constraints
            },
            {
                'name': 'Quantum Computing Resource Scheduling',
                'description': '''
                A quantum computing lab needs to schedule 6 quantum algorithms on 3 quantum computers.
                Algorithms: Shor (qubits: 20, time: 4h, priority: High), Grover (15, 2h, Medium), VQE (25, 6h, High), QAOA (18, 3h, Medium), HHL (30, 8h, Low), VQC (12, 1h, High)
                Computers: Q1 (qubits: 50, reliability: 95%), Q2 (40, 90%), Q3 (35, 85%)
                Constraints: Each algorithm can only run on one computer, qubit requirements must be met, algorithms cannot be interrupted, priority affects scheduling order
                Maintenance: Each computer needs 2h maintenance every 24h, maintenance windows are fixed
                Objective: Minimize total completion time while respecting all constraints and maximizing priority-weighted completion
                ''',
                'expected_variables': 18,  # 6 algorithms × 3 computers
                'expected_constraints': 12  # 6 algorithm assignments + 3 computer capacity + 3 maintenance
            },
            {
                'name': 'Biodiversity Conservation Planning',
                'description': '''
                A conservation organization needs to protect 10 endangered species across 6 protected areas.
                Species: Tiger (population: 50, habitat: forest, threat: High), Elephant (200, grassland, Medium), Rhino (30, savanna, High), Panda (100, bamboo, Medium), Eagle (80, mountain, Low), Dolphin (150, ocean, Medium), Whale (40, ocean, High), Bear (60, forest, Medium), Wolf (90, forest, Low), Lion (70, savanna, Medium)
                Areas: Forest Reserve (capacity: 300, cost: $2M), Grassland Park (250, $1.5M), Savanna Sanctuary (200, $1.8M), Mountain Preserve (150, $2.5M), Ocean Marine Park (400, $3M), Bamboo Grove (100, $1M)
                Constraints: Each species can only be placed in compatible habitat, area capacity limits, budget of $15M, minimum population thresholds for viability
                Migration: Some species need migration corridors between areas
                Objective: Maximize total protected population while minimizing cost and ensuring species viability
                ''',
                'expected_variables': 60,  # 10 species × 6 areas
                'expected_constraints': 16  # 10 species assignments + 6 area capacity
            },
            {
                'name': 'Cryptocurrency Mining Optimization',
                'description': '''
                A crypto mining operation needs to optimize mining across 5 different cryptocurrencies.
                Cryptocurrencies: Bitcoin (difficulty: High, reward: 6.25 BTC, power: 2000W), Ethereum (Medium, 2 ETH, 1500W), Litecoin (Low, 12.5 LTC, 800W), Monero (Medium, 0.6 XMR, 1200W), Dogecoin (Low, 10000 DOGE, 600W)
                Mining Rigs: 20 rigs with different hash rates and power consumption
                Power: 50kW total available, electricity cost $0.12/kWh
                Pool Fees: Bitcoin (2%), Ethereum (1%), Litecoin (1.5%), Monero (1%), Dogecoin (0.5%)
                Constraints: Power consumption cannot exceed available power, each rig can mine one currency at a time, pool fees reduce profits
                Market: Cryptocurrency prices fluctuate, need to consider price volatility
                Objective: Maximize daily profit while respecting power constraints and considering market volatility
                ''',
                'expected_variables': 100, # 20 rigs × 5 cryptocurrencies
                'expected_constraints': 25  # 20 rig assignments + 5 power constraints
            },
            {
                'name': 'Autonomous Vehicle Fleet Management',
                'description': '''
                A ride-sharing company needs to optimize its fleet of 15 autonomous vehicles across 8 city zones.
                Vehicles: AV1-AV15 (capacity: 4, battery: 100%, efficiency: 5mi/kWh), different models with varying characteristics
                Zones: Downtown (demand: High, distance: 2mi avg), Suburb (Medium, 8mi), Airport (High, 15mi), University (Medium, 5mi), Mall (Low, 3mi), Hospital (High, 4mi), Stadium (Variable, 6mi), Business (Medium, 7mi)
                Time Periods: Morning (6-10AM), Afternoon (10AM-2PM), Evening (2-6PM), Night (6-10PM)
                Constraints: Each vehicle can only be in one zone at a time, battery must be above 20% for operation, demand must be met, charging stations available in 3 zones
                Dynamic: Demand varies by time and events, vehicles need repositioning between zones
                Objective: Maximize revenue while minimizing empty miles and ensuring adequate coverage
                ''',
                'expected_variables': 480, # 15 vehicles × 8 zones × 4 time periods
                'expected_constraints': 60  # 15 vehicle constraints + 8 zone demand + 4 time period + 3 charging
            },
            {
                'name': 'Renewable Energy Grid Optimization',
                'description': '''
                A utility company needs to optimize renewable energy sources across 12 grid nodes.
                Sources: Solar (capacity: 100MW, cost: $50/MWh, reliability: 80%), Wind (150MW, $40/MWh, 70%), Hydro (80MW, $30/MWh, 95%), Geothermal (60MW, $60/MWh, 90%), Biomass (40MW, $70/MWh, 85%)
                Nodes: N1-N12 (demand: 20-50MW each, distance: 5-25km from sources)
                Storage: Battery systems (capacity: 200MWh, efficiency: 90%, cost: $100/MWh)
                Constraints: Each source can supply multiple nodes, transmission losses (2% per 10km), storage capacity limits, demand must be met 24/7
                Weather: Solar and wind generation varies with weather conditions
                Objective: Minimize total cost while ensuring reliable power supply and maximizing renewable energy usage
                ''',
                'expected_variables': 60,  # 5 sources × 12 nodes
                'expected_constraints': 17  # 12 demand + 5 source capacity
            }
        ]
        
        # Run all novel tests
        for problem in novel_problems:
            await self.test_novel_problem(
                problem['name'],
                problem['description'],
                problem['expected_variables'],
                problem['expected_constraints']
            )
        
        # Generate summary report
        self.generate_novel_summary_report()
    
    def generate_novel_summary_report(self):
        """Generate a summary report of all novel tests"""
        print(f'\n{"="*80}')
        print('📊 NOVEL PROBLEMS SUMMARY REPORT')
        print(f'{"="*80}')
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results.values() if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        print(f'Total Novel Tests: {total_tests}')
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
        with open('../NOVEL_PROBLEMS_TEST_RESULTS.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f'📄 Detailed results saved to: NOVEL_PROBLEMS_TEST_RESULTS.json')
        print(f'🎉 Novel Problems Testing Complete!')

async def main():
    tester = NovelProblemTester()
    await tester.run_novel_tests()

if __name__ == "__main__":
    asyncio.run(main())
