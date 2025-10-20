#!/usr/bin/env python3
"""
Test Real MCP Server Results
============================

This script tests our actual MCP server with real optimization problems
and captures the genuine outputs for documentation.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the MCP server path
sys.path.append('mcp-server/src')
from dcisionai_mcp_server.tools import DcisionAITools

class RealMCPTester:
    def __init__(self):
        self.tools = DcisionAITools()
        self.results = {}
    
    async def test_production_planning(self):
        """Test production planning optimization problem."""
        print("=== TESTING PRODUCTION PLANNING PROBLEM ===")
        
        problem = """I have 3 production lines that can produce 120, 100, and 90 units per hour respectively, at costs of $45, $50, and $55 per hour. I need to produce at least 800 units to meet demand. Minimize total production cost."""
        
        print(f"Problem: {problem}")
        print()
        
        try:
            # Step 1: Classify Intent
            print("Step 1: Classifying Intent...")
            intent = await self.tools.classify_intent(problem)
            print(f"✅ Intent classified: {intent['result']['optimization_type']}")
            print()
            
            # Step 2: Analyze Data
            print("Step 2: Analyzing Data...")
            data = await self.tools.analyze_data(problem, intent['result'])
            print(f"✅ Data analyzed: {data['result']['readiness_score']} readiness score")
            print()
            
            # Step 3: Build Model
            print("Step 3: Building Model...")
            model = await self.tools.build_model(problem, intent['result'], data['result'])
            print(f"✅ Model built: {model['status']}")
            
            # Extract the raw response for analysis
            if 'raw_response' in model['result']:
                print("📋 Model Details:")
                print(f"   - Variables: {len(model['result'].get('variables', []))}")
                print(f"   - Constraints: {len(model['result'].get('constraints', []))}")
                print(f"   - Objective: {model['result'].get('objective', {}).get('expression', 'N/A')}")
            print()
            
            # Step 4: Solve Optimization (if model is valid)
            if model['status'] == 'success' and 'raw_response' not in model['result']:
                print("Step 4: Solving Optimization...")
                solution = await self.tools.solve_optimization(problem, intent['result'], data['result'], model['result'])
                print(f"✅ Solution: {solution['status']}")
                if solution['status'] == 'success':
                    print(f"   - Objective Value: {solution['result'].get('objective_value', 'N/A')}")
                    print(f"   - Status: {solution['result'].get('status', 'N/A')}")
                print()
                
                # Step 5: Explain Results
                print("Step 5: Explaining Results...")
                explanation = await self.tools.explain_optimization(problem, intent['result'], data['result'], model['result'], solution['result'])
                print(f"✅ Explanation: {explanation['status']}")
                print()
            else:
                print("⚠️ Skipping optimization due to model parsing issues")
                print()
            
            # Store results
            self.results['production_planning'] = {
                'problem': problem,
                'intent': intent,
                'data_analysis': data,
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in production planning test: {e}")
            self.results['production_planning'] = {'error': str(e)}
    
    async def test_portfolio_optimization(self):
        """Test portfolio optimization problem."""
        print("=== TESTING PORTFOLIO OPTIMIZATION PROBLEM ===")
        
        problem = """I need to allocate $100K across 3 stocks with expected returns of 8%, 12%, and 15% and risks of 10%, 15%, and 20%. I want to maximize return while keeping risk below 18%."""
        
        print(f"Problem: {problem}")
        print()
        
        try:
            # Step 1: Classify Intent
            print("Step 1: Classifying Intent...")
            intent = await self.tools.classify_intent(problem)
            print(f"✅ Intent classified: {intent['result']['optimization_type']}")
            print()
            
            # Step 2: Analyze Data
            print("Step 2: Analyzing Data...")
            data = await self.tools.analyze_data(problem, intent['result'])
            print(f"✅ Data analyzed: {data['result']['readiness_score']} readiness score")
            print()
            
            # Step 3: Build Model
            print("Step 3: Building Model...")
            model = await self.tools.build_model(problem, intent['result'], data['result'])
            print(f"✅ Model built: {model['status']}")
            
            # Extract the raw response for analysis
            if 'raw_response' in model['result']:
                print("📋 Model Details:")
                print(f"   - Variables: {len(model['result'].get('variables', []))}")
                print(f"   - Constraints: {len(model['result'].get('constraints', []))}")
                print(f"   - Objective: {model['result'].get('objective', {}).get('expression', 'N/A')}")
            print()
            
            # Store results
            self.results['portfolio_optimization'] = {
                'problem': problem,
                'intent': intent,
                'data_analysis': data,
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in portfolio optimization test: {e}")
            self.results['portfolio_optimization'] = {'error': str(e)}
    
    async def test_healthcare_scheduling(self):
        """Test healthcare scheduling problem."""
        print("=== TESTING HEALTHCARE SCHEDULING PROBLEM ===")
        
        problem = """I manage a hospital with 3 operating rooms and 5 surgeons. Each surgeon has different specialties and availability. I need to schedule 12 surgeries over 2 days, minimizing total waiting time while respecting surgeon availability and room capacity."""
        
        print(f"Problem: {problem}")
        print()
        
        try:
            # Step 1: Classify Intent
            print("Step 1: Classifying Intent...")
            intent = await self.tools.classify_intent(problem)
            print(f"✅ Intent classified: {intent['result']['optimization_type']}")
            print()
            
            # Step 2: Analyze Data
            print("Step 2: Analyzing Data...")
            data = await self.tools.analyze_data(problem, intent['result'])
            print(f"✅ Data analyzed: {data['result']['readiness_score']} readiness score")
            print()
            
            # Step 3: Build Model
            print("Step 3: Building Model...")
            model = await self.tools.build_model(problem, intent['result'], data['result'])
            print(f"✅ Model built: {model['status']}")
            
            # Extract the raw response for analysis
            if 'raw_response' in model['result']:
                print("📋 Model Details:")
                print(f"   - Variables: {len(model['result'].get('variables', []))}")
                print(f"   - Constraints: {len(model['result'].get('constraints', []))}")
                print(f"   - Objective: {model['result'].get('objective', {}).get('expression', 'N/A')}")
            print()
            
            # Store results
            self.results['healthcare_scheduling'] = {
                'problem': problem,
                'intent': intent,
                'data_analysis': data,
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in healthcare scheduling test: {e}")
            self.results['healthcare_scheduling'] = {'error': str(e)}
    
    def save_results(self):
        """Save all test results to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"real_mcp_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"📁 Results saved to: {filename}")
        return filename
    
    async def run_all_tests(self):
        """Run all optimization tests."""
        print("🚀 Starting Real MCP Server Tests")
        print("=" * 50)
        print()
        
        await self.test_production_planning()
        print()
        await self.test_portfolio_optimization()
        print()
        await self.test_healthcare_scheduling()
        print()
        
        # Save results
        filename = self.save_results()
        
        print("=" * 50)
        print("✅ All tests completed!")
        print(f"📊 Results saved to: {filename}")
        
        return self.results

async def main():
    """Main test function."""
    tester = RealMCPTester()
    results = await tester.run_all_tests()
    
    # Print summary
    print("\n📋 TEST SUMMARY:")
    print("-" * 30)
    for test_name, result in results.items():
        if 'error' in result:
            print(f"❌ {test_name}: FAILED - {result['error']}")
        else:
            print(f"✅ {test_name}: SUCCESS")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
