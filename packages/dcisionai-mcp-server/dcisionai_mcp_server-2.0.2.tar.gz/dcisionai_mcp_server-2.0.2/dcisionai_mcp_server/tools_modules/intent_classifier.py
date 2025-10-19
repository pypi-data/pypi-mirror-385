#!/usr/bin/env python3
"""
Intent Classification Tool
"""

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..core.bedrock_client import BedrockClient
from ..core.knowledge_base import KnowledgeBase
from ..utils.json_parser import parse_json

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Intent classification for optimization problems"""
    
    def __init__(self, bedrock_client: BedrockClient, knowledge_base: KnowledgeBase, cache: Dict[str, Any]):
        self.bedrock = bedrock_client
        self.kb = knowledge_base
        self.cache = cache
    
    async def classify_intent(self, problem_description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Classify optimization problem intent"""
        try:
            cache_key = hashlib.md5(f"intent:{problem_description}".encode()).hexdigest()
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            kb_ctx = self.kb.search(problem_description)
            
            prompt = f"""Classify this optimization problem.

PROBLEM: {problem_description}
SIMILAR: {kb_ctx}

JSON only:
{{
  "intent": "resource_allocation|production_planning|portfolio_optimization|scheduling",
  "industry": "manufacturing|finance|healthcare|retail|logistics|general",
  "optimization_type": "linear_programming|quadratic_programming|mixed_integer_linear_programming",
  "complexity": "low|medium|high",
  "confidence": 0.85
}}"""
            
            resp = await self.bedrock.invoke("anthropic.claude-3-haiku-20240307-v1:0", prompt, 1000)
            result = parse_json(resp)
            result.setdefault('intent', 'unknown')
            result.setdefault('optimization_type', 'linear_programming')
            result.setdefault('confidence', 0.7)
            
            response = {
                "status": "success",
                "step": "intent_classification",
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "message": f"Intent: {result['intent']}"
            }
            self.cache[cache_key] = response
            return response
            
        except Exception as e:
            logger.error(f"Intent error: {e}")
            return {"status": "error", "step": "intent_classification", "error": str(e)}


async def classify_intent_tool(problem_description: str, context: Optional[str] = None) -> Dict[str, Any]:
    """Tool wrapper for intent classification"""
    # This would be called from the main tools orchestrator
    # For now, return a placeholder
    return {"status": "error", "error": "Tool not initialized"}
