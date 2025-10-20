#!/usr/bin/env python3
"""
Knowledge Base for DcisionAI optimization examples and guidance
"""

import json
import logging
import os
from functools import lru_cache
from typing import Any, Dict

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Knowledge base for optimization examples and guidance"""
    
    def __init__(self, path: str):
        self.path = path
        self.kb = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load knowledge base from file"""
        try:
            if os.path.exists(self.path):
                with open(self.path) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"KB load failed: {e}")
        return {'examples': []}
    
    @lru_cache(maxsize=500)
    def search(self, query: str, top_k: int = 2) -> str:
        """Search knowledge base for similar examples"""
        query_lower = query.lower()
        results = []
        
        for ex in self.kb.get('examples', []):
            score = sum(2 for w in query_lower.split() if w in ex.get('problem_description', '').lower())
            score += sum(3 for kw in ex.get('keywords', []) if kw.lower() in query_lower)
            if score > 0:
                results.append((score, ex))
        
        results.sort(key=lambda x: x[0], reverse=True)
        if not results[:top_k]:
            return "No similar examples."
        
        context = "Similar:\n"
        for _, ex in results[:top_k]:
            context += f"- {ex.get('problem_type', '')}: {ex.get('solution', '')[:80]}...\n"
        return context[:300]
    
    def get_problem_type_guidance(self, problem_description: str) -> str:
        """Get specific guidance based on problem type"""
        query_lower = problem_description.lower()
        
        if 'portfolio' in query_lower or 'investment' in query_lower or 'asset' in query_lower:
            return """
**Portfolio Optimization Guidance:**
- Decision variables represent investment allocations or asset weights
- Constraints include budget limits, risk limits, and diversification requirements
- Objective balances return maximization with risk minimization
- Consider correlation matrices, expected returns, and risk measures
- If individual stocks are mentioned, create individual stock variables
- If sector constraints exist, create sector-level constraints
"""
        elif 'production' in query_lower or 'factory' in query_lower or 'manufacturing' in query_lower:
            return """
**Production Planning Guidance:**
- Decision variables typically represent production quantities or resource allocation
- Constraints often include capacity limits, demand requirements, and resource availability
- Objective is usually cost minimization or profit maximization
- Consider time periods, production lines, and inventory constraints
"""
        elif 'schedule' in query_lower or 'task' in query_lower or 'employee' in query_lower:
            return """
**Scheduling Optimization Guidance:**
- Decision variables represent task assignments, start times, or resource allocations
- Constraints include precedence relationships, resource capacity, and deadlines
- Objective is usually makespan minimization or cost optimization
- Consider task dependencies, resource constraints, and time windows
"""
        else:
            return """
**Generic Optimization Guidance:**
- Identify the key decisions to be made (decision variables)
- Determine the limitations and requirements (constraints)
- Define the optimization goal (objective function)
- Ensure all variables are used and constraints are mathematically sound
"""
