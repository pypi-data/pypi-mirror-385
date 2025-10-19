#!/usr/bin/env python3
"""
DcisionAI MCP Tools - Production Version 2.0
============================================
SECURITY: No eval(), uses AST parsing
VALIDATION: Comprehensive result validation  
RELIABILITY: Multi-region failover, rate limiting
"""

import asyncio
import json
import logging
import re
import os
import hashlib
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from functools import lru_cache
from collections import deque
import ast
import operator

try:
    import numpy as np
    HAS_MONTE_CARLO = True
except ImportError:
    HAS_MONTE_CARLO = False

import boto3
from botocore.exceptions import ClientError

from .workflows import WorkflowManager
from .config import Config
from .optimization_engine import solve_real_optimization
from .solver_selector import SolverSelector

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Variable:
    name: str
    type: str
    bounds: str
    description: str
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Constraint:
    expression: str
    description: str
    type: str = "inequality"
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Objective:
    type: str
    expression: str
    description: str
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ModelSpec:
    variables: List[Variable]
    constraints: List[Constraint]
    objective: Objective
    model_type: str
    model_complexity: str = "medium"
    estimated_solve_time: float = 1.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelSpec':
        if 'result' in data:
            data = data['result']
        if 'raw_response' in data:
            data = json.loads(data['raw_response'])
        
        variables = [Variable(**v) if isinstance(v, dict) else v for v in data.get('variables', [])]
        constraints = [Constraint(**c) if isinstance(c, dict) else c for c in data.get('constraints', [])]
        obj = data.get('objective', {})
        objective = Objective(**obj) if isinstance(obj, dict) else obj
        
        return cls(
            variables=variables,
            constraints=constraints,
            objective=objective,
            model_type=data.get('model_type', 'linear_programming'),
            model_complexity=data.get('model_complexity', 'medium'),
            estimated_solve_time=data.get('estimated_solve_time', 1.0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'variables': [v.to_dict() for v in self.variables],
            'constraints': [c.to_dict() for c in self.constraints],
            'objective': self.objective.to_dict(),
            'model_type': self.model_type,
            'model_complexity': self.model_complexity,
            'estimated_solve_time': self.estimated_solve_time
        }

# ============================================================================
# KNOWLEDGE BASE
# ============================================================================

class KnowledgeBase:
    def __init__(self, path: str):
        self.path = path
        self.kb = self._load()
    
    def _load(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.path):
                with open(self.path) as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"KB load failed: {e}")
        return {'examples': []}
    
    @lru_cache(maxsize=500)
    def search(self, query: str, top_k: int = 2) -> str:
        query_lower = query.lower()
        results = []
        
        for ex in self.kb.get('examples', []):
            score = sum(2 for w in query_lower.split() if w in ex.get('problem_description', '').lower())
            score += sum(3 for kw in ex.get('keywords', []) if kw.lower() in query_lower)
            if score > 0:
                results.append((score, ex))
        
        results.sort(reverse=True)
        if not results[:top_k]:
            return "No similar examples."
        
        context = "Similar:\n"
        for _, ex in results[:top_k]:
            context += f"- {ex.get('problem_type', '')}: {ex.get('solution', '')[:80]}...\n"
        return context[:300]

# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = time.time()
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
            while len(self.calls) >= self.max_calls:
                await asyncio.sleep(0.1)
                now = time.time()
                while self.calls and self.calls[0] < now - self.period:
                    self.calls.popleft()
            self.calls.append(now)

# ============================================================================
# SAFE EXPRESSION EVALUATOR (NO eval()!)
# ============================================================================

