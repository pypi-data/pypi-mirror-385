#!/usr/bin/env python3
"""
Data models for optimization problems
"""

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class Variable:
    """Optimization variable definition"""
    name: str
    type: str
    bounds: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Constraint:
    """Optimization constraint definition"""
    expression: str
    description: str
    type: str = "inequality"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Objective:
    """Optimization objective definition"""
    type: str
    expression: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ModelSpec:
    """Complete optimization model specification"""
    variables: List[Variable]
    constraints: List[Constraint]
    objective: Objective
    model_type: str
    model_complexity: str = "medium"
    estimated_solve_time: float = 1.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelSpec':
        """Create ModelSpec from dictionary"""
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
        """Convert ModelSpec to dictionary"""
        return {
            'variables': [v.to_dict() for v in self.variables],
            'constraints': [c.to_dict() for c in self.constraints],
            'objective': self.objective.to_dict(),
            'model_type': self.model_type,
            'model_complexity': self.model_complexity,
            'estimated_solve_time': self.estimated_solve_time
        }
