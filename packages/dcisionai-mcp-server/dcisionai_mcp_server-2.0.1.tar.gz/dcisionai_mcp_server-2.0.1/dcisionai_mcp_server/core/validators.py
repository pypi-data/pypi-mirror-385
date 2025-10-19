#!/usr/bin/env python3
"""
Validation engine for optimization results and expressions
"""

import ast
import logging
import operator
import re
from typing import Any, Dict

from ..models.model_spec import ModelSpec

logger = logging.getLogger(__name__)


class SafeEvaluator:
    """Safe expression evaluator using AST (no eval()!)"""
    
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
        """Safely evaluate mathematical expression"""
        for name, val in sorted(vars.items(), key=lambda x: -len(x[0])):
            expr = re.sub(r'\b' + re.escape(name) + r'\b', str(val), expr)
        try:
            node = ast.parse(expr, mode='eval')
            return cls._eval(node.body)
        except Exception as e:
            raise ValueError(f"Expression evaluation failed: {e}")
    
    @classmethod
    def _eval(cls, node):
        """Recursively evaluate AST nodes"""
        if isinstance(node, (ast.Constant, ast.Num)):
            return node.value if hasattr(node, 'value') else node.n
        elif isinstance(node, ast.BinOp):
            return cls.OPS[type(node.op)](cls._eval(node.left), cls._eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return cls.OPS[type(node.op)](cls._eval(node.operand))
        raise ValueError(f"Unsupported: {type(node)}")


class Validator:
    """Validation engine for optimization results"""
    
    def __init__(self):
        self.eval = SafeEvaluator()
    
    def validate(self, result: Dict, model: ModelSpec) -> Dict[str, Any]:
        """Validate optimization results against model"""
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
        """Check if constraint is satisfied"""
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