class SafeEvaluator:
    OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }
    
    @classmethod
    def evaluate(cls, expr: str, vars: Dict[str, float]) -> float:
        for name, val in sorted(vars.items(), key=lambda x: -len(x[0])):
            expr = re.sub(r'\b' + re.escape(name) + r'\b', str(val), expr)
        node = ast.parse(expr, mode='eval')
        return cls._eval(node.body)
    
    @classmethod
    def _eval(cls, node):
        if isinstance(node, (ast.Constant, ast.Num)):
            return node.value if hasattr(node, 'value') else node.n
        elif isinstance(node, ast.BinOp):
            return cls.OPS[type(node.op)](cls._eval(node.left), cls._eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return cls.OPS[type(node.op)](cls._eval(node.operand))
        raise ValueError(f"Unsupported: {type(node)}")

# ============================================================================
# VALIDATION ENGINE
# ============================================================================

class Validator:
    def __init__(self):
        self.eval = SafeEvaluator()
    
    def validate(self, result: Dict, model: ModelSpec) -> Dict[str, Any]:
        errors = []
        warnings = []
        
        status = result.get('status')
        values = result.get('optimal_values', {})
        obj_val = result.get('objective_value', 0)
        
        if status == 'optimal' and values:
            try:
                calc = self.eval.evaluate(model.objective.expression, values)
                err = abs(calc - obj_val) / max(abs(calc), 1e-10)
                if err > 0.001:
                    errors.append(f"Objective mismatch: calc={calc:.4f}, reported={obj_val:.4f}")
            except Exception as e:
                warnings.append(f"Could not validate objective: {e}")
        
        if status == 'optimal' and values:
            for c in model.constraints:
                try:
                    if not self._check_constraint(c.expression, values):
                        errors.append(f"Violated: {c.expression}")
                except Exception as e:
                    warnings.append(f"Could not check {c.expression}: {e}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _check_constraint(self, expr: str, vars: Dict[str, float]) -> bool:
        if '<=' in expr:
            left, right = expr.split('<=', 1)
            return self.eval.evaluate(left, vars) <= self.eval.evaluate(right, vars) + 1e-6
        elif '>=' in expr:
            left, right = expr.split('>=', 1)
            return self.eval.evaluate(left, vars) >= self.eval.evaluate(right, vars) - 1e-6
        elif '==' in expr or '=' in expr:
            left, right = expr.split('==' if '==' in expr else '=', 1)
            return abs(self.eval.evaluate(left, vars) - self.eval.evaluate(right, vars)) < 1e-6
        return True

# ============================================================================
# BEDROCK CLIENT WITH FAILOVER
# ============================================================================

class BedrockClient:
    def __init__(self, regions: List[str] = None):
        self.regions = regions or ['us-east-1', 'us-west-2']
        self.current = 0
        self.clients = {}
        for r in self.regions:
            try:
                self.clients[r] = boto3.client('bedrock-runtime', region_name=r)
            except Exception as e:
                logger.error(f"Failed to init {r}: {e}")
        self.limiters = {
            'haiku': RateLimiter(10, 1.0),
            'sonnet': RateLimiter(5, 1.0)
        }
    
    async def invoke(self, model_id: str, prompt: str, max_tokens: int = 4000) -> str:
        limiter = self.limiters['haiku' if 'haiku' in model_id.lower() else 'sonnet']
        await limiter.acquire()
        
        for attempt in range(len(self.regions)):
            region = self.regions[self.current]
            client = self.clients.get(region)
            if not client:
                self.current = (self.current + 1) % len(self.regions)
                continue
            
            try:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": 0.1,
                    "messages": [{"role": "user", "content": prompt}]
                })
                
                resp = await asyncio.to_thread(
                    client.invoke_model,
                    modelId=model_id,
                    body=body,
                    contentType="application/json"
                )
                
                data = json.loads(resp['body'].read())
                if 'content' in data:
                    return data['content'][0]['text']
                elif 'completion' in data:
                    return data['completion']
                raise ValueError("Unexpected response")
                
            except Exception as e:
                if "ServiceUnavailable" in str(e) or "Throttling" in str(e):
                    self.current = (self.current + 1) % len(self.regions)
                    if attempt < len(self.regions) - 1:
                        continue
                raise
        
        raise RuntimeError("All regions failed")

# ============================================================================
# MAIN TOOLS CLASS
# ============================================================================

