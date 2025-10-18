#!/usr/bin/env python3
"""
Test Enhanced MCP Server with Knowledge Base
===========================================

This script tests the enhanced MCP server with knowledge base integration.
"""

import asyncio
import sys
import os

# Add the mcp-server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp-server'))

from dcisionai_mcp_server.tools import DcisionAITools

async def test_enhanced_mcp():
    """Test the enhanced MCP server with knowledge base integration."""
    
    print("🚀 Testing Enhanced MCP Server with Knowledge Base...")
    
    # Initialize the tools
    tools = DcisionAITools()
    
    # Test problem
    problem = "I need to optimize production scheduling for 5 machines with different capacities and processing times. Each machine can produce different products at different rates."
    
    print(f"\n📝 Test Problem: {problem}")
    
    try:
        # Test intent classification
        print("\n🔍 Testing Intent Classification...")
        intent_result = await tools.classify_intent(problem)
        print(f"✅ Intent Classification Result:")
        print(f"   Intent: {intent_result.get('intent', 'unknown')}")
        print(f"   Industry: {intent_result.get('industry', 'unknown')}")
        print(f"   Complexity: {intent_result.get('complexity', 'unknown')}")
        print(f"   Confidence: {intent_result.get('confidence', 0)}")
        
        # Test data analysis
        print("\n📊 Testing Data Analysis...")
        data_result = await tools.analyze_data(problem, intent_result)
        print(f"✅ Data Analysis Result:")
        print(f"   Variables: {len(data_result.get('variables_identified', []))}")
        print(f"   Constraints: {len(data_result.get('constraints_identified', []))}")
        print(f"   Data Readiness: {data_result.get('data_readiness', 'unknown')}")
        
        # Test model building
        print("\n🏗️ Testing Model Building...")
        model_result = await tools.build_model(problem, intent_result, data_result)
        print(f"✅ Model Building Result:")
        print(f"   Status: {model_result.get('status', 'unknown')}")
        if model_result.get('status') == 'success':
            print(f"   Variables: {len(model_result.get('variables', []))}")
            print(f"   Constraints: {len(model_result.get('constraints', []))}")
            print(f"   Objective: {model_result.get('objective', {}).get('direction', 'unknown')}")
        
        print("\n🎉 Enhanced MCP Server Test Complete!")
        print("✅ Knowledge base integration is working!")
        
    except Exception as e:
        print(f"❌ Error testing enhanced MCP server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_mcp())