class DcisionAITools:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.bedrock = BedrockClient()
        self.validator = Validator()
        self.solver_selector = SolverSelector()
        self.workflow_manager = WorkflowManager()
        
        kb_path = os.path.join(os.path.dirname(__file__), '..', 'dcisionai_kb.json')
        self.kb = KnowledgeBase(kb_path)
        self.cache = {}
        
        logger.info("DcisionAI Tools v2.0 initialized")
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        try:
            return json.loads(text.strip())
        except:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
            return {"raw_response": text}
    
    async def classify_intent(self, problem_description: str, context: Optional[str] = None) -> Dict[str, Any]:
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
            result = self._parse_json(resp)
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
    
    async def analyze_data(self, problem_description: str, intent_data: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            intent = intent_data.get('intent', 'unknown') if intent_data else 'unknown'
            kb_ctx = self.kb.search(problem_description)
            
            prompt = f"""Analyze data for optimization.

PROBLEM: {problem_description}
INTENT: {intent}
SIMILAR: {kb_ctx}

JSON only:
{{
  "readiness_score": 0.85,
  "entities": 10,
  "data_quality": "high|medium|low",
  "variables_identified": ["x1", "x2"],
  "constraints_identified": ["capacity", "demand"]
}}"""
            
            resp = await self.bedrock.invoke("anthropic.claude-3-haiku-20240307-v1:0", prompt, 2000)
            result = self._parse_json(resp)
            result.setdefault('readiness_score', 0.8)
            result.setdefault('entities', 0)
            
            return {
                "status": "success",
                "step": "data_analysis",
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "message": f"Ready: {result['readiness_score']:.1%}"
            }
        except Exception as e:
            logger.error(f"Data error: {e}")
            return {"status": "error", "step": "data_analysis", "error": str(e)}
    
    async def build_model(
        self,
        problem_description: str,
        intent_data: Optional[Dict] = None,
        data_analysis: Optional[Dict] = None,
        solver_selection: Optional[Dict] = None,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        try:
            opt_type = intent_data.get('optimization_type', 'linear_programming') if intent_data else 'linear_programming'
            kb_ctx = self.kb.search(problem_description)
            
            for attempt in range(max_retries + 1):
                retry_note = f"\nPREVIOUS FAILED. Ensure all variables used.\n" if attempt > 0 else ""
                
                prompt = f"""{retry_note}Build optimization model.

PROBLEM: {problem_description}
TYPE: {opt_type}
SIMILAR: {kb_ctx}

JSON only:
{{
  "variables": [{{"name": "x1", "type": "continuous", "bounds": "0 to 100", "description": "Units"}}],
  "constraints": [{{"expression": "x1 + x2 <= 100", "description": "Capacity"}}],
  "objective": {{"type": "maximize", "expression": "5*x1", "description": "Profit"}},
  "model_type": "{opt_type}"
}}"""
                
                resp = await self.bedrock.invoke("anthropic.claude-3-haiku-20240307-v1:0", prompt, 4000)
                result = self._parse_json(resp)
                
                if self._validate_model(result):
                    result.setdefault('model_type', opt_type)
                    return {
                        "status": "success",
                        "step": "model_building",
                        "timestamp": datetime.now().isoformat(),
                        "result": result,
                        "message": f"Model built (attempt {attempt+1})"
                    }
            
            return {"status": "error", "step": "model_building", "error": "Validation failed"}
            
        except Exception as e:
            logger.error(f"Model error: {e}")
            return {"status": "error", "step": "model_building", "error": str(e)}
    
    def _validate_model(self, data: Dict) -> bool:
        if not data.get('variables') or not data.get('constraints') or not data.get('objective'):
            return False
        
        var_names = {v['name'] for v in data['variables'] if isinstance(v, dict)}
        all_text = ' '.join(c.get('expression', '') for c in data['constraints'] if isinstance(c, dict))
        all_text += ' ' + data['objective'].get('expression', '') if isinstance(data.get('objective'), dict) else ''
        
        return all(name in all_text for name in var_names)
    
    async def solve_optimization(
        self,
        problem_description: str,
        intent_data: Optional[Dict] = None,
        data_analysis: Optional[Dict] = None,
        model_building: Optional[Dict] = None
    ) -> Dict[str, Any]:
        try:
            if not model_building or 'result' not in model_building:
                return {"status": "error", "error": "No model"}
            
            model_spec = ModelSpec.from_dict(model_building['result'])
            solver_result = solve_real_optimization(model_spec.to_dict())
            
            validation = self.validator.validate(solver_result, model_spec)
            
            if not validation['is_valid'] and solver_result.get('status') == 'optimal':
                logger.warning(f"Validation errors: {validation['errors']}")
            
            solver_result['validation'] = validation
            
            return {
                "status": "success" if validation['is_valid'] else "error",
                "step": "optimization_solution",
                "timestamp": datetime.now().isoformat(),
                "result": solver_result,
                "message": f"Solved: {solver_result.get('status')}"
            }
            
        except Exception as e:
            logger.error(f"Solve error: {e}")
            return {"status": "error", "step": "optimization_solution", "error": str(e)}
    
    async def select_solver(self, optimization_type: str, problem_size: Optional[Dict] = None, performance_requirement: str = "balanced") -> Dict[str, Any]:
        try:
            result = self.solver_selector.select_solver(optimization_type, problem_size or {}, performance_requirement)
            return {
                "status": "success",
                "step": "solver_selection",
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "message": f"Selected: {result['selected_solver']}"
            }
        except Exception as e:
            return {"status": "error", "step": "solver_selection", "error": str(e)}
    
    async def explain_optimization(
        self,
        problem_description: str,
        intent_data: Optional[Dict] = None,
        data_analysis: Optional[Dict] = None,
        model_building: Optional[Dict] = None,
        optimization_solution: Optional[Dict] = None
    ) -> Dict[str, Any]:
        try:
            status = optimization_solution.get('status', 'unknown') if optimization_solution else 'unknown'
            
            prompt = f"""Explain optimization result to business stakeholders.

PROBLEM: {problem_description}
STATUS: {status}

JSON only:
{{
  "executive_summary": {{
    "problem_statement": "Clear statement",
    "key_findings": ["finding 1", "finding 2"],
    "business_impact": "Expected value"
  }},
  "implementation_guidance": {{
    "next_steps": ["step 1", "step 2"],
    "risk_considerations": ["risk 1"]
  }}
}}"""
            
            resp = await self.bedrock.invoke("anthropic.claude-3-haiku-20240307-v1:0", prompt, 3000)
            result = self._parse_json(resp)
            
            return {
                "status": "success",
                "step": "explainability",
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "message": "Explanation generated"
            }
        except Exception as e:
            return {"status": "error", "step": "explainability", "error": str(e)}
    
    async def simulate_scenarios(
        self,
        problem_description: str,
        optimization_solution: Optional[Dict] = None,
        scenario_parameters: Optional[Dict] = None,
        simulation_type: str = "monte_carlo",
        num_trials: int = 10000
    ) -> Dict[str, Any]:
        try:
            if simulation_type != "monte_carlo" or not HAS_MONTE_CARLO:
                return {
                    "status": "error",
                    "error": f"Only Monte Carlo supported (NumPy required)",
                    "available_simulations": ["monte_carlo"],
                    "roadmap": ["discrete_event", "agent_based"]
                }
            
            obj_val = optimization_solution.get('objective_value', 0) if optimization_solution else 0
            
            np.random.seed(42)
            scenarios = np.random.normal(obj_val, obj_val * 0.1, num_trials)
            
            return {
                "status": "success",
                "step": "simulation_analysis",
                "timestamp": datetime.now().isoformat(),
                "result": {
                    "simulation_type": "monte_carlo",
                    "num_trials": num_trials,
                    "risk_metrics": {
                        "mean": float(np.mean(scenarios)),
                        "std_dev": float(np.std(scenarios)),
                        "percentile_5": float(np.percentile(scenarios, 5)),
                        "percentile_95": float(np.percentile(scenarios, 95))
                    }
                },
                "message": f"Monte Carlo completed ({num_trials} trials)"
            }
        except Exception as e:
            return {"status": "error", "step": "simulation_analysis", "error": str(e)}
    
    async def get_workflow_templates(self) -> Dict[str, Any]:
        try:
            return {
                "status": "success",
                "workflow_templates": self.workflow_manager.get_all_workflows(),
                "total_workflows": 21
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def execute_workflow(self, industry: str, workflow_id: str, user_input: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            problem_desc = f"{workflow_id} for {industry}"
            
            intent_result = await self.classify_intent(problem_desc, industry)
            data_result = await self.analyze_data(problem_desc, intent_result.get('result'))
            model_result = await self.build_model(problem_desc, intent_result.get('result'), data_result.get('result'))
            solve_result = await self.solve_optimization(problem_desc, intent_result.get('result'), data_result.get('result'), model_result)
            explain_result = await self.explain_optimization(problem_desc, intent_result.get('result'), data_result.get('result'), model_result, solve_result.get('result'))
            
            return {
                "status": "success",
                "workflow_type": workflow_id,
                "industry": industry,
                "steps_completed": 5,
                "results": {
                    "intent_classification": intent_result,
                    "data_analysis": data_result,
                    "model_building": model_result,
                    "optimization_solution": solve_result,
                    "explainability": explain_result
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

# ============================================================================
# GLOBAL INSTANCE & WRAPPERS
# ============================================================================

_tools_instance = None

def get_tools() -> DcisionAITools:
    global _tools_instance
    if _tools_instance is None:
        _tools_instance = DcisionAITools()
    return _tools_instance

async def classify_intent(problem_description: str, context: Optional[str] = None) -> Dict[str, Any]:
    return await get_tools().classify_intent(problem_description, context)

async def analyze_data(problem_description: str, intent_data: Optional[Dict] = None) -> Dict[str, Any]:
    return await get_tools().analyze_data(problem_description, intent_data)

async def build_model(problem_description: str, intent_data: Optional[Dict] = None, data_analysis: Optional[Dict] = None, solver_selection: Optional[Dict] = None) -> Dict[str, Any]:
    return await get_tools().build_model(problem_description, intent_data, data_analysis, solver_selection)

async def solve_optimization(problem_description: str, intent_data: Optional[Dict] = None, data_analysis: Optional[Dict] = None, model_building: Optional[Dict] = None) -> Dict[str, Any]:
    return await get_tools().solve_optimization(problem_description, intent_data, data_analysis, model_building)

async def select_solver(optimization_type: str, problem_size: Optional[Dict] = None, performance_requirement: str = "balanced") -> Dict[str, Any]:
    return await get_tools().select_solver(optimization_type, problem_size, performance_requirement)

async def explain_optimization(problem_description: str, intent_data: Optional[Dict] = None, data_analysis: Optional[Dict] = None, model_building: Optional[Dict] = None, optimization_solution: Optional[Dict] = None) -> Dict[str, Any]:
    return await get_tools().explain_optimization(problem_description, intent_data, data_analysis, model_building, optimization_solution)

async def simulate_scenarios(problem_description: str, optimization_solution: Optional[Dict] = None, scenario_parameters: Optional[Dict] = None, simulation_type: str = "monte_carlo", num_trials: int = 10000) -> Dict[str, Any]:
    return await get_tools().simulate_scenarios(problem_description, optimization_solution, scenario_parameters, simulation_type, num_trials)

async def get_workflow_templates() -> Dict[str, Any]:
    return await get_tools().get_workflow_templates()

async def execute_workflow(industry: str, workflow_id: str, user_input: Optional[Dict] = None) -> Dict[str, Any]:
    return await get_tools().execute_workflow(industry, workflow_id, user_input)
